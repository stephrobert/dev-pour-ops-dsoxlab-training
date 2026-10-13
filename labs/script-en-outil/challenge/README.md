# Challenge: certcheck honours its contract

5 tasks, 100 points, 60 minutes.

Your tool is called through `bin/certcheck`, and only through it. The
contract is in `CONTRAT.md`.

### Task 1: a predictable interface (20 pts)

`--help` exits 0 and names every option; `--version` prints
`certcheck X.Y.Z`; an unknown option, `--days abc` or `--format xml` exit 2
with a message on standard error and nothing on standard output.

### Task 2: actionable exit codes (20 pts)

0, 1 or 2 depending on the certificates, on random inventories; a missing
certificate or a missing inventory return 2.

### Task 3: a usable JSON output (20 pts)

`--format json` returns a single document, with correct `days_left`,
`status` and `not_after` for every host, inclusive threshold;
`--format text` carries the host and its status on each line.

### Task 4: configuration through the environment (20 pts)

`CERTCHECK_INVENTORY` and `CERTCHECK_DAYS` are read, the option wins over the
variable, an invalid value returns 2, and the inventory accepts tabs and
comments.

### Task 5: a dry run that sends nothing (20 pts)

`--publish --dry-run` sends no request and shows the ticket on standard
error; `--publish` without `FORGE_TOKEN` returns 2 and sends nothing.
