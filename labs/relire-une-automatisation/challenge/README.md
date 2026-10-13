# Challenge: review pull request #42

5 tasks, 100 points, 40 minutes.

The `challenge/work` directory holds the project on `main`, the pull request
description (`pr/DESCRIPTION.md`) and its diff (`pr/0042.diff`). Your review
goes into `revue.yaml`, whose header documents the format and the closed list
of categories. A comment points at a defect if it has the right file, the
right category, and a line at most two lines away from the faulty line,
counted in the file **after** `git apply`.

### Task 1: the exposed secret and the disabled TLS (20 pts)

Two comments report the webhook URL, which carries a token, written to an
output (`secret-expose`), and the chat certificate check turned off
(`tls-desactive`).

### Task 2: the swallowed error and the unbounded side effect (20 pts)

Two comments report the exception caught then ignored (`erreur-avalee`) and
the recursive deletion whose target is not validated
(`effet-de-bord-non-borne`).

### Task 3: the unpinned dependency and the missing test (20 pts)

Two comments report the dependency declared without an exact version
(`dependance-non-epinglee`) and the new function no test exercises
(`test-absent`, on its `def` line within three lines, or on the test file).

### Task 4: an actionable review (20 pts)

Each comment has a `commentaire` and a `proposition` of at least 25
characters, every category comes from the closed list, at most two comments
point at no real defect, and `verdict` is `demander-des-changements`.

### Task 5: mechanical defects refused at commit time (20 pts)

`.pre-commit-config.yaml`, at the project root, declares a secret detector
(gitleaks, detect-secrets or detect-private-key) and the ruff linter, each
from its official repository, and every `rev` is a full 40-character commit
hash. The check reads the file, it does not run pre-commit.
