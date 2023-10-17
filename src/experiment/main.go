package main

import (
	"encoding/csv"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/kube-sched-testing/src/experiment/parser"
)

const (
	outputPath = "./jobs"
)

var (
	dataFileHeaders = []string{"id", "arrival_time", "ddl", "execution_time", "priority"}
)

var (
	count        *int
	templateFile *string
	dataFile     *string
)

func validateFlags() {
	if strings.Trim(*templateFile, " ") == "" {
		log.Fatal("template YAML file is required, use flag -t to pass it as arg")
	}
	if strings.Trim(*dataFile, " ") == "" {
		log.Fatal("data CSV file is required, use flag -d to pass it as arg")
	}

}
func main() {
	count = flag.Int("n", 0, "number of times the experiment should run")
	templateFile = flag.String("t", "", "template file for the deployment")
	dataFile = flag.String("d", "", "data file for the template")
	flag.Parse()
	validateFlags()
	dFile, err := os.Open(*dataFile)
	if err != nil {
		log.Fatalf("failed to open data file: %s", err)
	}
	defer dFile.Close()
	reader := csv.NewReader(dFile)
	rows, err := reader.ReadAll()
	if err != nil {
		log.Fatalf("failed to read data file: %s", err)
	}

	if _, err := os.Stat(outputPath); errors.Is(err, os.ErrNotExist) {
		err := os.Mkdir(outputPath, os.ModePerm)
		if err != nil {
			log.Fatalf("directory %s does not exist, attempt to create failed: %s", outputPath, err)
		}
	}

	var arrivalTimes []int
	var outputFiles []string
	for i, row := range rows {
		if i == 0 {
			// skip header
			continue
		}
		arrivalT, err := strconv.Atoi(row[1])
		if err != nil {
			log.Fatalf("failed to parse arrival time of job %d: %s", i, err)
		}
		arrivalTimes = append(arrivalTimes, arrivalT)
		data := parser.Data{
			ID:            row[0],
			DDL:           row[2],
			ExecutionTime: row[3],
			Priority:      row[4],
		}
		outputFile := filepath.Join(outputPath, fmt.Sprintf("job-%s.yaml", data.ID))
		outputFiles = append(outputFiles, outputFile)
		if err := parser.ParseYAML(*templateFile, data, outputFile); err != nil {
			log.Fatalf("failed to parse yaml for job %d: %s", i, err)
		}
	}

	// TODO: deploy jobs based on arrival time
	// TODO: use count to run experiment multiple times
}
