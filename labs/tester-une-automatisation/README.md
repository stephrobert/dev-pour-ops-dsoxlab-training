# Test an automation

Common-thread lab of **Development for Ops**, paired with the lesson "Tester
une automatisation". certcheck honours its contract; it must now keep
honouring it when someone edits it. You write its **pytest suite**, and it is
graded on the defects it catches.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), openssl |
| Duration | about 45 minutes |
| Paired lesson | [Tester une automatisation](https://blog.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) (in French) |
| Previous | `appeler-une-api` |
| Next | `deboguer` |

```bash
dsoxlab run   tester-une-automatisation
cd labs/tester-une-automatisation/challenge/work
uv run pytest -v          # the shipped example passes
# write your tests in tests/test_certcheck.py
dsoxlab check tester-une-automatisation
```

The check runs your suite, through `uv run pytest`, on the correct tool and
then on four mutants: the reference with a single defect each. A useful suite
passes on the first and fails on each of the other four.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
