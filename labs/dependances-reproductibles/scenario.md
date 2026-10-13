# Works on my machine

## Situation

A colleague evolved certcheck. The expiry date is now read by the
`cryptography` library (no more call to `openssl`), and publishing to the
forge goes through `requests`. He made it a package: `src/certcheck/`, a
`certcheck` entry point declared in `[project.scripts]`, version 0.5.0.

Its dependencies stayed in a `requirements.txt` he installed by hand in his
virtual environment: two names, no version at all. `pyproject.toml` declares
none of them, does not say which Python versions are supported, there is no
lockfile, and nothing says which interpreter to use. "Works on my machine."

On yours, `bin/certcheck --version` already fails.

## Goal

Anyone, starting from the repository alone, gets exactly the same tool:

1. `pyproject.toml` declares `requests` and `cryptography` (with a lower
   bound) and a `requires-python`;
2. a `uv.lock` exists and matches `pyproject.toml`;
3. the interpreter is pinned to a precise version, compatible with
   `requires-python`;
4. a clean copy, without `.venv`, installs with `uv sync --frozen` and
   returns the contract's result;
5. only one source of truth remains: `requirements.txt` is deleted, or
   generated from the lockfile.

## Hints

- The lower bound (`>=`) goes in `pyproject.toml`; the exact version of each
  package, transitive ones included, goes in `uv.lock`.
- `uv lock --check` tells whether the lockfile still matches
  `pyproject.toml`.
- A pinned Python version must be obtainable elsewhere: check that uv can
  find or download it (`uv python list`).
- This lab needs network access: uv downloads from PyPI.
