# Exam: step in on a small operations tool

5 tasks, 100 points, 45 minutes. Pass mark: 70 points.

No hint is offered. First clone the repository:
`git clone depot.bundle certcheck`. Tasks 1 and 2 go into `reponses.yaml` and
are about the repository **as received**; tasks 3 to 5 are about
`certcheck/`.

### Task 1: the tool is understood (20 pts)

`role`, `commande_declaree` and `hote_mal_classe` describe the received tool.

### Task 2: the CI is read and the defect located (20 pts)

`etape_en_echec` names the red step of `ci/run-12.log` as `ci.yml` names it,
`commande_locale` replays it on your workstation, and `fichier_du_defaut`
names the file holding the ticket's defect.

### Task 3: the defect is fixed (20 pts)

`bin/certcheck` honours the contract's decision (inclusive threshold, expired,
exit codes) on random hosts, thresholds and dates.

### Task 4: the tests are green, and complete (20 pts)

`uv run pytest` is green, the five tests received are still there, and those tests, replayed as received against your code, pass: changing a test fixes nothing.

### Task 5: quality and CI pass (20 pts)

Every `run:` step of the received `ci.yml` (dependencies, quality, tests,
package) passes, replayed in a clean copy of `certcheck/`.

To get graded: `dsoxlab check level-exams-intervenir`.
