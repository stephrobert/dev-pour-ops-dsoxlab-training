# Structure a Python project as a tool

Second lab of the **Development for Ops** common thread, paired with the
lesson "Structurer un projet Python en outil". The inherited Bash script is
replaced by a **Python project** structured the way a developer does it: a
package under `src/certcheck/`, a `pyproject.toml` that declares the
`certcheck` command, a `uv.lock`, and a short contract honoured: an
interface discovered through `--help`, exit codes a scheduler can read, a
JSON output, a threshold set through the environment and errors on standard
error. The skeleton is provided: you complete guided functions.

| | |
|---|---|
| Target | your machine: uv and Python (`mise install`), openssl, no VM |
| Duration | about 30 minutes |
| Paired lesson | [Structurer un projet Python en outil](https://blog.stephane-robert.info/docs/developper/pratiques/script-en-outil/) (in French) |
| Previous | `lire-du-code` |
| Next | `appeler-une-api` starts from the reference solution |

```bash
dsoxlab run   script-en-outil
cd labs/script-en-outil/challenge/work
less CONTRAT.md pyproject.toml src/certcheck/certificats.py src/certcheck/cli.py
# write the functions that raise NotImplementedError, then:
CERTCHECK_NOW=2031-02-20 bin/certcheck --format json; echo "code: $?"
dsoxlab check script-en-outil
```

The check verifies that `bin/certcheck` does run the project's package, then
stops reading your code: it runs `bin/certcheck` as cron would, with
inventories and dates drawn at random.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
