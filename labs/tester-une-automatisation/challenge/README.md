# Challenge: first tests, two real bugs caught

5 tasks, 100 points, 25 minutes.

Your suite lives in `tests/` and runs with `uv run pytest`. The check runs it
on a copy of the project where `src/certcheck/certificats.py` is replaced:
first by the
correct tool, then by each of two buggy versions. Every task also requires
the suite to pass on the correct tool.

### Task 1: the suite passes on the correct tool (20 pts)

`uv run pytest` finds at least one test, and all of them are green on the
reference, whatever the day they run.

### Task 2: at least three tests (20 pts)

The suite has at least three green tests: one rule per test.

### Task 3: catch an exclusive threshold (20 pts)

The suite fails on a tool where a certificate expiring in exactly 30 days,
with a threshold of 30, is `ok` instead of `warning`.

### Task 4: catch an exit code 0 despite an alert (20 pts)

The suite fails on a tool that exits with 0 while a certificate is in
`warning`.

### Task 5: a temporary file or a fixed date (20 pts)

At least one test takes `tmp_path` as a parameter, or sets today's date with
`CERTCHECK_NOW` to run the whole tool.
