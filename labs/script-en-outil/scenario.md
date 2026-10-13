# A project with a contract

## Situation

The Bash script `certcheck.sh` still checks certificates on an old server:
it always exits 0, reports a missing certificate as "0 days", and has
neither help nor machine-readable output. The team wrote what it expects
from its replacement in `CONTRAT.md`, and laid out the skeleton of the
Python project that must replace it.

The skeleton is structured the way a developer would do it: the
`src/certcheck/` package, split into two modules (`certificats.py` reads the
inventory and decides the status, `cli.py` handles the interface), a
`pyproject.toml` that declares the `certcheck` command in
`[project.scripts]`, a `uv.lock`, and the `bin/certcheck` launcher, which
runs it through `uv run`. Part of the code is written; the other functions
are there, with their docstring and examples, but raise
`NotImplementedError`.

## Goal

`bin/certcheck` honours the contract: help and version, usage errors as
code 2, codes 0, 1 and 2 depending on the certificates, a JSON output, a
threshold set through `CERTCHECK_DAYS`, and errors on standard error. The
Bash script stays as the former implementation, to read, not to call.

## Hints

- `uv run certcheck --help` runs the command the project declares, in its
  environment; `bin/certcheck` does the same from any directory.
- As long as a function raises `NotImplementedError`, the command prints a
  Python traceback: its last line tells which function to write.
- `CERTCHECK_NOW=YYYY-MM-DD` sets today's date: without it, no alert can be
  tested with fixed-date certificates.
- `print(..., file=sys.stderr)` writes to standard error; standard output
  carries only the result.
