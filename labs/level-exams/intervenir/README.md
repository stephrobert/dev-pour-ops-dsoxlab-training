# Exam: step in on a small operations tool

End-of-level exam for level o1 of **Development for Ops**: a measurement, not
a lesson. A small Python tool, a recent change that introduced a defect, a red
CI run. You read the code and the CI log, make a limited fix and
get tests, quality and CI back to green.

| | |
|---|---|
| Target | your workstation: uv and Python (`mise install`), openssl and Git, no VM |
| Duration | about 45 minutes, pass mark 70 points, no hints |
| Exam page | [Exam: step in on a small operations tool](https://blog.stephane-robert.info/docs/developper/pratiques/epreuve-intervenir/) (in French) |

```bash
dsoxlab run   level-exams-intervenir
cd labs/level-exams/intervenir/challenge/work
git clone depot.bundle certcheck
less TICKET.md ci/run-12.log
dsoxlab check level-exams-intervenir
```

What a pass proves: stepping in on a small, supported Python project. What it
does not prove: writing a tool, a pipeline or a release, nor the autonomy of a
Python developer.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
instructor's solution, replayable. The verdict is in `validation-labs.json`.
