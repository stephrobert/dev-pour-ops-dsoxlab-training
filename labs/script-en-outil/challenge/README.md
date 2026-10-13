# Challenge: certcheck honours its contract

5 tasks, 100 points, 30 minutes.

Your tool is the project's Python package `src/certcheck/`, called
through `bin/certcheck`, and only through it. The contract is in
`CONTRAT.md` (in French).

### Task 1: a Python project and a predictable interface (20 pts)

`pyproject.toml` declares the `certcheck` command in `[project.scripts]`,
pointing to a function of the `src/certcheck/` package, and `bin/certcheck`
runs that package: `uv run certcheck --version` and
`bin/certcheck --version` give the same answer. `--help` exits 0 and names
every option; `--version` prints `certcheck X.Y.Z`; an unknown option,
`--days abc` or `--format xml` exit 2 with a message on standard error and
nothing on standard output.

### Task 2: actionable exit codes (20 pts)

0, 1 or 2 depending on the certificates, on random inventories; a missing
certificate or a missing inventory return 2.

### Task 3: a usable JSON output (20 pts)

`--format json` returns a single document, with correct `days_left`,
`status` and `not_after` for every host, inclusive threshold;
`--format text` carries the host and its status on each line.

### Task 4: the threshold comes from the environment (20 pts)

`CERTCHECK_DAYS` sets the threshold, `--days` wins over the variable, an
invalid value returns 2, and the inventory accepts tabs and comments, run
from another directory.

### Task 5: errors go to standard error (20 pts)

A missing certificate appears in the JSON as `error`, and its host is named
on standard error, without polluting the document; a missing inventory
returns 2, with a one-line message on standard error, no Python traceback
and nothing on standard output.
