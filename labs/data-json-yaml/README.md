# Normalize JSON and YAML service inventories

An operations team receives the same service inventory as JSON from one tool
and YAML from another. Build a converter that produces one stable JSON
representation, regardless of the input format.

| | |
|---|---|
| Target | your machine: Go 1.27.3 or newer |
| Duration | about 45 minutes |
| Network | needed once to download the pinned Go YAML module |
| Companion lesson | [Go programming](https://www.stephane-robert.info/docs/developper/programmation/golang/) (in French) |

```bash
dsoxlab run data-json-yaml
cd labs/data-json-yaml/challenge/work
go test ./...
go run . inventory.yaml
go run . --output normalized.json inventory.json
go build -o fleet-data .
dsoxlab check data-json-yaml
```

The Go output is sorted by service name and uses ISO dates. An invalid input
must return a non-zero status, explain the problem, and leave an existing
output file untouched.
