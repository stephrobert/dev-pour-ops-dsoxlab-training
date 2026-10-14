# Challenge: take over an operations tool

5 tasks, 100 points, 60 minutes. Passing score: 70 points.

No hint is offered: the exam measures what you already know how to do.
Nothing reads your code: each check runs your files the way the colleague
who takes the tool over after you would, and the contract checks are
**hidden**, played on inventories, thresholds and dates drawn at random.

## What you receive

- `certcheck.sh`, the inherited script, to read only: nothing runs it any
  more;
- the skeleton of the Python project that replaces it: `pyproject.toml` (the
  `certcheck` command in `[project.scripts]`, the `[build-system]`, and
  pytest 9.1.1 in the `[dependency-groups]` development group), `uv.lock`,
  which locks those versions, the `src/certcheck/` package whose functions
  to write raise `NotImplementedError`, and `bin/certcheck`, which already
  runs that package through `uv run --project`;
- `CONTRAT.md`, what the tool must do, seen from outside (in French);
- `inventaire.txt` and `certs/`, a small fleet to try things on;
- `pr/`, Inès's pull request #57: its description, its diff, and the
  `pr/main/` project it applies to;
- `revue.yaml`, to fill in.

## What you deliver, at the root of the working directory

The skeleton gives the project its shape; grading is about what you make
of it. A row marked "provided" must stay correct until delivery, a row
marked "to write" is entirely yours.

| File | Role |
|---|---|
| `pyproject.toml` | provided: carry the shipped version there, keep the `certcheck` command in `[project.scripts]` |
| `src/certcheck/` | provided, to complete: the tool's Python package, compliant with `CONTRAT.md` |
| `bin/certcheck` | provided: the launcher, which runs your package through `uv run --project` |
| `tests/` | to write: your pytest tests, which run the executable named by `CERTCHECK_BIN` (default: `bin/certcheck`) |
| `uv.lock` | provided: the pinned (`==`) development dependencies, pytest at least; `uv run` keeps it up to date |
| `CHANGELOG.md` | to write: a `## [X.Y.Z]` section for the shipped version |
| `revue.yaml` | to fill in: your review of PR #57, in the form its header describes |

The working directory becomes a Git repository, and the shipped version
carries a `vX.Y.Z` tag (annotated or not).

### Task 1: the tool honours the contract (20 pts)

Interface (`--help`, `--version`, incorrect usage), exit codes 0, 1 and 2,
a JSON output exact to the day with an inclusive threshold, threshold set
through `CERTCHECK_DAYS` with the option taking precedence, inventories with
mixed separators (spaces and tabs), certificates whose expiry day is a
single digit, and a missing certificate reported as `error` with exit
code 2.

### Task 2: your tests catch the inherited bug (20 pts)

`uv run pytest tests` is run three times, in a copy of the working
directory, changing only `CERTCHECK_BIN`: it passes against your tool, with
at least three passing tests, passes against the instructor's reference
tool, and **fails** against a variant that reproduces the inherited
script's bug (a missing certificate counted as `warning` at 0 days, exit
code 1).

### Task 3: the project installs (20 pts)

`pyproject.toml` declares the `certcheck` command, the code lives in a
package under `src/`, and the development dependencies are pinned. The
project is installed (`pip install .`) into a fresh environment: the
`certcheck --version` command there prints the `pyproject.toml` version, and
the installed tool passes a smoke test. The skeleton already installs: what
earns the points is `--version` and the smoke test, which go through your
code, and the printed version must follow the `pyproject.toml` one when you
change it.

### Task 4: the version is recorded and tagged (20 pts)

The highest `vX.Y.Z` tag points to a commit whose `CHANGELOG.md` carries the
`## [X.Y.Z]` section and whose `pyproject.toml` carries version `X.Y.Z`.

### Task 5: the review of PR #57 (20 pts)

The PR carries four defects, all from categories of the closed list in
`revue.yaml`. At least three are pointed at by a comment with the right file
(path from `pr/main`), the right category, and a line within two of the
faulty one in the file **after** applying the diff; every comment and every
proposal is at least 25 characters long; at most two comments point at no
real defect; `verdict` is `demander-des-changements`.

To get graded: `dsoxlab check level-exams-outil`.
