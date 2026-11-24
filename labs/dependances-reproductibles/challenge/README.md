# Works on my machine

## Situation

A colleague evolved certcheck: the expiry date is read by the
`cryptography` library, and publishing to the forge goes through
`requests`. He installed both by hand in his virtual environment (his
`README.md` shows it), and declared nothing: `pyproject.toml` lists no
dependency and no Python version. "Works on my machine."

On yours, `bin/certcheck --version` already fails.

## Why declare and pin

A **virtual environment** (`.venv`) isolates a project's libraries from the
system's. But it is not shared: what counts are the repository files that
say what to install in it. A library installed by hand only exists on your
machine. And a dependency declared without a version takes the latest
release: two machines, two versions, two behaviours.

## Steps

### 1. See the failure

```bash
bin/certcheck --version; echo "code: $?"
```

`ModuleNotFoundError: No module named 'cryptography'`: the code imports it,
nothing declares it.

### 2. Declare both dependencies

With uv, one command writes the dependency in `pyproject.toml` and installs
it in `.venv`:

```bash
uv add requests cryptography
```

Look at `pyproject.toml`: a `dependencies` section appeared. So did a
`uv.lock` file.

### 3. Pin the versions

Open `uv.lock`: it freezes the **exact** version of every package,
including those `requests` needs (`urllib3`, `idna`...). This lockfile is
versioned with the code: a colleague running `uv sync` gets exactly the same
versions. Without uv, the equivalent is a `requirements.txt` whose every
line carries `==` (`requests==2.34.2`).

### 4. Note the Python version

In `pyproject.toml`, `[project]` section, add `requires-python = ">=3.12"`:
the oldest supported version. You can also pin the project's own with
`uv python pin 3.14`, which writes `.python-version`. Run `uv lock` again
after editing `pyproject.toml`.

### 5. Check as a colleague would

In a copy without `.venv`, the tool must install from the files alone:

```bash
rsync -a --exclude .venv ./ /tmp/trial/ && cd /tmp/trial
uv sync && uv run certcheck --version
```

Then `dsoxlab check dependances-reproductibles`.

## Certcheck installs elsewhere too

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
