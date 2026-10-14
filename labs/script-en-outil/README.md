# Understand a Python tool, then modify it

Second lab of the common thread of **Development for Ops**, paired with the
lesson "Structure a Python project as a command-line tool". The small script
from the previous lab has become a **Python project**, structured the way a
developer does it: a package under `src/certcheck/`, a `pyproject.toml` that
declares the `certcheck` command, a `uv.lock`, a `bin/certcheck` launcher and
a written contract. You first find your way around it, then close two gaps
with the contract: the threshold read from the environment, and errors
written on standard error.

| | |
|---|---|
| Target | your workstation: uv and Python (`mise install`), openssl, no VM |
| Duration | about 20 minutes |
| Paired lesson | [Structure a Python project as a command-line tool](https://dev.stephane-robert.info/docs/developper/pratiques/script-en-outil/) (in French) |
| Previous | `lire-du-code` |
| Next | `dependances-reproductibles` |

```bash
dsoxlab run   script-en-outil
cd labs/script-en-outil/challenge/work
less CONTRAT.md pyproject.toml src/certcheck/cli.py
CERTCHECK_NOW=2026-06-01 bin/certcheck; echo "code: $?"
dsoxlab check script-en-outil
```

The check reads the delivered project again to recompute your answers, then
runs `bin/certcheck` the way cron would, without reading your code.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
instructor's solution, replayable. The verdict is in `validation-labs.json`.
