# Read and modify a small Python script

First lab of the common thread of the **Development for Ops** course, paired
with the lesson "Read and modify Python code you did not write". The starting
point is the most common situation for an Ops: a script that runs every
night, that nobody around them wrote, and that they are asked to fix. Before
touching it, you **read** it: its role, its inputs, the function that decides,
what it prints and its exit code. Only then do you change a condition.

| | |
|---|---|
| Target | your workstation: Python 3 and openssl, no VM |
| Duration | about 25 minutes |
| Paired lesson | [Read and modify Python code you did not write](https://blog.stephane-robert.info/docs/developper/pratiques/lire-du-code/) (in French) |
| Next | `script-en-outil` shows the same tool turned into a Python project |

```bash
dsoxlab run   lire-du-code
cd labs/lire-du-code/challenge/work
less certcheck.py
python3 certcheck.py --help
CERTCHECK_NOW=2026-10-31 python3 certcheck.py; echo "code: $?"
dsoxlab check lire-du-code
```

Answers go into `reponses.yaml`. The check takes nothing on trust: it replays
the script you received to recompute each answer, then runs your version on
random inventories and dates.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
instructor's solution, replayable. The verdict is in `validation-labs.json`.
