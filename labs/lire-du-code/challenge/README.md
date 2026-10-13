# Challenge: read certcheck.sh

5 tasks, 100 points, 30 minutes.

The `challenge/work` directory holds the inherited script, its inventory,
the collected certificates and its history. Your answers go into
`reponses.yaml`.

### Task 1: the external commands (20 pts)

`commandes_externes` lists exactly the PATH programs the script calls,
without Bash builtins.

### Task 2: the side effects (20 pts)

`fichier_ecrit` names the file the script writes, and
`variable_appel_reseau` the variable that triggers the call to the forge.

### Task 3: running it safely (20 pts)

`code_de_sortie` and `hote_mal_signale` are those observed by running the
script on the provided inventory, without `FORGE_TOKEN`.

### Task 4: the real defects (20 pts)

`defauts` lists every real defect from the proposed list, and no other.

### Task 5: the history (20 pts)

`commit_erreur_avalee` gives the hash of the commit that introduced
`2>/dev/null` on the openssl call.
