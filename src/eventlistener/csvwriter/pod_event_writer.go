package csvwriter

import (
	"encoding/csv"
	"fmt"
	"os"
)

var (
	csvHeaders = []string{"ID", "Job", "Start", "End", "Deadline", "Status", "Node"}
)

type podEventCSVWriter struct {
	file   *os.File
	writer *csv.Writer
}

func NewPodEventCSVWriter(filename string) Writer {
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
