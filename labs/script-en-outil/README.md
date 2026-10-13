# From script to tool

Second lab of the **Development for Ops** common thread, paired with the
lesson "Structurer un script en outil". The inherited script from the
previous lab becomes a **tool**: an interface discovered through `--help`,
exit codes a scheduler can read, a JSON output, configuration through the
environment and a dry-run mode.

| | |
|---|---|
| Target | your machine: Python (`mise install`), Go or Bash, your choice |
| Duration | about 60 minutes |
| Paired lesson | [Structurer un script en outil](https://blog.stephane-robert.info/docs/developper/pratiques/script-en-outil/) (in French) |
| Previous | `lire-du-code` |
| Next | `appeler-une-api` starts from the reference solution |

```bash
dsoxlab run   script-en-outil
cd labs/script-en-outil/challenge/work
less CONTRAT.md
# write your tool, then point bin/certcheck at it
CERTCHECK_NOW=2031-02-20 bin/certcheck --format json; echo "code: $?"
dsoxlab check script-en-outil
```

The check never reads your code: it runs `bin/certcheck` as cron would, with
inventories and dates drawn at random.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
