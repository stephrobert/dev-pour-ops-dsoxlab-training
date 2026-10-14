# The pull request with green tests

## Situation

certcheck runs every night from the operations server's cron. Malik proposes
**pull request #42**: purging old reports, which filled the disk, and
posting alerts to the team chat's webhook. He added a test, the suite
passes, and he asks you for a review before merging.

The working directory holds the project as it is on `main` (the
`src/certcheck/` package, `pyproject.toml`, `tests/`), the PR description
(`pr/DESCRIPTION.md`) and its diff (`pr/0042.diff`).

## Why review

Green tests only prove what they test. A review looks for what no test
sees: a leaking secret, a deletion that may hit the wrong folder, an error
that is silenced. It is only useful if the author can act: a file, a line,
the problem, a fix.

## Steps

### 1. Read the description, then the code

Read `pr/DESCRIPTION.md`, then apply the diff in a copy to see the files as
they would be merged:

```bash
cp -r . /tmp/pr42 && cd /tmp/pr42 && git apply pr/0042.diff
grep -n "" src/certcheck/maintenance.py | less
```

Check every claim of the description in the code: "it is handled" is proved
or disproved line by line.

### 2. Look for the four defects

The PR carries four, one per category of the list written in `revue.yaml`:
a swallowed error, a printed secret, a dangerous path, a missing test.
Three are enough to succeed. For every environment variable read, ask what
the code does when it is missing.

### 3. Write the review

In `revue.yaml` (the real one, in the working directory), one comment per
defect: `fichier`, `ligne` (read AFTER `git apply`), `categorie`,
`commentaire` and `proposition`. Then the `verdict`.

### 4. Hand the mechanical part to ruff

A linter tirelessly sees what a review should not have to look for. Add a
ruff configuration to the project, for instance in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120
```

Run `uv run ruff check .`: it reports defects in the base code. Read each
line (rule code, file, line), then `uv run ruff check --fix .` fixes those
marked `[*]`. Run again: `All checks passed!`.

**Formatting** is settled the same way, with no debate: `uv run ruff format
--check .` lists the files whose layout departs from the configuration, and
`uv run ruff format .` rewrites them. Check again: nothing left to reformat.

### 5. Check

`dsoxlab check relire-une-automatisation`.
