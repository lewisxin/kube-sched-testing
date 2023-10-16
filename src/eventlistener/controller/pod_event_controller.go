package controller

import (
	"fmt"
	"strings"
	"time"

	"github.com/kube-sched-testing/src/eventlistener/csvwriter"
	"github.com/kube-sched-testing/src/eventlistener/podevent"
	v1 "k8s.io/api/core/v1"
	"k8s.io/client-go/informers"
	coreinformers "k8s.io/client-go/informers/core/v1"
	"k8s.io/client-go/tools/cache"
	"k8s.io/klog/v2"
)

const (
	AnnotationKeyDDL    = AnnotationKeyPrefix + "ddl"
	AnnotationKeyPrefix = "rt-preemptive.scheduling.x-k8s.io/"
	NamespaceLocalPath  = "local-path-storage"
	NamespaceSystem     = "kube-system"
	TimeFormat          = "2006-01-02 15:04:05.000000"
)

// PodLoggingController logs the name and namespace of pods that are added,
// deleted, or updated
type PodLoggingController struct {
	informerFactory informers.SharedInformerFactory
	podInformer     coreinformers.PodInformer
	csvWriter       csvwriter.Writer
	podEvents       map[string]*podevent.Event
}

// NewPodLoggingController creates a PodLoggingController
func NewPodLoggingController(informerFactory informers.SharedInformerFactory, filename string) (*PodLoggingController, error) {
	podInformer := informerFactory.Core().V1().Pods()

	c := &PodLoggingController{
		informerFactory: informerFactory,
		podInformer:     podInformer,
		csvWriter:       csvwriter.NewPodEventCSVWriter(filename),
		podEvents:       make(map[string]*podevent.Event),
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

func (c *PodLoggingController) Stop() {
	c.csvWriter.Close()
}

// trimPodName removes the unique idenfitier attached to a pod name
func trimPodName(str string) string {
	lastDash := strings.LastIndex(str, "-")
	if lastDash != -1 {
		return str[:lastDash]
	}
	return str
}

func (c *PodLoggingController) writePodEvent(podName string, newEvent podevent.Event) {
	podName = trimPodName(podName)
	event, ok := c.podEvents[podName]
	if !ok || event == nil {
		event = &podevent.Event{
			Start:    newEvent.Start,
			End:      newEvent.End,
			NodeName: newEvent.NodeName,
			Deadline: newEvent.Deadline,
			Created:  newEvent.Created,
		}
	}
	switch newEvent.EventType {
	case podevent.TypeCreated:
		event.Created = newEvent.Created
	case podevent.TypeRunning:
		event.Start = newEvent.Start
		if !event.Created.IsZero() {
			c.csvWriter.Append([]string{podName, event.Created.Format(TimeFormat), event.Start.Format(TimeFormat), "In Queue", event.NodeName})
			var t time.Time
			event.Created = t
		}
	case podevent.TypeResumed:
		event.Start = newEvent.Start
	case podevent.TypePaused, podevent.TypeFinished:
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
	case podevent.TypeFailed:
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
		c.writePodEvent(pod.Name, podevent.Event{EventType: podevent.TypeRunning, Start: time.Now()})
		klog.Infof("POD RUNNING: %s/%s", pod.Namespace, pod.Name)
	} else {
		c.writePodEvent(pod.Name, podevent.Event{EventType: podevent.TypeCreated, Deadline: getPodDDL(pod), Created: pod.CreationTimestamp.Time})
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
		c.writePodEvent(newPod.Name, podevent.Event{EventType: podevent.TypeRunning, Start: time.Now()})
		klog.Infof("POD RUNNING: %s/%s", newPod.Namespace, newPod.Name)
	case oldPhase == v1.PodRunning && newPhase == phasePause:
		c.writePodEvent(newPod.Name, podevent.Event{EventType: podevent.TypePaused, End: time.Now()})
		klog.Infof("POD PAUSED: %s/%s", newPod.Namespace, newPod.Name)
	case oldPhase == phasePause && newPhase == v1.PodRunning:
		c.writePodEvent(newPod.Name, podevent.Event{EventType: podevent.TypeResumed, Start: time.Now()})
		klog.Infof("POD RESUMED: %s/%s", newPod.Namespace, newPod.Name)
	case (oldPhase == v1.PodRunning || oldPhase == phasePause) && newPhase == v1.PodSucceeded:
		c.writePodEvent(newPod.Name, podevent.Event{EventType: podevent.TypeFinished, End: time.Now(), NodeName: newPod.Spec.NodeName})
		klog.Infof("POD FINISHED: %s/%s", newPod.Namespace, newPod.Name)
	case (oldPhase == v1.PodRunning || oldPhase == phasePause || oldPhase == v1.PodPending) && newPhase == v1.PodFailed:
		c.writePodEvent(newPod.Name, podevent.Event{EventType: podevent.TypeFailed, End: time.Now(), NodeName: newPod.Spec.NodeName})
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
