# Call an API without fragility

Third lab of the **Development for Ops** common thread, paired with the
lesson "Automatiser par une API REST : authentification, pagination, erreurs
et reprise". certcheck can already check a fleet; it must now **publish** its
result to the forge without leaking a secret, without duplicates, and
without hanging when the forge is in trouble.

| | |
|---|---|
| Target | your machine: Python (`mise install`) and openssl |
| Duration | about 45 minutes |
| Paired lesson | [Automatiser par une API REST](https://blog.stephane-robert.info/docs/developper/api-rest/) (in French) |
| Previous | `script-en-outil` |

```bash
dsoxlab run   appeler-une-api
cd labs/appeler-une-api/challenge/work
less CONTRAT.md                       # section "Publication sur la forge"
CERTCHECK_NOW=2026-06-01 bin/certcheck --publish --dry-run; echo "code: $?"
# fix the "Publication sur la forge" part of certcheck.py
dsoxlab check appeler-une-api
```

The starting point is the tool from the previous lab, compliant with the
contract except for its publication, written in a hurry by a colleague. The
check never reads your code: it runs `bin/certcheck --publish` against a
fake forge that answers like the Forgejo API, and counts the requests it
receives.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
