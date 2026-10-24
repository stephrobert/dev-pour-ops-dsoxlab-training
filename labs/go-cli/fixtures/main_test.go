package main

import (
	"bytes"
	"strings"
	"testing"
)

func environment(values map[string]string) func(string) (string, bool) {
	return func(key string) (string, bool) {
		value, ok := values[key]
		return value, ok
	}
}

func TestHelpAndVersion(t *testing.T) {
	for _, test := range []struct {
		args []string
		want string
	}{
		{[]string{"help"}, "Usage:"},
		{[]string{"version"}, "fleetctl dev"},
	} {
		var stdout, stderr bytes.Buffer
		if code := run(test.args, &stdout, &stderr, environment(nil)); code != 0 {
			t.Fatalf("run(%v) = %d, stderr %q", test.args, code, stderr.String())
		}
		if !strings.Contains(stdout.String(), test.want) {
			t.Errorf("run(%v) output %q does not contain %q", test.args, stdout.String(), test.want)
		}
	}
}

func TestConfigShowHelp(t *testing.T) {
	var stdout, stderr bytes.Buffer
	if code := run([]string{"config", "show", "--help"}, &stdout, &stderr, environment(nil)); code != 0 {
		t.Fatalf("help returned %d, stderr %q", code, stderr.String())
	}
	if !strings.Contains(stderr.String(), "Usage: fleetctl config show") {
		t.Fatalf("subcommand help missing from stderr: %q", stderr.String())
	}
}

func TestConfigUsesEnvironmentOverride(t *testing.T) {
	config, err := loadConfig("fleetctl.json", environment(map[string]string{
		"FLEETCTL_ENDPOINT": "https://override.example.invalid",
	}))
	if err != nil {
		t.Fatal(err)
	}
	if config.Endpoint != "https://override.example.invalid" || config.TimeoutSeconds != 25 {
		t.Fatalf("unexpected config: %+v", config)
	}
}

func TestUnknownCommandFails(t *testing.T) {
	var stdout, stderr bytes.Buffer
	if code := run([]string{"deploy"}, &stdout, &stderr, environment(nil)); code == 0 {
		t.Fatal("unknown command unexpectedly succeeded")
	}
	if stderr.Len() == 0 {
		t.Fatal("unknown command did not explain the error")
	}
}
