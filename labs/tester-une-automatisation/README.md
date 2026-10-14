# Use the tests

Common-thread lab of **Development for Ops**, paired with the lesson "First
Python tests with pytest: the basic move". certcheck has four tests, and one
of them has been red since a change. You run the suite, read the failure, fix
the code and not the test, run it again until green, then add a test by
copying a model.

| | |
|---|---|
| Target | your workstation: Python and uv (`mise install`), openssl |
| Duration | about 20 minutes |
| Paired lesson | [First Python tests with pytest](https://dev.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) (in French) |
| Previous | `dependances-reproductibles` |
| Next | `deboguer` |

```bash
dsoxlab run   tester-une-automatisation
cd labs/tester-une-automatisation/challenge/work
uv run pytest -v          # one red test: read the E line
# fix src/certcheck/certificats.py, run again, add a test
dsoxlab check tester-une-automatisation
```

The check recomputes the red test on the delivered project, runs
`bin/certcheck` on random cases, then runs your suite on the correct tool and
on a version carrying a new defect: your added test must catch it.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
instructor's solution, replayable. The verdict is in `validation-labs.json`.
