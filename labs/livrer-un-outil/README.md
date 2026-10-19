# Ship a tool

Common-thread lab of **Development for Ops**, paired with the lesson "Livrer
un outil Python : version, étiquette, installation". certcheck installs
elsewhere; it now has to become a **release**: a number written in one place,
a changelog, a Git tag, and the proof that it installs in a fresh environment.
Nothing is published: the release stays in the repository.

| | |
|---|---|
| Target | your machine: uv, Python (`mise install`) and Git |
| Duration | about 25 minutes |
| Network | **required**: the fresh installation downloads dependencies from PyPI |
| Paired lesson | [Livrer un outil Python : version, étiquette, installation](https://www.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) (in French) |
| Previous | `dependances-reproductibles` (optional lab, outside the core) |

```bash
dsoxlab run   livrer-un-outil
cd labs/livrer-un-outil/challenge/work
bin/certcheck --version      # certcheck 0.5.0
# follow the scenario steps
dsoxlab check livrer-un-outil
```

The check installs your project in a fresh environment, then clones your
repository at the `v1.0.0` tag and installs it the same way: what whoever
fetches your release does.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable. The verdict is in `validation-labs.json`.
