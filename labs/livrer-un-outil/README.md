# Shipping an internal tool

A lab of the **Development for Ops** common thread, paired with the
lesson "Livrer un outil". certcheck installs identically elsewhere; it now
has to become a **release**: a version number with a single source, a
changelog, a Git tag, built artefacts, and the proof that it installs from
the tag alone.

| | |
|---|---|
| Target | your machine: uv, Python (`mise install`) and Git |
| Duration | about 40 minutes |
| Network | **required**: the clean install downloads the dependencies from PyPI (uv builds with its bundled `uv_build` backend) |
| Paired lesson | [Livrer un outil](https://blog.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) (in French) |
| Previous | `dependances-reproductibles`, whose solution is the starting point |

```bash
dsoxlab run   livrer-un-outil
cd labs/livrer-un-outil/challenge/work
git init                     # the working directory is not a repository yet
bin/certcheck --version
# version, changelog, commit, tag, build
dsoxlab check livrer-un-outil
```

The check clones your repository at the `v1.0.0` tag into a temporary
folder, builds the wheel there, installs it in a fresh environment and runs
certcheck: what anyone installing your release does.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
