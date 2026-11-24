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
2. **Read** the CI log and the code: the failing step, the command that
   replays it on your workstation, the file holding the defect.
3. **Fix**, keeping the change limited to the defect.
4. **Check**: `uv run pytest -v` green, `uv run ruff check .` and
   `uv run ruff format --check .` green, and every CI step passing again.

## What is graded

The state of the working directory and of `certcheck/`, never the commands
typed. The tool is run the way cron runs it, on random cases, and the CI steps
are replayed in a clean copy. No hint is offered: the exam measures what you
already know how to do. Pass mark: 70 points.

## Exam: step in on a small operations tool

5 tasks, 100 points, 45 minutes. Pass mark: 70 points.

No hint is offered. First clone the repository:
`git clone depot.bundle certcheck`. Tasks 1 and 2 go into `reponses.yaml` and
are about the repository **as received**; tasks 3 to 5 are about
`certcheck/`.

### Task 1: the tool is understood (20 pts)

`role`, `commande_declaree` and `hote_mal_classe` describe the received tool.

### Task 2: the CI is read and the defect located (20 pts)

`etape_en_echec` names the red step of `ci/run-12.log` as `ci.yml` names it,
`commande_locale` replays it on your workstation, and `fichier_du_defaut`
names the file holding the ticket's defect.

### Task 3: the defect is fixed (20 pts)

`bin/certcheck` honours the contract's decision (inclusive threshold, expired,
exit codes) on random hosts, thresholds and dates.

### Task 4: the tests are green, and complete (20 pts)

`uv run pytest` is green, the five tests received are still there, and those tests, replayed as received against your code, pass: changing a test fixes nothing.

### Task 5: quality and CI pass (20 pts)

Every `run:` step of the received `ci.yml` (dependencies, quality, tests,
package) passes, replayed in a clean copy of `certcheck/`.

To get graded: `dsoxlab check level-exams-intervenir`.
