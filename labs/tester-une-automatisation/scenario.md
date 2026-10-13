# Your first tests

## Situation

certcheck runs every night. It decides whether the check turns red, and
three people will edit it this quarter. Today, nothing proves that an edit
does not break a rule of the contract: it has no tests.

The working directory is certcheck's Python package: its code in
`src/certcheck/` (the decision lives in `certificats.py`), its launcher
`bin/certcheck`, the contract `CONTRAT.md`, four fixed-date certificates, and
`tests/test_certcheck.py`, still empty. pytest is declared in the `dev`
group of `pyproject.toml`: `uv run pytest` installs it on first run.

## Why test

A test is a small function that calls the code with a known input and
checks the result with `assert`. It does not prove that the code works
today: it lets you **see at once** when an edit changes a behaviour. This
lab's check verifies that concretely: it runs your suite on two versions of
certcheck that each carry a bug, and the suite must catch them.

## Steps

### 1. A first test

Run `uv run pytest -v`: pytest answers "no tests ran". Add at the end of
`tests/test_certcheck.py`:

```python
def test_un_certificat_lointain_est_ok():
    resultats = certificats.analyser([("web-01", CERTS / "web-01.pem")], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "ok"
```

Run again: `1 passed`. Today's date is an **argument**: the test gives the
same verdict in 2026 and in 2040. A test that depends on the day it runs
always ends up breaking.

### 2. The threshold boundary

The contract says the threshold is **inclusive**: a certificate expiring in
exactly 30 days, with a threshold of 30, is `warning`. Bugs hide at the
edges. Write a test that checks `certificats.statut(30, 30)`, plus a case on
each side (`statut(31, 30)`, `statut(-1, 30)`).

### 3. The exit code

`certificats.code_de_sortie(resultats)` returns 0, 1 or 2 depending on the
statuses (see `CONTRAT.md`). Check that a list holding a single warning,
`[{"status": "warning"}]`, does return 1. Test one status at a time: a test
that only looks at `expired` misses a slip on `warning`.

### 4. A temporary file or a fixed date

Add a `tmp_path` parameter to a test: pytest gives it an empty folder, owned
by that test, and deletes it afterwards. Write a fake certificate in it and
check that it is `error`:

```python
def test_un_certificat_illisible_est_en_erreur(tmp_path):
    faux = tmp_path / "faux.pem"
    faux.write_text("ceci n'est pas un certificat\n")
    resultats = certificats.analyser([("faux", faux)], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "error"
```

To test the whole tool, run `bin/certcheck` with `subprocess.run` and set
the date with the `CERTCHECK_NOW` variable (example in the hints).

### 5. Check

`uv run pytest -v` must be green, then `dsoxlab check
tester-une-automatisation`.

## Proof

`dsoxlab check tester-une-automatisation` copies your project, replaces
the module `src/certcheck/certificats.py` with the reference and then with
each buggy version, and runs `uv run pytest`. Your own code is never
modified.
