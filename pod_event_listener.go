package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	v1 "k8s.io/api/core/v1"
	"k8s.io/client-go/informers"
	coreinformers "k8s.io/client-go/informers/core/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
	"k8s.io/component-base/logs"
	"k8s.io/klog/v2"
	//
	// Uncomment to load all auth plugins
	// _ "k8s.io/client-go/plugin/pkg/client/auth"
	//
	// Or uncomment to load specific auth plugins
	// _ "k8s.io/client-go/plugin/pkg/client/auth/azure"
	// _ "k8s.io/client-go/plugin/pkg/client/auth/gcp"
	// _ "k8s.io/client-go/plugin/pkg/client/auth/oidc"
)

const (
	NamespaceSystem     = "kube-system"
	NamespaceLocalPath  = "local-path-storage"
	CSVFileName         = "pod_events_%s.csv"
	TimeFormat          = "2006-01-02 15:04:05.000000"
	AnnotationKeyPrefix = "rt-preemptive.scheduling.x-k8s.io/"
	AnnotationKeyDDL    = AnnotationKeyPrefix + "ddl"
)

var (
	csvHeaders = []string{"Job", "Start", "End", "Status", "Node"}
)

type CSVWriter interface {
	Open(filename string) error
	Append(line []string)
	Close()
}

type podEventCSVWriter struct {
	file   *os.File
	writer *csv.Writer
}

func NewPodEventCSVWriter(filename string) CSVWriter {
	csvWriter := &podEventCSVWriter{}
	csvWriter.Open(filename)
	return csvWriter
}

func (w *podEventCSVWriter) Open(filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}
	writer := csv.NewWriter(file)
	writer.Write(csvHeaders)
	defer writer.Flush()
	w.file = file
	w.writer = writer
	return nil
}

func (w *podEventCSVWriter) Append(line []string) {
	w.writer.Write(line)
	defer w.writer.Flush()
}

func (w *podEventCSVWriter) Close() {
	w.writer.Flush()
	w.file.Close()
	w.file = nil
}

type PodEvent struct {
	EventType EventType
	Start     time.Time
	End       time.Time
	NodeName  string
	Deadline  time.Time
	Created   time.Time
}

type EventType int

const (
	EventTypeCreated EventType = iota
	EventTypeRunning
	EventTypePaused
	EventTypeResumed
	EventTypeFinished
	EventTypeFailed
)

// PodLoggingController logs the name and namespace of pods that are added,
// deleted, or updated
type PodLoggingController struct {
	informerFactory informers.SharedInformerFactory
	podInformer     coreinformers.PodInformer
	csvWriter       CSVWriter
	podEvents       map[string]*PodEvent
}

// NewPodLoggingController creates a PodLoggingController
func NewPodLoggingController(informerFactory informers.SharedInformerFactory, plugin string) (*PodLoggingController, error) {
	podInformer := informerFactory.Core().V1().Pods()

	c := &PodLoggingController{
		informerFactory: informerFactory,
		podInformer:     podInformer,
		csvWriter:       NewPodEventCSVWriter(fmt.Sprintf(CSVFileName, plugin)),
		podEvents:       make(map[string]*PodEvent),
	}
	_, err := podInformer.Informer().AddEventHandler(
		// Your custom resource event handlers.
		cache.ResourceEventHandlerFuncs{
			// Called on creation
			AddFunc: c.podAdd,
			// Called on resource update and every resyncPeriod on existing resources.
			UpdateFunc: c.podUpdate,
			// Called on resource deletion.
			DeleteFunc: c.podDelete,
		},
	)
	if err != nil {
		return nil, err
	}

	return c, nil
}

// Run starts shared informers and waits for the shared informer cache to
// synchronize.
func (c *PodLoggingController) Run(stopCh chan struct{}) error {
	// Starts all the shared informers that have been created by the factory so
	// far.
	c.informerFactory.Start(stopCh)
	// wait for the initial synchronization of the local cache.
	if !cache.WaitForCacheSync(stopCh, c.podInformer.Informer().HasSynced) {
		return fmt.Errorf("failed to sync")
	}
	return nil
}

// trimPodName removes the unique idenfitier attached to a pod name
func trimPodName(str string) string {
	lastDash := strings.LastIndex(str, "-")
	if lastDash != -1 {
		return str[:lastDash]
	}
	return str
}

