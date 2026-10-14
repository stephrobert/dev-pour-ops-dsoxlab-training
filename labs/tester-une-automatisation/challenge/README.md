# Challenge: a red test, read, fixed, and one more test

5 tasks, 100 points, 20 minutes.

Your suite lives in `tests/` and runs with `uv run pytest -v`. Tasks 1 and 2
go into `reponses.yaml` and are about the project **as you received it**.

### Task 1: the red test is named (20 pts)

`test_en_echec` gives the name of the failing test function.

### Task 2: the assertion is read (20 pts)

`valeur_attendue` and `valeur_obtenue` copy the two values compared by
pytest's `E   assert ...` line.

### Task 3: the defect is fixed (20 pts)

`bin/certcheck` classifies as `warning`, with exit code 1, a certificate that
expires exactly at the threshold, on random hosts, thresholds and dates.

### Task 4: the suite is green, and complete (20 pts)

`uv run pytest` is green on your version, and the four tests you received are
still there.

### Task 5: an added test catches a new defect (20 pts)

The suite holds at least five tests, passes on the reference tool, and fails
on a version where a lone warning exits with 0.

To get graded: `dsoxlab check tester-une-automatisation`.
