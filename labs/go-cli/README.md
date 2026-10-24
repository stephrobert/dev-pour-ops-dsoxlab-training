# Build a small, predictable Go CLI

The platform team needs a local `fleetctl` command that can show its
deployment endpoint and timeout without requiring a service to be online.
Implement the command structure, predictable configuration precedence, and
tests before producing a standalone binary.

| | |
|---|---|
| Target | your machine: Go 1.27.3 or newer |
| Duration | about 60 minutes |
| Network | not needed by the lab; Go may download its declared toolchain if absent |
| Companion lesson | [Go programming](https://www.stephane-robert.info/docs/developper/programmation/golang/) (in French) |

```bash
dsoxlab run go-cli
cd labs/go-cli/challenge/work
go test ./...
go run . help
go run . config show --config fleetctl.json
go build -o fleetctl .
dsoxlab check go-cli
```

Configuration precedence is defaults, then the JSON file, then environment
variables. The grader checks actual command output, exit codes, invalid
configuration, tests, and the built executable.
