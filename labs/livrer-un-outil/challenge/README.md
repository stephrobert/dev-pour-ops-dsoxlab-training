# Challenge: certcheck 1.0.0, versioned and installable

5 tasks, 100 points, 25 minutes. Network access required (PyPI).

### Task 1: a single source for the version (20 pts)

`pyproject.toml` carries version 1.0.0, `bin/certcheck --version` prints
exactly `certcheck 1.0.0`, no `1.0.0` string is hard-coded under `src/`, and
a copy whose `pyproject.toml` changes version prints the new one without
touching the code.

### Task 2: the changelog (20 pts)

`CHANGELOG.md` has a `## [1.0.0]` section with at least one `- ...` entry.

### Task 3: the v1.0.0 tag (20 pts)

The working directory is a Git repository, and the `v1.0.0` tag (annotated
or lightweight) points at a commit where `pyproject.toml` says 1.0.0.

### Task 4: installation in a fresh environment (20 pts)

`pip install .` of the project in a fresh environment succeeds, and
`certcheck --version` there prints `certcheck 1.0.0`.

### Task 5: installation from the tag (20 pts)

The repository cloned at `v1.0.0` installs in a fresh environment,
`certcheck --version` there prints `certcheck 1.0.0`, and a run on a
randomly drawn inventory gives the contract's result.
