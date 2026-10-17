# Challenge: take over an operations tool

**Optional** challenge of the **Development for Ops** course, beyond the
introduction: the level exam is `level-exams-intervenir`. This challenge
measures, on a new situation, what is expected from an Ops who ships an
internal tool to other teams: from reading inherited code to shipping a
version of a Python project.

| | |
|---|---|
| Target | your machine: uv and Python (`mise install`), plus Git and openssl |
| Duration | about 60 minutes |
| Passing score | 70 points out of 100 |
| Hints | none |
| Course | [Développer pour les Ops](https://blog.stephane-robert.info/docs/developper/parcours/) (in French) |
| Paired lesson | [Livrer un outil Python : version, étiquette, installation](https://blog.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) (in French) |

| Task | What is checked |
|---|---|
| The contract | interface, exit codes 0, 1 and 2, JSON, threshold through `CERTCHECK_DAYS`, tabs, single-digit day, missing certificate as 2, on random draws |
| Your tests | `uv run pytest tests` passes against your tool (at least 3 tests) and the reference, and fails against a variant reproducing the inherited bug |
| Installation | `pyproject.toml` and a package under `src/`, pinned development dependencies, install into a fresh environment, `certcheck --version` |
| The version | a `vX.Y.Z` tag, the `## [X.Y.Z]` CHANGELOG section and the `pyproject.toml` version at the tagged commit |
| The review | at least three of the four defects of PR #57, actionable comments, verdict |

```bash
dsoxlab run   level-exams-outil
cd labs/level-exams/outil/challenge/work
dsoxlab challenge level-exams-outil
# ... your work ...
dsoxlab check level-exams-outil
```

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
instructor's solution, replayable. The verdict is in `validation-labs.json`.
