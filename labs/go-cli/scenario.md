# Give `fleetctl` a reliable command-line interface

Implement the starter Go module as a small operations CLI. It must be useful
for local inspection and must not require a live API.

The module requires Go 1.27.3 or newer.

## Contract

- `fleetctl help` (and no arguments) prints usage and exits 0.
- `fleetctl version` prints `fleetctl dev` and exits 0.
- `fleetctl config show [--config FILE]` reads JSON with `endpoint` and
  `timeout_seconds`, applies environment overrides, and prints canonical
  indented JSON.
- Configuration precedence is defaults (`http://127.0.0.1:8080`, 10
  seconds), file, then `FLEETCTL_ENDPOINT` and `FLEETCTL_TIMEOUT_SECONDS`.
- The endpoint must be an HTTP(S) URL with a host. The timeout must be an
  integer from 1 through 120. Unknown JSON properties, malformed JSON,
  invalid values, and unknown commands produce a readable stderr message
  and non-zero exit status.
- `go test ./...` passes and `go build -o fleetctl .` produces a working
  executable.

## Steps

1. Read `main_test.go`; run `go test ./...` to see the unfinished behavior.
2. Implement config loading, validation, and precedence.
3. Implement `help`, `version`, and `config show`, including flag errors.
4. Test file and environment combinations, then build and run the binary.
5. Run `dsoxlab check go-cli`.
