# Challenge : certcheck respecte son contrat

5 tâches, 100 points, 30 minutes.

Votre outil est le paquet Python `src/certcheck/` du projet, appelé par
`bin/certcheck`, et seulement par lui. Le contrat est dans `CONTRAT.md`.

### Tâche 1 : un projet Python et une interface prévisible (20 pts)

`pyproject.toml` déclare la commande `certcheck` dans `[project.scripts]`
vers une fonction du paquet `src/certcheck/`, et `bin/certcheck` lance ce
paquet : `uv run certcheck --version` et `bin/certcheck --version` répondent
la même chose. `--help` sort en 0 et cite chaque option ; `--version` affiche
`certcheck X.Y.Z` ; une option inconnue, `--days abc` ou `--format xml`
sortent en 2 avec un message sur la sortie d'erreur et rien sur la sortie
standard.

### Tâche 2 : des codes de sortie exploitables (20 pts)

0, 1 ou 2 selon les certificats, sur des inventaires tirés au hasard ; un
certificat absent ou un inventaire absent rendent 2.

### Tâche 3 : une sortie JSON exploitable (20 pts)

`--format json` rend un seul document, avec `days_left`, `status` et
`not_after` justes pour chaque hôte, seuil inclusif ; `--format text` porte
l'hôte et son statut sur chaque ligne.

### Tâche 4 : le seuil vient de l'environnement (20 pts)

`CERTCHECK_DAYS` règle le seuil, `--days` l'emporte sur la variable, une
valeur invalide rend 2, et l'inventaire accepte tabulations et commentaires,
lancé depuis un autre dossier.

### Tâche 5 : les erreurs vont sur la sortie d'erreur (20 pts)

Un certificat absent figure dans le JSON en `error`, et son hôte est nommé
sur la sortie d'erreur, sans polluer le document ; un inventaire absent rend
2, avec un message d'une ligne sur la sortie d'erreur, ni trace Python ni
rien sur la sortie standard.
