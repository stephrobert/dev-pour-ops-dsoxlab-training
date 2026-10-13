# Challenge: certcheck installs identically elsewhere

5 tasks, 100 points, 40 minutes. Network access required (PyPI).

The check reads the project files, then installs it in a **clean copy**,
without `.venv`, as a colleague or a pipeline would.

### Task 1: declared dependencies (20 pts)

`pyproject.toml` declares `requests` and `cryptography` in
`[project] dependencies`, each with a lower bound (`>=` or `~=`), and
carries a `requires-python`.

### Task 2: an up-to-date lockfile (20 pts)

`uv.lock` exists, pins `requests` and `cryptography`, and
`uv lock --check` accepts it: it matches `pyproject.toml`.

### Task 3: a pinned interpreter (20 pts)

`.python-version` (or `mise.toml`) carries a precise `X.Y.Z` version, within
`requires-python`.

### Task 4: reproducible elsewhere (20 pts)

In a copy without `.venv`, `uv sync --frozen` succeeds, then
`uv run certcheck --version` and a run on a random inventory, with
`CERTCHECK_NOW`, return the contract's result.

### Task 5: a single source of truth (20 pts)

`requirements.txt` is deleted or, if kept, generated from the lockfile:
every line in `==`, with its `--hash` digests, at the versions of
`uv.lock`.
