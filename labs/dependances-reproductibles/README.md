# Reproducible dependencies

A lab of the **Development for Ops** common thread, paired with the lesson
"Dépendances reproductibles". certcheck became a Python package that imports
`requests` and `cryptography`, but nothing guarantees it installs elsewhere
the way it does on its author's machine. You declare its dependencies, lock
them, pin the interpreter, and prove it on a clean copy.

| | |
|---|---|
| Target | your machine: uv and Python (`mise install` at the catalogue root) |
| Duration | about 40 minutes |
| Network | **required**: uv downloads the packages from PyPI, and the pinned interpreter if missing |
| Paired lesson | [Dépendances reproductibles](https://blog.stephane-robert.info/docs/developper/pratiques/dependances-reproductibles/) (in French) |
| Next | `livrer-un-outil` starts from this lab's solution |

```bash
dsoxlab run   dependances-reproductibles
cd labs/dependances-reproductibles/challenge/work
cat requirements.txt pyproject.toml
bin/certcheck --version; echo "code: $?"      # fails: nothing is declared
# declare, lock, pin, then check as a colleague would
dsoxlab check dependances-reproductibles
```

The check copies your project **without** its `.venv`, installs it with
`uv sync --frozen` and runs certcheck on a random inventory: the situation
of a colleague or a pipeline that fetches the repository.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
