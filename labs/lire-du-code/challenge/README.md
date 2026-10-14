# Challenge: read and modify the certcheck script

5 tasks, 100 points, 25 minutes.

The `challenge/work` directory holds `certcheck.py`, its inventory and the
collected certificates. Tasks 1 to 3 go into `reponses.yaml` and are about the
script **as you received it**; tasks 4 and 5 are done in `certcheck.py`.

### Task 1: what the script does (20 pts)

`role` is picked from the list in `reponses.yaml`, and `programme_externe`
names the program the script runs to read a certificate.

### Task 2: its inputs (20 pts)

`option_seuil` gives the option that sets the alert threshold, `variable_date`
the environment variable that replaces today's date, and `fonction_verdict`
the name of the function that decides a certificate's verdict.

### Task 3: what running it shows (20 pts)

`code_de_sortie`, `hotes_en_alerte` and `hote_au_seuil` are what you observe
when running `CERTCHECK_NOW=2026-10-31 python3 certcheck.py` on the provided
inventory, before any change.

### Task 4: the threshold is inclusive (20 pts)

A certificate that expires in exactly N days, with `--days N`, is shown as
`warning` and the script exits with 1; at N + 1 days it stays `ok` and the
script exits with 0. Checked on random hosts, thresholds and dates.

### Task 5: an expired certificate is reported (20 pts)

A certificate whose date has passed is shown as `expired`, and the script
exits with 1.

To get graded: `dsoxlab check lire-du-code`.
