# Review an automation change

Lab of the common thread of **Development for Ops**, paired with the lesson
"Relire une automatisation". This time you do not write the code: you
**review** it. A colleague proposes a pull request on certcheck, its tests
pass, and it is up to you to say whether it can be merged. A useful review
points at a precise defect, at a precise line, and proposes a fix the author
can apply.

| | |
|---|---|
| Target | your machine: Git and an editor, no VM |
| Duration | about 40 minutes |
| Paired lesson | [Relire une automatisation](https://blog.stephane-robert.info/docs/developper/pratiques/relire-une-automatisation/) (in French) |

```bash
dsoxlab run   relire-une-automatisation
cd labs/relire-une-automatisation/challenge/work
less pr/DESCRIPTION.md pr/0042.diff
cp -r . /tmp/pr42 && (cd /tmp/pr42 && git apply pr/0042.diff)
# write your review into revue.yaml, then write .pre-commit-config.yaml
dsoxlab check relire-une-automatisation
```

The review goes into `revue.yaml` (French keys and categories, kept as they
are). The check applies the diff itself on the untouched starting point to
know at which lines the defects are: nothing to guess, everything can be
read in the code.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
