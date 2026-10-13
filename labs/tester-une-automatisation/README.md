# First tests

Common-thread lab of **Development for Ops**, paired with the lesson "Premiers
tests Python avec pytest : le geste de base". certcheck honours its contract;
it must now keep honouring it when someone edits it. You write its **first
pytest tests**, step by step, and the suite is graded on the bugs it catches.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), openssl |
| Duration | about 25 minutes |
| Paired lesson | [Premiers tests Python avec pytest : le geste de base](https://blog.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) (in French) |
| Previous | `appeler-une-api` |
| Next | `deboguer` |

```bash
dsoxlab run   tester-une-automatisation
cd labs/tester-une-automatisation/challenge/work
uv run pytest -v          # "no tests ran": writing the first one is up to you
# follow the scenario steps in tests/test_certcheck.py
dsoxlab check tester-une-automatisation
```

The check runs your suite, through `uv run pytest`, on the correct tool and
then on two buggy versions: the reference with a single defect each. A useful
suite passes on the first and fails on each of the other two.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
