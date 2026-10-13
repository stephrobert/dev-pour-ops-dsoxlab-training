# Release 1.0.0

## Situation

certcheck declares its dependencies and locks them in `uv.lock`: it installs
on any machine. The team now wants to ship it to other teams, as version
**1.0.0**.

Two things are in the way. The version is written **twice**: in
`pyproject.toml` and hard-coded in `src/certcheck/__init__.py`. And the
project is not under Git yet. `CHANGELOG.md` only has an `## [Unreleased]`
section.

## Why version

A version is a stable name for a state of the code: "1.0.0", which the
on-call team can install, quote in a ticket, or reinstall six months later.
It is written in **one place only**, otherwise two files end up stating two
numbers. The changelog says what changes; the Git tag marks the exact commit
carrying that version.

## Steps

### 1. A single source for the version

In `pyproject.toml`, set `version` to `"1.0.0"`. In
`src/certcheck/__init__.py`, replace the hard-coded string with a read of the
installed package's metadata:

```python
from importlib.metadata import version

__version__ = version("certcheck")
```

`bin/certcheck --version` must print `certcheck 1.0.0`.

### 2. The changelog

In `CHANGELOG.md`, keep `## [Unreleased]` on top (empty), and put right
below it a `## [1.0.0] - YYYY-MM-DD` section (today's date) holding the
entries.

### 3. The repository and the tag

The working directory lives inside the catalogue's repository: it needs ITS
own repository, otherwise Git would walk up to the catalogue's.

```bash
git init
git add -A
git commit -m "certcheck 1.0.0"
git tag -a v1.0.0 -m "certcheck 1.0.0"
```

`.gitignore` already excludes `.venv/` and `dist/`. The tag goes **after**
the commit that contains 1.0.0.

### 4. Install in a fresh environment

```bash
python3 -m venv /tmp/trial-env
/tmp/trial-env/bin/pip install .
/tmp/trial-env/bin/certcheck --version
```

### 5. Install from the tag

```bash
git clone --branch v1.0.0 . /tmp/trial-clone
python3 -m venv /tmp/trial-env2
/tmp/trial-env2/bin/pip install /tmp/trial-clone
/tmp/trial-env2/bin/certcheck --version
```

Then `dsoxlab check livrer-un-outil`.

## Outside this lab

Publishing a wheel to an index, building a container image or shipping
through a pipeline belong to other courses: here, the release stays in the
repository.
