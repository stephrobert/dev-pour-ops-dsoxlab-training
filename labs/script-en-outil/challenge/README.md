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

## Understand certcheck, then modify it

5 tasks, 100 points, 20 minutes.

The `challenge/work` directory holds the certcheck Python project and its
contract, `CONTRAT.md`. Tasks 1 to 3 go into `reponses.yaml` and are about the
project **as you received it**; tasks 4 and 5 are done in
`src/certcheck/cli.py`.

### Task 1: the command is declared by the project (20 pts)

`fichier_declaration` names the file that declares the `certcheck` command,
and `commande_declaree` copies what it declares, in the `module:function`
form.

### Task 2: where things are (20 pts)

`module_decision` gives the file that holds the `statut` function, and
`lanceur` the file cron or a pipeline runs, paths from the working directory.

### Task 3: the observed exit codes (20 pts)

The three codes in `reponses.yaml` are those observed when running the given
commands on the project you received.

### Task 4: the threshold comes from the environment (20 pts)

`CERTCHECK_DAYS` sets the threshold when `--days` is absent, `--days` wins
over the variable, and a value that is not a positive integer returns 2, with
a message on standard error.

### Task 5: errors go to standard error (20 pts)

A missing inventory returns 2, with a one-line message on standard error, no
Python traceback and nothing on standard output. A missing certificate stays
in the JSON as `error`, and its host is named on standard error.

To get graded: `dsoxlab check script-en-outil`.
