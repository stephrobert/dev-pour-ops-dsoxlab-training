# Release 1.0.0

## Situation

certcheck declares its dependencies, locks them in `uv.lock` and pins its
interpreter: it installs identically on any machine. The team now wants to
**ship** it to the other teams, as version 1.0.0.

The starting point is the previous lab's solution, with two differences: the
project is not under Git yet (the `git init` and the commits are yours), and
`CHANGELOG.md`, in the Keep a Changelog format, only carries an
`## [Unreleased]` section. The version itself is written twice: in
`pyproject.toml` and hard-coded in `src/certcheck/__init__.py`.

## Goal

1. Version 1.0.0 has a single source, `pyproject.toml`; `certcheck
   --version` prints `certcheck 1.0.0` by reading it from the installed
   package's metadata.
2. `CHANGELOG.md` carries a non-empty `## [1.0.0] - YYYY-MM-DD` section,
   below `[Unreleased]` and above earlier versions.
3. An **annotated** Git tag `v1.0.0` points at the commit that carries
   1.0.0, and the working tree is clean.
4. `dist/` holds the 1.0.0 wheel and sdist, built by `uv build`.
5. A clean environment installs the wheel built from the tag, and certcheck
   runs there.

## Hints

- The working directory sits inside the catalogue repository: without
  `git init` here, Git would climb up to the catalogue's repository.
- `importlib.metadata.version("certcheck")` reads the installed package's
  version; a wheel does not carry `pyproject.toml`.
- The lockfile also records the project's version: after changing
  `pyproject.toml`, run `uv lock` again before committing.
- The Python wheel is only one of the delivery forms covered in the lesson.
  The static Go binary and the container image are the two others; they
  stay out of this lab.
- This lab needs network access: uv downloads from PyPI.
