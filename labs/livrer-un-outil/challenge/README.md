# Challenge: certcheck 1.0.0, tagged and installable

5 tasks, 100 points, 40 minutes. Network access required (PyPI).

### Task 1: a single-source version (20 pts)

`pyproject.toml` carries version 1.0.0, `bin/certcheck --version` prints
exactly `certcheck 1.0.0`, no `1.0.0` string is hard-coded under `src/`,
and a copy whose `pyproject.toml` changes version prints the new one without
touching the code.

### Task 2: a dated changelog (20 pts)

`CHANGELOG.md` carries `## [1.0.0] - YYYY-MM-DD`, with at least one heading
(Added, Changed, Fixed or Ajouté, Modifié, Corrigé) and one entry, below
`[Unreleased]` and above earlier versions.

### Task 3: an annotated tag on the right revision (20 pts)

The working directory is a Git repository; `v1.0.0` is an annotated tag; at
the tagged commit, `pyproject.toml` is 1.0.0 and `uv.lock` follows it; the
working tree is clean.

### Task 4: the built artefacts (20 pts)

`dist/` holds `certcheck-1.0.0-py3-none-any.whl` and
`certcheck-1.0.0.tar.gz`; the wheel declares its version, its dependencies
and the `certcheck` entry point.

### Task 5: a clean install from the tag (20 pts)

The repository cloned at `v1.0.0` builds, the wheel installs in a fresh
environment, `certcheck --version` prints `certcheck 1.0.0` there, and a run
on a random inventory returns the contract's result.
