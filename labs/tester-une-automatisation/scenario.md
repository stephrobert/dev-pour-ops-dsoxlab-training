# A suite that catches the real bugs

## Situation

certcheck runs every night. It decides whether the check turns red, and it
opens a ticket on the forge when certificates must be renewed. Three people
will edit it this quarter. Its only test is an example checking that a
certificate valid until 2045 is `ok`.

The working directory is a small uv project: `certcheck.py`, its launcher
`bin/certcheck`, the contract `CONTRAT.md`, four fixed-date certificates, and
`tests/test_certcheck.py`. pytest is declared in the `dev` group of
`pyproject.toml`, at an exact version locked by `uv.lock`.

## Goal

A suite of **at least six tests**, green on the correct tool, that fails on
each of the four mutants prepared by the team. Each mutant carries a defect a
developer really introduces when editing this kind of tool: a shifted
boundary, a swallowed error, a wrong exit code, a dry run that is not one.

## Hints

- **The clock is injected.** The certificates have fixed dates: a test that
  depends on the day it runs passes today and breaks in six months. Pass the
  date to the functions (`analyser(entries, threshold, date(2031, 2, 20))`)
  or set it through `CERTCHECK_NOW` when you run `bin/certcheck`.
- **Two levels.** The decision functions (`statut`, `code_de_sortie`,
  `analyser`) are tested by calling them; the exit code and the dry run are
  tested by running `bin/certcheck` with `subprocess.run`.
- **The network is doubled.** A test never talks to a real forge. A test
  double, a small local HTTP server (`http.server`) or `monkeypatch` on
  `certcheck.requete`, records what the tool sends. To prove that
  `--dry-run` sends nothing, you need a configured, reachable forge: without
  it, "nothing was sent" proves nothing.
- `tmp_path` gives each test a clean folder, to write an inventory or a fake
  certificate.

## Proof

`dsoxlab check tester-une-automatisation` copies your project, replaces
`certcheck.py` with the reference and then with each mutant, and runs
`uv run pytest`. Your own `certcheck.py` is never modified.
