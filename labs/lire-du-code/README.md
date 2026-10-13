# Read the code of a Python application

First lab of the common thread of the **Development for Ops** course, paired
with the lesson "Lire le code d'une application Python qu'on n'a pas écrite".
The starting point is the most common situation for a developer joining a
team: an application running in production, that nobody around them wrote, and
that they are asked to take over. Before touching it, you **read** it: the
entry point the package declares, the modules it loads, side effects,
configuration, history.

| | |
|---|---|
| Target | your machine: uv and Python (`mise install`), openssl and Git, no VM |
| Duration | about 30 minutes |
| Paired lesson | [Lire le code d'une application Python qu'on n'a pas écrite](https://blog.stephane-robert.info/docs/developper/pratiques/lire-du-code/) (in French) |
| Next | `script-en-outil` structures a Python project that honours a contract |

```bash
dsoxlab run   lire-du-code
cd labs/lire-du-code/challenge/work
less pyproject.toml src/certcheck/cli.py
CERTCHECK_NOW=2026-06-01 uv run certcheck --inventory inventaire.txt; echo "code: $?"
git clone historique.bundle historique
dsoxlab check lire-du-code
```

Answers go into `reponses.yaml` (French keys, kept as they are). The check
takes nothing on trust: it rereads the code, replays the package and the
history to recompute each answer.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
