# Challenge: the certificate certcheck cannot read

5 tasks, 100 points, 25 minutes.

The ticket is in `TICKET.md`. Your suite runs with `uv run pytest`, the tool
with `bin/certcheck`, and the debugging log goes in `DEBUG.md`, at the root
of the project.

### Task 1: a test reproduces the bug (20 pts)

Your suite fails on the original version of `src/certcheck/certificats.py`,
the one from the ticket, and passes on the reference version: at least one
test catches the bug, and only it.

### Task 2: the bug is fixed (20 pts)

`bin/certcheck` reads certificates whose expiry day has a single digit:
statuses, `days_left`, `not_after` and exit code are right, on randomly
drawn fleets, dates and thresholds.

### Task 3: the test stays, and passes afterwards (20 pts)

`uv run pytest` is green on your fixed version, and the suite has more tests
than the shipped one: the reproduction test stayed.

### Task 4: no regression (20 pts)

The rest of the contract still holds (inclusive threshold, wrong usage and
missing certificate give 2). A truly unreadable certificate stays `error`,
code 2, and leaves a message naming the host on standard error.

### Task 5: the debugging log (20 pts)

`DEBUG.md` has three written sections: `## Ce que j'ai vu`, `## La cause`
and `## La correction` (what I saw, the cause, the fix; the titles stay in
French). The cause says what breaks the reading of the date.
