# Dependencies: certcheck installs elsewhere too

A lab of the **Development for Ops** common thread, paired with the lesson
"Dépendances Python : déclarer, épingler, installer ailleurs". certcheck
became a Python package that imports `requests` and `cryptography`, but its
author installed them by hand: nothing guarantees it installs elsewhere. You
declare its dependencies, pin their versions, note the Python version, and
prove it in a fresh environment.

| | |
|---|---|
| Target | your machine: uv and Python (`mise install` at the catalogue root) |
| Duration | about 25 minutes |
| Network | **required**: packages are downloaded from PyPI |
| Paired lesson | [Dépendances Python : déclarer, épingler, installer ailleurs](https://dev.stephane-robert.info/docs/developper/pratiques/dependances-reproductibles/) (in French) |
| Next | `tester-une-automatisation` |

```bash
dsoxlab run   dependances-reproductibles
cd labs/dependances-reproductibles/challenge/work
cat README.md pyproject.toml
bin/certcheck --version; echo "code: $?"      # fails: nothing is declared
# follow the scenario steps
dsoxlab check dependances-reproductibles
```

The check copies your project **without** its `.venv`, installs it in a
fresh environment from its files alone, and runs certcheck: the situation
of a colleague or a pipeline that fetches the repository.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
