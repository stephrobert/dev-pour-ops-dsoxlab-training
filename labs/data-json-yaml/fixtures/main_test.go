package main

import (
	"reflect"
	"testing"
)

func TestJSONAndYAMLNormalizeIdentically(t *testing.T) {
	fromJSON, err := readInventory("inventory.json")
	if err != nil {
		t.Fatal(err)
	}
	fromYAML, err := readInventory("inventory.yaml")
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(fromJSON, fromYAML) {
		t.Fatalf("JSON and YAML differ:\nJSON: %#v\nYAML: %#v", fromJSON, fromYAML)
	}
	if got := fromJSON.Services[0].ID; got != "api" {
		t.Fatalf("services are not normalized and sorted; first id = %q", got)
	}
}

func TestInvalidInventoryIsRejected(t *testing.T) {
	if _, err := readInventory("invalid.yaml"); err == nil {
		t.Fatal("invalid inventory unexpectedly passed")
	}
	if _, err := readInventory("unsupported.toml"); err == nil {
		t.Fatal("unsupported file format unexpectedly passed")
	}
}
