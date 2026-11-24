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

`tests/test_certcheck.py` already holds, commented out at the end, a test that asks for vpn-01's date. Uncomment it:

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
  `c` until the end. With Python 3.14, `q` asks for confirmation then
  stops the program; with an older version, the exception it raises can be
  swallowed by the code's `except Exception`, and the program carries on:
  prefer `c`.

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

## What is asked

5 tasks, 100 points, 25 minutes.

The ticket is in `TICKET.md`. Your suite runs with `uv run pytest`, the tool
with `bin/certcheck`, and the debugging log goes in `DEBUG.md`, at the root
of the project.

### Task 1: a test reproduces the bug (20 pts)

Your suite fails on the original version of `src/certcheck/certificats.py`,
the one from the ticket, and passes on the reference version: at least one
test catches the bug, and only it.

### Task 2: the bug is fixed (20 pts)

`bin/certcheck` reads certificates whose expiry day has a single digit:
statuses, `days_left`, `not_after` and exit code are right, on randomly
drawn fleets, dates and thresholds.

### Task 3: the test stays, and passes afterwards (20 pts)

`uv run pytest` is green on your fixed version, and the suite has more tests
than the shipped one: the reproduction test stayed.

### Task 4: no regression (20 pts)

The rest of the contract still holds (inclusive threshold, wrong usage and
missing certificate give 2). A truly unreadable certificate stays `error`,
code 2, and leaves a message naming the host on standard error.

### Task 5: the debugging log (20 pts)

`DEBUG.md` has three written sections: `## Ce que j'ai vu`, `## La cause`
and `## La correction` (what I saw, the cause, the fix; the titles stay in
French). The cause says what breaks the reading of the date.
