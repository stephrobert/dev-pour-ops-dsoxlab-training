# A tool with a contract

## Situation

The small script from the previous lab has become a **Python project**: a
colleague split it the way a developer does. The `src/certcheck/` package
holds two modules (`certificats.py` reads the inventory and decides the
status, `cli.py` handles the interface), `pyproject.toml` declares the
`certcheck` command, `uv.lock` pins the environment, and the `bin/certcheck`
launcher runs it all through `uv run`. The team wrote what the tool must do
in `CONTRAT.md`.

Two tickets are open: the tool ignores the `CERTCHECK_DAYS` variable the
contract promises, and when the inventory is missing, its error message goes
to standard output, where a program expects the result.

## Goal

First **find your way** around the project and write it down in
`reponses.yaml`: which file declares the command, what it declares, where the
decision lives, which file cron runs, and which exit codes the tool returns.
Then **close the two gaps** with the contract, without rewriting anything
else.

## Hints

- `uv run certcheck --help` and `bin/certcheck --help` run the same thing:
  the command `pyproject.toml` declares in `[project.scripts]`.
- `CERTCHECK_NOW=2026-06-01 bin/certcheck; echo $?` replays the check on a
  fixed date and prints its exit code; `CONTRAT.md` says what it means.
- The threshold is decided in a single function of `cli.py`, and
  `os.environ.get` reads an environment variable.
- `print(..., file=sys.stderr)` writes on standard error; standard output
  only carries the result.
