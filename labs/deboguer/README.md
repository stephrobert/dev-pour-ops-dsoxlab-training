# Debug with method

Common-thread lab of **Development for Ops**, paired with the lesson
"Déboguer". A ticket came in: certcheck reports a certificate as unreadable
while openssl reads it without trouble. You handle it with a **method**
rather than by trial and error: reproduce, reduce, observe, fix, and keep a
record of each step.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), openssl |
| Duration | about 45 minutes |
| Paired lesson | [Déboguer](https://blog.stephane-robert.info/docs/developper/pratiques/deboguer/) (in French) |
| Previous | `tester-une-automatisation` |

```bash
dsoxlab run   deboguer
cd labs/deboguer/challenge/work
less TICKET.md
uv run pytest -v                  # the shipped suite passes, and yet
python3 -m pdb certcheck.py       # watch the bug live
dsoxlab check deboguer
```

The check runs your suite on the original buggy version (it must fail) and
on the reference (it must pass), runs `bin/certcheck` on random fleets,
checks the rest of the contract and reads `DEBUG.md`.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
