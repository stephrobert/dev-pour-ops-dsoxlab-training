# Step in on a tool you did not write

## Situation

The operations team runs `certcheck` every night, a small Python tool that
reports the TLS certificates to renew. A ticket just came in (`TICKET.md`):
the 31 October report let through a certificate that expired at the
threshold. And the CI pipeline has been red for a few days; its last log is in
`ci/run-12.log`.

The tool's repository comes as a bundle, `depot.bundle`: clone it with
`git clone depot.bundle certcheck`, and work in `certcheck/`.

## What is expected

1. **Understand** the tool and write in `reponses.yaml` its role, the command
   it declares and the host it misclassifies on the ticket's date.
2. **Read** the CI log and the history: the failing step, the command that
   replays it on your workstation, the commit that introduced the defect.
3. **Fix**, keeping the change limited to the defect.
4. **Check**: `uv run pytest -v` green, `uv run ruff check .` and
   `uv run ruff format --check .` green, and every CI step passing again.

## What is graded

The state of the working directory and of `certcheck/`, never the commands
typed. The tool is run the way cron runs it, on random cases, and the CI steps
are replayed in a clean copy. No hint is offered: the exam measures what you
already know how to do. Pass mark: 70 points.
