# Challenge: a suite that catches four real bugs

5 tasks, 100 points, 45 minutes.

Your suite lives in `tests/` and runs with `uv run pytest`. The check runs it
on a copy of the project where `certcheck.py` is replaced: first by the
correct tool, then by each of the four mutants. Each mutant task also
requires the suite to pass on the correct tool.

### Task 1: a suite that is green on the correct tool (20 pts)

At least six tests, all green on the reference, whatever the day they run:
the date is set through `CERTCHECK_NOW` or passed to the functions.

### Task 2: catch an exclusive threshold (20 pts)

The suite fails on a tool where a certificate expiring in exactly N days,
with a threshold of N, is `ok` instead of `warning`.

### Task 3: catch a swallowed error (20 pts)

The suite fails on a tool that counts an unreadable certificate as `ok`,
without the exit code reporting it.

### Task 4: catch a silent exit code (20 pts)

The suite fails on a tool that exits 0 while certificates are in `warning`.

### Task 5: catch a dry run that sends (20 pts)

The suite fails on a tool whose `--publish --dry-run` still sends the ticket
to the forge. The network is replaced by a test double: a local HTTP server
or a replacement of the request function.
