# The certificate certcheck cannot read

## Situation

`TICKET.md`: certcheck exits with an error (code 2) on vpn-01 while openssl
reads its certificate fine. The daily check is red every day, and nobody
looks at the real alerts any more. Nothing in the logs, even with
`--verbose`.

The working directory is certcheck's Python package: its code in
`src/certcheck/` (date reading lives in `certificats.py`), its launcher
`bin/certcheck`, the contract, four certificates and a test suite
that passes. A green suite only proves what it tests.

## Why a method

Fixing by trial and error means changing a line, rerunning, starting over,
without ever knowing what really changed. The method fits in three moves:
**reproduce** the symptom at will, **look** at the program at the moment it
goes wrong, **fix** and keep the test that proves it.

## Steps

### 1. See the symptom

```bash
CERTCHECK_NOW=2026-10-13 bin/certcheck; echo "code: $?"
openssl x509 -enddate -noout -in certs/vpn-01.pem
```

vpn-01 is `error`, while openssl prints its expiry date.

### 2. Reproduce with a test, BEFORE fixing

Add to `tests/test_certcheck.py` a test that asks for vpn-01's date:

```python
def test_un_jour_a_un_chiffre_se_lit():
    assert certificats.date_expiration(CERTS / "vpn-01.pem") == date(2031, 3, 5)
```

`uv run pytest -k chiffre -v`: it **fails**, which is what we want. It will
prove the fix, and it will stop the bug from coming back.

### 3. Look at the faulty value

Read the traceback pytest prints: it names the line that raises the
exception. To see the value at the moment of the error, two ways:

- a temporary `print(repr(brut))` just before the split, in
  `date_expiration` (`src/certcheck/certificats.py`), then rerun the test;
- the debugger: a `breakpoint()` line at the same place, then
  `CERTCHECK_NOW=2026-10-13 bin/certcheck`. The program stops in pdb, once
  per certificate: `p brut` prints a variable, `c` continues to the next
  certificate (vpn-01 is the third), `n` runs the next line. To finish,
  `c` until the end: `q` raises an exception that the code's
  `except Exception` swallows, and the program carries on.

Compare with another certificate: `openssl x509 -enddate -noout -in
certs/vpn-01.pem | cat -A` makes spaces visible.

### 4. Fix

Two changes, in `src/certcheck/certificats.py`:

- splitting the date must no longer break on a single-digit day;
- the `except Exception` in `analyser` swallows the error silently: catch
  only the expected errors (`OSError`, `ValueError`) and write a message
  naming the host with `log.error(...)`, so that the next truly unreadable
  certificate leaves a trace.

Remove the temporary `print` or `breakpoint()`. `uv run pytest -v` must be
green, the reproduction test included.

### 5. Write DEBUG.md

At the root of the project, three sections, a few lines each (the titles
stay in French, the check reads them):

```markdown
## Ce que j'ai vu
## La cause
## La correction
```

## Proof

`dsoxlab check deboguer` runs your suite on the original version (it must
fail) and on the reference (it must pass), runs `bin/certcheck` on randomly
drawn fleets, checks the rest of the contract, and reads `DEBUG.md`.
