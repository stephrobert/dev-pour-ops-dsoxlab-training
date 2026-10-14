# Challenge: understand certcheck, then modify it

5 tasks, 100 points, 20 minutes.

The `challenge/work` directory holds the certcheck Python project and its
contract, `CONTRAT.md`. Tasks 1 to 3 go into `reponses.yaml` and are about the
project **as you received it**; tasks 4 and 5 are done in
`src/certcheck/cli.py`.

### Task 1: the command is declared by the project (20 pts)

`fichier_declaration` names the file that declares the `certcheck` command,
and `commande_declaree` copies what it declares, in the `module:function`
form.

### Task 2: where things are (20 pts)

`module_decision` gives the file that holds the `statut` function, and
`lanceur` the file cron or a pipeline runs, paths from the working directory.

### Task 3: the observed exit codes (20 pts)

The three codes in `reponses.yaml` are those observed when running the given
commands on the project you received.

### Task 4: the threshold comes from the environment (20 pts)

`CERTCHECK_DAYS` sets the threshold when `--days` is absent, `--days` wins
over the variable, and a value that is not a positive integer returns 2, with
a message on standard error.

### Task 5: errors go to standard error (20 pts)

A missing inventory returns 2, with a one-line message on standard error, no
Python traceback and nothing on standard output. A missing certificate stays
in the JSON as `error`, and its host is named on standard error.

To get graded: `dsoxlab check script-en-outil`.
