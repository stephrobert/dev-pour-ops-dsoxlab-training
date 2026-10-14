# A red test

## Situation

certcheck runs every night and decides whether the check turns red.
Yesterday, someone touched the decision; this morning, the test suite is red.
Nobody looked at it.

The working directory is the certcheck Python project: its code in
`src/certcheck/` (the decision is in `certificats.py`), its `bin/certcheck`
launcher, the contract `CONTRAT.md`, a few certificates with fixed dates, and
`tests/test_certcheck.py`, which holds four tests. pytest is declared in the
`dev` group of `pyproject.toml`: `uv run pytest` installs it on first run.

## Why test

A test is a small function that calls the code with a known input and checks
the result with `assert`. It lets you **see at once** when a change alters a
behaviour: that is exactly what just happened.

## Steps

### 1. Run the suite and read the failure

```bash
uv run pytest -v
```

Three tests pass, one fails. Write the name of the red test (the `FAILED`
line) in `reponses.yaml`, then read the line starting with `E`: `assert X ==
Y` puts side by side what the code returned (X) and what the test expected
(Y).

### 2. Fix the code, not the test

The test describes the contract (`CONTRAT.md`, "Décision" section); the code
is what drifted. Open `src/certcheck/certificats.py`, find the function the
test calls, fix the condition, then run `uv run pytest -v` again until all
four tests are green.

### 3. Check by running the tool

```bash
CERTCHECK_NOW=2026-06-01 bin/certcheck; echo "code: $?"
```

### 4. Add a test

The four tests do not check that a **lone warning** gives exit code 1. Copy
`test_un_certificat_expire_est_signale`, rename the copy (its name must start
with `test_`) and replace its body with:

```python
assert certificats.code_de_sortie([{"status": "warning"}]) == 1
```

Run again: five green tests. The check will run your suite on a version of
certcheck where a lone warning exits with 0: your new test must make it fail.
