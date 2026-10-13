# The pull request with green tests

## Situation

certcheck runs every night from the cron of the operations server. Malik
proposes **pull request #42**: purge the old reports, which filled the disk,
and post the alerts to the team chat webhook. He added tests, they pass, and
he asks you for a review before merging.

The working directory holds the project as it is on `main`
(`certcheck.py`, `pyproject.toml`, `tests/`), the pull request description
(`pr/DESCRIPTION.md`) and its diff (`pr/0042.diff`).

## Goal

Write a review Malik can apply without asking you anything again, in
`revue.yaml`: each real defect reported in the right file, at the right
line, in the right category, with a concrete fix, then a verdict. Finally,
add to the project a `.pre-commit-config.yaml` that will refuse at commit
time the defects a machine can see, so the next review focuses on what
matters.

## Hints

- Read the description first, then check each claim in the code: "it is
  worked around", "it is handled" and "tests added" are proven or refuted
  line by line.
- `git apply pr/0042.diff` in a copy of the project gives the files as they
  would be merged; the review line numbers are those, not the diff's.
- For each environment variable read, ask yourself what the code does when
  it is missing.
- `git ls-remote <repository> 'refs/tags/<tag>*'` gives the commit hash of a
  tag without cloning anything. `pre-commit autoupdate --freeze` does the
  same for a whole configuration.
