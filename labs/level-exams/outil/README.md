# Exam: take over an operations tool

This exam closes the **Development for Ops** course. It is not a lesson: it
measures, on a new situation, what the common thread worked on, from reading
the inherited script to shipping a version.

| | |
|---|---|
| Target | your machine: Bash, Python or Go, your choice (`mise install`), plus Git, make and openssl |
| Duration | about 120 minutes |
| Passing score | 70 points out of 100 |
| Hints | none |
| Course | [Développer pour les Ops](https://blog.stephane-robert.info/docs/developper/parcours/) (in French) |

| Task | What is checked |
|---|---|
| The contract | interface, exit codes 0, 1 and 2, JSON, configuration, tabs, CRLF, single-digit day, missing certificate as 2, on random draws |
| Publishing | token in the header and never in the URL, idempotence, pagination, retry on 503, timeout against a silent forge (exit code 3 in under 60 s) |
| Your tests | `./test.sh` passes against your tool and the reference, and fails against a variant reproducing the inherited defect |
| Shipping | annotated tag, CHANGELOG, version lock, `make install` from a clone of the tag |
| The review | at least four of the five defects of PR #57, actionable comments, verdict |

```bash
dsoxlab run   level-exams-outil
cd labs/level-exams/outil/challenge/work
dsoxlab challenge level-exams-outil
# ... your work ...
dsoxlab check level-exams-outil
```

`CHOIX.md` is not graded by the check: it is judged on the self-assessment
grid it contains.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
instructor's solution, replayable. The verdict is in `validation-labs.json`.
