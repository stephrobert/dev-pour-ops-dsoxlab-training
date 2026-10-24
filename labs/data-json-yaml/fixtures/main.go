package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

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
		return Inventory{}, err
	}
	var inventory Inventory
	switch strings.ToLower(filepath.Ext(path)) {
	case ".json":
		err = json.Unmarshal(data, &inventory)
	case ".yaml", ".yml":
		err = yaml.Unmarshal(data, &inventory)
	default:
		return Inventory{}, errors.New("cannot decode input")
	}
	return inventory, err
}

func run(args []string, stdout, stderr io.Writer) int {
	flags := flag.NewFlagSet("fleet-data", flag.ContinueOnError)
	flags.SetOutput(stderr)
	output := flags.String("output", "", "write JSON to this file")
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
		fmt.Fprintf(stderr, "fleet-data: %v\n", err)
		return 2
	}
	data = append(data, '\n')
	if *output != "" {
		err = os.WriteFile(*output, data, 0o644)
	} else {
		_, err = stdout.Write(data)
	}
	if err != nil {
		fmt.Fprintf(stderr, "fleet-data: %v\n", err)
		return 2
	}
	return 0
}

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}