func (c *PodLoggingController) writePodEvent(podName string, newEvent PodEvent) {
	podName = trimPodName(podName)
	event, ok := c.podEvents[podName]
	if !ok || event == nil {
		event = &PodEvent{
			Start:    newEvent.Start,
			End:      newEvent.End,
			NodeName: newEvent.NodeName,
			Deadline: newEvent.Deadline,
			Created:  newEvent.Created,
		}
	}
	switch newEvent.EventType {
	case EventTypeCreated:
		event.Created = newEvent.Created
	case EventTypeRunning:
		event.Start = newEvent.Start
		if !event.Created.IsZero() {
			c.csvWriter.Append([]string{podName, event.Created.Format(TimeFormat), event.Start.Format(TimeFormat), "In Queue", event.NodeName})
			var t time.Time
			event.Created = t
		}
	case EventTypeResumed:
		event.Start = newEvent.Start
	case EventTypePaused, EventTypeFinished:
		event.End = newEvent.End
		// write event to csv and reset start and end
		if event.End.Before(event.Deadline) {
			c.csvWriter.Append([]string{podName, event.Start.Format(TimeFormat), event.End.Format(TimeFormat), "Running", event.NodeName})
		} else if event.Start.Before(event.Deadline) {
			c.csvWriter.Append([]string{podName, event.Start.Format(TimeFormat), event.Deadline.Format(TimeFormat), "Running"})
			c.csvWriter.Append([]string{podName, event.Deadline.Format(TimeFormat), event.End.Format(TimeFormat), "Overdue", event.NodeName})
		} else {
			c.csvWriter.Append([]string{podName, event.Start.Format(TimeFormat), event.End.Format(TimeFormat), "Overdue", event.NodeName})
		}
	case EventTypeFailed:
		event.End = newEvent.End
		if !event.Created.IsZero() {
			c.csvWriter.Append([]string{podName, event.Created.Format(TimeFormat), event.End.Format(TimeFormat), "In Queue", event.NodeName})
			var t time.Time
			event.Created = t
		}
	}
	c.podEvents[podName] = event
}

func (c *PodLoggingController) podAdd(obj interface{}) {
	pod := obj.(*v1.Pod)
	if pod.Namespace == NamespaceSystem || pod.Namespace == NamespaceLocalPath {
		return
	}
	if pod.Status.Phase == v1.PodRunning {
		c.writePodEvent(pod.Name, PodEvent{EventType: EventTypeRunning, Start: time.Now()})
		klog.Infof("POD RUNNING: %s/%s", pod.Namespace, pod.Name)
	} else {
		c.writePodEvent(pod.Name, PodEvent{EventType: EventTypeCreated, Deadline: getPodDDL(pod), Created: pod.CreationTimestamp.Time})
		klog.Infof("POD CREATED: %s/%s", pod.Namespace, pod.Name)
	}
}

func getPodDDL(pod *v1.Pod) time.Time {
	ddlRel, _ := time.ParseDuration(pod.Annotations[AnnotationKeyDDL])
	return pod.CreationTimestamp.Add(ddlRel)
}

func (c *PodLoggingController) podUpdate(old, new interface{}) {
	oldPod := old.(*v1.Pod)
	newPod := new.(*v1.Pod)
	if newPod.Namespace == NamespaceSystem || newPod.Namespace == NamespaceLocalPath {
		return
	}
	oldPhase := oldPod.Status.Phase
	newPhase := newPod.Status.Phase
	phasePause := v1.PodPhase("Paused")
	switch {
	case oldPhase == v1.PodPending && newPhase == v1.PodRunning:
		c.writePodEvent(newPod.Name, PodEvent{EventType: EventTypeRunning, Start: time.Now()})
		klog.Infof("POD RUNNING: %s/%s", newPod.Namespace, newPod.Name)
	case oldPhase == v1.PodRunning && newPhase == phasePause:
		c.writePodEvent(newPod.Name, PodEvent{EventType: EventTypePaused, End: time.Now()})
		klog.Infof("POD PAUSED: %s/%s", newPod.Namespace, newPod.Name)
	case oldPhase == phasePause && newPhase == v1.PodRunning:
		c.writePodEvent(newPod.Name, PodEvent{EventType: EventTypeResumed, Start: time.Now()})
		klog.Infof("POD RESUMED: %s/%s", newPod.Namespace, newPod.Name)
	case (oldPhase == v1.PodRunning || oldPhase == phasePause) && newPhase == v1.PodSucceeded:
		c.writePodEvent(newPod.Name, PodEvent{EventType: EventTypeFinished, End: time.Now(), NodeName: newPod.Spec.NodeName})
		klog.Infof("POD FINISHED: %s/%s", newPod.Namespace, newPod.Name)
	case (oldPhase == v1.PodRunning || oldPhase == phasePause || oldPhase == v1.PodPending) && newPhase == v1.PodFailed:
		c.writePodEvent(newPod.Name, PodEvent{EventType: EventTypeFailed, End: time.Now(), NodeName: newPod.Spec.NodeName})
		klog.Infof("POD FAILED: %s/%s", newPod.Namespace, newPod.Name)
	}
}

func (c *PodLoggingController) podDelete(obj interface{}) {
	pod := obj.(*v1.Pod)
	if pod.Namespace == NamespaceSystem {
		return
	}
	klog.Infof("POD DELETED: %s/%s", pod.Namespace, pod.Name)
}

func main() {
	var plugin *string
	var kubeconfig *string
	if home := homedir.HomeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "(optional) absolute path to the kubeconfig file")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to the kubeconfig file")
	}
	plugin = flag.String("plugin", "", "name of the scheduler plugin")
	flag.Parse()
	logs.InitLogs()
	defer logs.FlushLogs()

	// use the current context in kubeconfig
	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
	if err != nil {
		panic(err.Error())
	}

	// create the clientset
	cs, err := kubernetes.NewForConfig(config)
	if err != nil {
		klog.Fatal(err)
	}

	factory := informers.NewSharedInformerFactory(cs, time.Hour*24)
	controller, err := NewPodLoggingController(factory, strings.ToLower(*plugin))
	if err != nil {
		klog.Fatal(err)
	}

	stop := make(chan struct{})
	defer close(stop)
	err = controller.Run(stop)
	if err != nil {
		klog.Fatal(err)
	}
	defer controller.csvWriter.Close()
	select {}

}
