# Read code you did not write

First lab of the common thread of the **Development for Ops** course, paired
with the lesson "Lire un code qu'on n'a pas écrit". The starting point is the
most common situation for an ops engineer: a script running in production,
that nobody on the team wrote, and that you are asked to take over. Before
touching it, you **read** it: entry point, commands called, side effects,
configuration, history.

| | |
|---|---|
| Target | your machine: Bash, openssl and Git, no VM |
| Duration | about 30 minutes |
| Paired lesson | [Lire un code qu'on n'a pas écrit](https://blog.stephane-robert.info/docs/developper/pratiques/lire-du-code/) (in French) |
| Next | `script-en-outil` turns this script into a tool |

```bash
dsoxlab run   lire-du-code
cd labs/lire-du-code/challenge/work
less certcheck.sh
bash certcheck.sh inventaire.txt; echo "code: $?"
git clone historique.bundle historique
dsoxlab check lire-du-code
```

Answers go into `reponses.yaml` (French keys, kept as they are). The check
takes nothing on trust: it replays the script and the history to recompute
each answer.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
