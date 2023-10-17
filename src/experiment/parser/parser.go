package parser

import (
	"fmt"
	"os"
	"path"
	"text/template"
)

type Data struct {
	DDL           string
	ExecutionTime string
	ID            string
	Priority      string
}

func ParseYAML(templateFile string, data Data, outputFile string) error {
	template, err := template.New(path.Base(templateFile)).Delims("<%", "%>").ParseFiles(templateFile)
	if err != nil {
		return fmt.Errorf("failed to create template from file: %w", err)
	}
	out, err := os.Create(outputFile)
	if err != nil {
		return fmt.Errorf("error create output file: %w", err)
	}
	defer out.Close()
	if err := template.Execute(out, data); err != nil {
		return fmt.Errorf("failed to parse template: %w", err)
	}
	return nil
}
