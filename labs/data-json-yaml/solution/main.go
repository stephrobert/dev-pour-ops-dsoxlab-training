package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"gopkg.in/yaml.v3"
)

type Service struct {
	ID          string `json:"id" yaml:"id"`
	Environment string `json:"environment" yaml:"environment"`
	Replicas    int    `json:"replicas" yaml:"replicas"`
	Expires     string `json:"expires" yaml:"expires"`
}

type Inventory struct {
	Services []Service `json:"services" yaml:"services"`
}

func readInventory(path string) (Inventory, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return Inventory{}, fmt.Errorf("read %s: %w", path, err)
	}
	var inventory Inventory
	switch strings.ToLower(filepath.Ext(path)) {
	case ".json":
		decoder := json.NewDecoder(bytes.NewReader(data))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&inventory); err != nil {
			return Inventory{}, fmt.Errorf("parse JSON: %w", err)
		}
		var extra any
		if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
			return Inventory{}, fmt.Errorf("parse JSON: expected one document")
		}
	case ".yaml", ".yml":
		decoder := yaml.NewDecoder(bytes.NewReader(data))
		decoder.KnownFields(true)
		if err := decoder.Decode(&inventory); err != nil {
			return Inventory{}, fmt.Errorf("parse YAML: %w", err)
		}
		var extra any
		if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
			return Inventory{}, fmt.Errorf("parse YAML: expected one document")
		}
	default:
		return Inventory{}, fmt.Errorf("unsupported input format: %s", filepath.Ext(path))
	}
	if inventory.Services == nil {
		return Inventory{}, fmt.Errorf("services must be a list")
	}
	for index := range inventory.Services {
		service := &inventory.Services[index]
		service.ID = strings.ToLower(strings.TrimSpace(service.ID))
		service.Environment = strings.ToLower(strings.TrimSpace(service.Environment))
		if service.ID == "" {
			return Inventory{}, fmt.Errorf("services[%d].id must be a non-empty string", index)
		}
		if service.Environment == "" {
			return Inventory{}, fmt.Errorf("services[%d].environment must be a non-empty string", index)
		}
		if service.Replicas < 1 {
			return Inventory{}, fmt.Errorf("services[%d].replicas must be a positive integer", index)
		}
		expires, err := time.Parse("2006-01-02", strings.TrimSpace(service.Expires))
		if err != nil {
			return Inventory{}, fmt.Errorf("services[%d].expires must be an ISO date", index)
		}
		service.Expires = expires.Format("2006-01-02")
	}
	sort.Slice(inventory.Services, func(i, j int) bool {
		return inventory.Services[i].ID < inventory.Services[j].ID
	})
	return inventory, nil
}

func writeOutput(data []byte, path string, stdout io.Writer) error {
	if path == "" {
		_, err := stdout.Write(data)
		return err
	}
	if err := os.WriteFile(path, data, 0o644); err != nil {
		return fmt.Errorf("write %s: %w", path, err)
	}
	return nil
}

func run(args []string, stdout, stderr io.Writer) int {
	flags := flag.NewFlagSet("fleet-data", flag.ContinueOnError)
	flags.SetOutput(stderr)
	output := flags.String("output", "", "write JSON to this file instead of stdout")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	if flags.NArg() != 1 {
		fmt.Fprintln(stderr, "usage: fleet-data [--output PATH] INPUT")
		return 2
	}
	inventory, err := readInventory(flags.Arg(0))
	if err != nil {
		fmt.Fprintf(stderr, "fleet-data: %v\n", err)
		return 2
	}
	data, err := json.MarshalIndent(inventory.Services, "", "  ")
	if err != nil {
		fmt.Fprintf(stderr, "fleet-data: encode JSON: %v\n", err)
		return 2
	}
	data = append(data, '\n')
	if err := writeOutput(data, *output, stdout); err != nil {
		fmt.Fprintf(stderr, "fleet-data: %v\n", err)
		return 2
	}
	return 0
}

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}
