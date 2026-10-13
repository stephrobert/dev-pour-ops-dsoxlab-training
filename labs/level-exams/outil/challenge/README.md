# Exam: take over an operations tool

5 tasks, 100 points, 120 minutes. Passing score: 70 points.

No hint is offered: the exam measures what you already know how to do. The
language is your choice, Bash, Python or Go. Nothing reads your code: each
check runs your files the way the colleague who takes the tool over after you
would, and the contract checks are **hidden**, played on inventories,
thresholds and dates drawn at random.

## What you receive

- `certcheck.sh`, the inherited script, and `bin/certcheck`, which runs it;
- `CONTRAT.md`, what the tool must do, seen from outside (in French);
- `inventaire.txt` and `certs/`, a small fleet to try things on;
- `pr/`, Inès's pull request #57: its description, its diff, and the
  `pr/main/` project it applies to;
- `revue.yaml` and `CHOIX.md`, to fill in.

## What you deliver, at the root of the working directory

| File | Role |
|---|---|
| `bin/certcheck` | your tool's entry point, compliant with `CONTRAT.md` |
| `test.sh` | runs YOUR test suite against the executable named by `CERTCHECK_BIN` (default: `bin/certcheck`), exits 0 when everything passes |
| version lock | `uv.lock` (Python), `go.sum` or `go.mod` with `toolchain goX.Y.Z` (Go), or `mise.toml` with exact X.Y.Z versions (Bash) |
| `CHANGELOG.md` | a `## [X.Y.Z]` section for the shipped version |
| `Makefile` | `make install PREFIX=<dir>` installs `<dir>/bin/certcheck` |
| `revue.yaml` | your review of PR #57, in the form its header describes |
| `CHOIX.md` | why you chose that language |

The working directory becomes a Git repository, and the shipped version
carries an **annotated tag** `vX.Y.Z`.

### Task 1: the tool honours the contract (20 pts)

Interface (`--help`, `--version`, incorrect usage), exit codes 0, 1 and 2,
a JSON output exact to the day with an inclusive threshold, configuration
through the environment with the option taking precedence, inventories with
mixed separators (spaces and tabs) and CRLF line endings, certificates whose
expiry day is a single digit, and a missing certificate reported as `error`
with exit code 2.

### Task 2: publishing is safe, idempotent and bounded (20 pts)

With `--publish` against a fake forge: the token goes in the header and
never in the URL nor on an output, a second run opens no duplicate, the
existing ticket is found on the second page, two 503 responses are retried,
and against a forge that accepts the connection and never answers, the tool
gives up on its own, with exit code 3, in less than 60 seconds.

### Task 3: your test suite catches the inherited defect (20 pts)

`./test.sh` is run three times, in a copy of the working directory, changing
only `CERTCHECK_BIN`: it passes against your tool, passes against the
instructor's reference tool, and **fails** against a variant that reproduces
the inherited script's defect (a missing certificate counted as `warning` at
0 days, exit code 1).

### Task 4: the version ships from its tag (20 pts)

The highest annotated tag `vX.Y.Z` carries a `CHANGELOG.md` with its
`## [X.Y.Z]` section and a version lock. It is cloned into a temporary
directory, `make install PREFIX=<tmp>` runs there, then the clone is
deleted: `<tmp>/bin/certcheck --version` prints `certcheck X.Y.Z` and the
installed tool passes a smoke test.

### Task 5: the review of PR #57 (20 pts)

The PR carries five defects, all from categories of the closed list in
`revue.yaml`. At least four are pointed at by a comment with the right file
(path from `pr/main`), the right category, and a line within two of the
faulty one in the file **after** applying the diff; every comment and every
proposal is at least 25 characters long; at most two comments point at no
real defect; `verdict` is `demander-des-changements`.

## What is not graded automatically

`CHOIX.md` is **self-assessed**: the grid it contains is published, score
yourself on it. A language choice is judged on its arguments, not by a test.

To get graded: `dsoxlab check level-exams-outil`.
