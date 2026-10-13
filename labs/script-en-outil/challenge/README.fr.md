# Challenge : certcheck respecte son contrat

5 tâches, 100 points, 60 minutes.

Votre outil est appelé par `bin/certcheck`, et seulement par lui. Le contrat
est dans `CONTRAT.md`.

### Tâche 1 : une interface prévisible (20 pts)

`--help` sort en 0 et cite chaque option ; `--version` affiche
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

### Tâche 4 : la configuration par l'environnement (20 pts)

`CERTCHECK_INVENTORY` et `CERTCHECK_DAYS` sont lus, l'option l'emporte sur la
variable, une valeur invalide rend 2, et l'inventaire accepte tabulations et
commentaires.

### Tâche 5 : une simulation qui n'envoie rien (20 pts)

`--publish --dry-run` n'envoie aucune requête et montre le ticket sur la
sortie d'erreur ; `--publish` sans `FORGE_TOKEN` rend 2 sans rien envoyer.
