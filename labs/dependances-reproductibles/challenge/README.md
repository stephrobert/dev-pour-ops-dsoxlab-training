# Challenge: certcheck installs elsewhere too

5 tasks, 100 points, 25 minutes. Network access required (PyPI).

The check reads the project files, then installs it in a **fresh
environment**, without your `.venv`: with `uv sync --frozen` if it finds a
`uv.lock`, otherwise with `pip install -r requirements.txt` (if present)
then `pip install .`.

### Task 1: the dependencies are declared (20 pts)

`requests` and `cryptography` are declared, in `pyproject.toml`
(`[project] dependencies`) or in `requirements.txt`.

### Task 2: the versions are pinned (20 pts)

Each carries an exact version (`==`), or a `uv.lock` freezes both.

### Task 3: the Python version is noted (20 pts)

`pyproject.toml` carries a `requires-python`, or the project has a
`.python-version` file.

### Task 4: installation in a fresh environment (20 pts)

Installed from the project files alone, `certcheck --version` prints
`certcheck 0.5.0`.

### Task 5: nothing installed by hand (20 pts)

In that same fresh environment, certcheck analyses a fleet and publishes its
ticket on a fake forge: everything it imports, `requests` included, comes
from the project files.
