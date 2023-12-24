package main

import (
	"encoding/csv"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/kube-sched-testing/src/experiment/parser"
	"k8s.io/component-base/logs"
	"k8s.io/klog/v2"
)

const (
	outputPath = "./jobs"
)

var (
	dataFile *string
)

func validateFlags() {
	if strings.Trim(*dataFile, " ") == "" {
		klog.Fatal("data CSV file is required, use flag -d to pass it as arg")
		klog.Fatal("create a CSV file with the headers: id,arrival_time,execution_time,ddl,priority")
	}
}

func getTemplateFile(templateName string) string {
	fileName := ""
	switch templateName {
	case "transcoding":
		fileName = "transcode-video-tmpl"
	case "hyperparam":
		fileName = "hyperparam-tuning"
	case "countdown":
		fileName = "countdown-ddl-tmpl"
	}
	return fmt.Sprintf("templates/%s.yaml", fileName)
}
func main() {
	dataFile = flag.String("d", "", "data file for the template")
	flag.Parse()
	validateFlags()
	logs.InitLogs()
	defer logs.FlushLogs()
	dFile, err := os.Open(*dataFile)
	if err != nil {
		klog.Fatalf("failed to open data file: %s", err)
	}
	defer dFile.Close()
	reader := csv.NewReader(dFile)
	rows, err := reader.ReadAll()
	if err != nil {
		klog.Fatalf("failed to read data file: %s", err)
	}

	if _, err := os.Stat(outputPath); errors.Is(err, os.ErrNotExist) {
		err := os.Mkdir(outputPath, os.ModePerm)
		if err != nil {
			klog.Fatalf("directory %s does not exist, attempt to create failed: %s", outputPath, err)
		}
	}

	var wg sync.WaitGroup
	for i, row := range rows {
		if i == 0 {
			// skip header
			continue
		}
		arrivalT, err := strconv.Atoi(row[1])
		if err != nil {
			wg.Done()
			klog.Fatalf("failed to parse arrival time of job %d: %s", i, err)
		}
		data := parser.Data{
			ID:            row[0],
			ExecutionTime: row[2],
			DDL:           row[3],
			CPU:           row[4],
			Meta1:         row[6],
			Meta2:         row[7],
			Meta3:         row[8],
		}
		templateFile := getTemplateFile(row[5])
		outputFile := filepath.Join(outputPath, fmt.Sprintf("job-%s.yaml", data.ID))
		if err := parser.ParseYAML(templateFile, data, outputFile); err != nil {
			wg.Done()
			klog.Fatalf("failed to parse yaml for job %d: %s", i, err)
		}
		wg.Add(1)
		go func() {
			time.Sleep(time.Duration(arrivalT) * time.Second)
			klog.Infof("deploying job %s", outputFile)
			deployJob(outputFile)
			wg.Done()
		}()
	}
	wg.Wait()
}

func deployJob(jobFile string) {
	cmd := exec.Command("kubectl", "apply", "-f", jobFile)
	stdout, err := cmd.Output()

	if err != nil {
		klog.Error(err)
		return
	}

	// Print the output
	klog.Info(string(stdout))
}
