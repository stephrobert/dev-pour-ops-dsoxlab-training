package main

import (
	"errors"
	"fmt"
	"io"
)

type Config struct {
	Endpoint       string `json:"endpoint"`
	TimeoutSeconds int    `json:"timeout_seconds"`
}

func loadConfig(string, func(string) (string, bool)) (Config, error) {
	return Config{}, errors.New("TODO: load and validate configuration")
}

func run([]string, io.Writer, io.Writer, func(string) (string, bool)) int {
	fmt.Fprintln(io.Discard, "not implemented")
	return 2
}

func main() {
	fmt.Println("fleetctl: TODO")
}
