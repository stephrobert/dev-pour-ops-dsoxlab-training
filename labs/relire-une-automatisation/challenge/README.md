# Challenge: review pull request #42

5 tasks, 100 points, 25 minutes.

The working directory holds the project on `main`, the PR description
(`pr/DESCRIPTION.md`) and its diff (`pr/0042.diff`). Your review goes in
`revue.yaml`, whose header documents the format and the four categories. A
comment points at a defect if it names the right file, the right category,
and a line at most two lines away from the faulty one, counted in the file
**after** `git apply`.

### Task 1: at least three defects found (20 pts)

Of the PR's four defects (swallowed error, printed secret, dangerous path,
missing test), at least three are pointed at by a comment.

### Task 2: every comment proposes a fix (20 pts)

Every comment has a `commentaire` and a `proposition` of at least 25
characters each, its category comes from the list, and at most two comments
point at no real defect.

### Task 3: a verdict (20 pts)

`verdict` is `demander-des-changements` (request changes).

### Task 4: a versioned ruff configuration (20 pts)

The project carries a ruff configuration: a `[tool.ruff]` section in
`pyproject.toml`, or a `ruff.toml` file.

### Task 5: ruff check and ruff format pass on the base code (20 pts)

`uv run ruff check .` reports nothing any more, the base code's unused import
was removed from the code, not hidden by the configuration, and
`uv run ruff format --check .` finds no file left to reformat.
