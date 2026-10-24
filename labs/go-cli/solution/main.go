package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/url"
	"os"
	"strconv"
	"strings"
)

type Config struct {
	Endpoint       string `json:"endpoint"`
	TimeoutSeconds int    `json:"timeout_seconds"`
}

func loadConfig(path string, lookup func(string) (string, bool)) (Config, error) {
	config := Config{Endpoint: "http://127.0.0.1:8080", TimeoutSeconds: 10}
	file, err := os.Open(path)
	if err == nil {
		defer file.Close()
		decoder := json.NewDecoder(file)
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&config); err != nil {
			return Config{}, fmt.Errorf("read config %s: %w", path, err)
		}
		if err := decoder.Decode(new(any)); !errors.Is(err, io.EOF) {
			return Config{}, fmt.Errorf("read config %s: expected one JSON document", path)
		}
	} else if !errors.Is(err, os.ErrNotExist) {
		return Config{}, fmt.Errorf("read config %s: %w", path, err)
	}

	if endpoint, ok := lookup("FLEETCTL_ENDPOINT"); ok {
		config.Endpoint = endpoint
	}
	if timeout, ok := lookup("FLEETCTL_TIMEOUT_SECONDS"); ok {
		config.TimeoutSeconds, err = strconv.Atoi(timeout)
		if err != nil {
			return Config{}, fmt.Errorf("FLEETCTL_TIMEOUT_SECONDS must be an integer")
		}
	}
	if err := validateConfig(config); err != nil {
		return Config{}, err
	}
	return config, nil
}

func validateConfig(config Config) error {
	parsed, err := url.Parse(config.Endpoint)
	if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.Hostname() == "" {
		return fmt.Errorf("endpoint must be an HTTP(S) URL with a host")
	}
	if config.TimeoutSeconds < 1 || config.TimeoutSeconds > 120 {
		return fmt.Errorf("timeout_seconds must be between 1 and 120")
	}
	return nil
}

func usage(output io.Writer) {
	fmt.Fprintln(output, "Usage: fleetctl <command>")
	fmt.Fprintln(output, "Commands:")
	fmt.Fprintln(output, "  help                 Show this help")
	fmt.Fprintln(output, "  version              Show version")
	fmt.Fprintln(output, "  config show [flags]  Display effective configuration")
}

func run(args []string, stdout, stderr io.Writer, lookup func(string) (string, bool)) int {
	if len(args) == 0 || args[0] == "help" || args[0] == "--help" || args[0] == "-h" {
		usage(stdout)
		return 0
	}
	switch args[0] {
	case "version":
		fmt.Fprintln(stdout, "fleetctl dev")
		return 0
	case "config":
		if len(args) < 2 || args[1] != "show" {
			fmt.Fprintln(stderr, "usage: fleetctl config show [--config FILE]")
			return 2
		}
		flags := flag.NewFlagSet("config show", flag.ContinueOnError)
		flags.SetOutput(stderr)
		path := flags.String("config", "fleetctl.json", "path to JSON configuration")
		flags.Usage = func() {
			fmt.Fprintln(stderr, "Usage: fleetctl config show [--config FILE]")
			flags.PrintDefaults()
		}
		if err := flags.Parse(args[2:]); err != nil {
			if errors.Is(err, flag.ErrHelp) {
				return 0
			}
			return 2
		}
		if flags.NArg() != 0 {
			fmt.Fprintf(stderr, "unexpected arguments: %s\n", strings.Join(flags.Args(), " "))
			return 2
		}
		config, err := loadConfig(*path, lookup)
		if err != nil {
			fmt.Fprintf(stderr, "fleetctl: %v\n", err)
			return 2
		}
		var output bytes.Buffer
		encoder := json.NewEncoder(&output)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(config); err != nil {
			fmt.Fprintf(stderr, "fleetctl: encode config: %v\n", err)
			return 2
		}
		if _, err := stdout.Write(output.Bytes()); err != nil {
			fmt.Fprintf(stderr, "fleetctl: write output: %v\n", err)
			return 2
		}
		return 0
	default:
		fmt.Fprintf(stderr, "fleetctl: unknown command %q\n", args[0])
		usage(stderr)
		return 2
	}
}

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr, os.LookupEnv))
}
