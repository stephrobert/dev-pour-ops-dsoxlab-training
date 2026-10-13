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
