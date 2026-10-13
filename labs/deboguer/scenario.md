# The certificate certcheck cannot read

## Situation

`TICKET.md`: certcheck exits in error (code 2) on vpn-01 while openssl reads
its certificate fine. The daily check is red every day, and nobody looks at
the real alerts any more. Nothing in the logs, even with `--verbose`.

The working directory is certcheck's uv project: `certcheck.py`, its
launcher `bin/certcheck`, the contract, four certificates and a test suite
that passes. A green suite only proves what it tests.

## Goal

Handle the ticket with method, in four steps, and keep a record of them in a
`DEBUG.md` file at the root of the project, one `##` section per step (the
headings are in French: `## Reproduire`, `## Réduire`, `## Observer`,
`## Corriger`).

1. **Reproduce.** A symptom you cannot trigger at will cannot be fixed.
   Write a test that fails on the current version, BEFORE touching the
   code: it will prove the fix, and it will stop the bug from coming back.
2. **Reduce.** Remove everything that is not needed (the inventory, the
   other hosts, openssl itself) down to the smallest input that still
   breaks. Quote that exact string, spaces included, in the `## Réduire`
   section.
3. **Observe.** Look at the program at the moment it goes wrong, instead of
   guessing. The bug can be watched under Python's debugger:
   `python3 -m pdb certcheck.py --inventory inventaire.txt`, then a
   breakpoint (`b date_expiration`, or `b <line>, "vpn" in str(certificat)`
   to stop on vpn-01 only), `c` to continue, `p brut` to print a variable,
   `n` to step one line. A `breakpoint()` line in the code does the same
   without any option.
4. **Fix.** The smallest change that makes the reproduction test pass,
   without breaking the rest of the contract. Also ask yourself why the bug
   stayed invisible.

## Hints

- `uv run pytest -v` runs the suite; `uv run pytest -k vpn` runs only the
  tests whose name contains "vpn".
- `openssl x509 -enddate -noout -in certs/vpn-01.pem` shows what certcheck
  receives. Compare with another certificate, character by character:
  `| cat -A` makes spaces and line ends visible.
- Under pdb, quitting with `q` raises a `BdbQuit` exception. An overly broad
  `except Exception` swallows it too, and the program goes on: one more
  clue about what this `except` hides.
- Today's date is set through `CERTCHECK_NOW=YYYY-MM-DD`, or passed to the
  functions: a test must not depend on the day it runs.

## Proof

`dsoxlab check deboguer` runs your suite on the original version (it must
fail) and on the reference (it must pass), runs `bin/certcheck` on random
fleets, replays the rest of the contract, and reads `DEBUG.md`.
