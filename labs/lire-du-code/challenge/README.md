# Challenge: read the certcheck package

5 tasks, 100 points, 30 minutes.

The `challenge/work` directory holds the inherited Python project, its
inventory, the collected certificates and its history. Your answers go into
`reponses.yaml`.

### Task 1: the entry point and its modules (20 pts)

`point_d_entree` gives the function the `certcheck` command runs, in the
`module:function` form declared in `[project.scripts]`, and
`modules_internes` lists exactly the package modules that module imports,
including an import placed inside a function.

### Task 2: the side effects (20 pts)

`sous_processus` names the program launched as a subprocess,
`fonction_appel_reseau` the function that sends the network request, and
`variable_appel_reseau` the variable that triggers that call.

### Task 3: running it safely (20 pts)

`code_de_sortie` and `hote_mal_classe` are those observed by running
`uv run certcheck` on the provided inventory, with
`CERTCHECK_NOW=2026-06-01` and without `FORGE_TOKEN`.

### Task 4: the real defects (20 pts)

`defauts` lists every real defect from the proposed list, and no other.

### Task 5: the history (20 pts)

`commit_erreur_avalee` gives the hash of the commit that introduced
`except Exception` in `src/certcheck/certificats.py`.
