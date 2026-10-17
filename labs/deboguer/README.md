# Debug step by step

Common-thread lab of **Development for Ops**, paired with the lesson "Déboguer
un programme Python pas à pas, avec pdb". A ticket came in: certcheck reports
a certificate as unreadable while openssl reads it without trouble. You handle
it in order rather than by trial and error: **reproduce** with a test,
**look** at the faulty value, **fix**, and keep a short record of what you
learned.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), openssl |
| Duration | about 25 minutes |
| Paired lesson | [Déboguer un programme Python pas à pas, avec pdb](https://blog.stephane-robert.info/docs/developper/pratiques/deboguer/) (in French) |
| Previous | `tester-une-automatisation` |

```bash
dsoxlab run   deboguer
cd labs/deboguer/challenge/work
less TICKET.md
uv run pytest -v                  # the shipped suite passes, and yet
# follow the scenario steps
dsoxlab check deboguer
```

The check runs your suite on the original buggy version (it must fail) and
on the reference (it must pass), runs `bin/certcheck` on randomly drawn
fleets, checks the rest of the contract and reads `DEBUG.md`.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
