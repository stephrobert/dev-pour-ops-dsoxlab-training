# Challenge: the certificate certcheck cannot read

5 tasks, 100 points, 45 minutes.

The ticket is in `TICKET.md`. Your suite runs with `uv run pytest`, the tool
with `bin/certcheck`, and the debugging log goes in `DEBUG.md`, at the root
of the project.

### Task 1: a test reproduces the bug (20 pts)

Your suite fails on the original version of `certcheck.py`, the ticket's
one, and passes on the reference version: at least one test catches the
bug, and only it.

### Task 2: the bug is fixed (20 pts)

`bin/certcheck` reads certificates whose expiry day has a single digit:
correct statuses, `days_left`, `not_after` and exit code, on random fleets,
dates and thresholds.

### Task 3: the suite passes on the fixed version (20 pts)

`uv run pytest` is green on your version, and the suite has more tests than
the shipped one: the reproduction test stayed.

### Task 4: no regression (20 pts)

The rest of the contract still holds: usage errors exit 2, inclusive
threshold, tab-separated inventory, missing certificate or missing inventory
exit 2. A truly unreadable certificate stays `error`, exit 2, and leaves a
message naming the host on standard error.

### Task 5: the debugging log (20 pts)

`DEBUG.md` has the sections `## Reproduire`, `## Réduire`, `## Observer`
and `## Corriger`, each one written, and the Réduire section quotes the
smallest string that triggers the bug.
