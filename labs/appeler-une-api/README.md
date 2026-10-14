# Call an API with requests

Common-thread lab of **Development for Ops**, paired with the lesson "Appeler
une API REST avec Python et requests". certcheck can already check a fleet; it
must now **open a ticket** on the forge when certificates are due. You write
that call with the `requests` library, step by step: declare the dependency,
put the token in the right place, bound the wait, handle errors, avoid
duplicates.

| | |
|---|---|
| Target | your machine: Python and uv (`mise install`), openssl |
| Duration | about 30 minutes |
| Network | needed once: uv downloads `requests` from PyPI |
| Paired lesson | [Appeler une API REST avec Python et requests](https://blog.stephane-robert.info/docs/developper/api-rest/) (in French) |
| Previous | `script-en-outil` (optional lab, outside the core) |

```bash
dsoxlab run   appeler-une-api
cd labs/appeler-une-api/challenge/work
CERTCHECK_NOW=2026-06-01 bin/certcheck --publish --dry-run; echo "code: $?"
# follow the scenario steps in src/certcheck/forge.py
python3 forge_factice.py        # in a second terminal, to try it out
dsoxlab check appeler-une-api
```

The check does not read your code: it runs `bin/certcheck --publish`
against a fake forge that answers like the Forgejo API, and looks at the
requests it receives.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
