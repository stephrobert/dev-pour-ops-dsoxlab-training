# Un outil qui a un contrat

## Situation

Le petit script du lab précédent est devenu un **projet Python** : un collègue
l'a découpé comme le fait un développeur. Le paquet `src/certcheck/` contient
deux modules (`certificats.py` lit l'inventaire et décide du statut, `cli.py`
gère l'interface), `pyproject.toml` déclare la commande `certcheck`, `uv.lock`
fige l'environnement, et le lanceur `bin/certcheck` exécute le tout par
`uv run`. L'équipe a écrit ce que l'outil doit faire dans `CONTRAT.md`.

Deux tickets sont ouverts : l'outil ignore la variable `CERTCHECK_DAYS` que le
contrat promet, et quand l'inventaire manque, son message d'erreur part sur la
sortie standard, là où un programme attend le résultat.

## Objectif

D'abord **se repérer** dans le projet et le noter dans `reponses.yaml` : quel
fichier déclare la commande, ce qu'il déclare, où vit la décision, quel fichier
cron lance, et quels codes de sortie l'outil rend. Ensuite, **combler les deux
écarts** au contrat, sans rien réécrire d'autre.

## Repères

- `uv run certcheck --help` et `bin/certcheck --help` lancent la même chose :
  la commande que `pyproject.toml` déclare dans `[project.scripts]`.
- `CERTCHECK_NOW=2026-06-01 bin/certcheck; echo $?` rejoue le contrôle à une
  date fixée et affiche son code de sortie ; `CONTRAT.md` dit ce qu'il signifie.
- Le seuil se décide dans une seule fonction de `cli.py`, et `os.environ.get`
  lit une variable d'environnement.
- `print(..., file=sys.stderr)` écrit sur la sortie d'erreur ; la sortie
  standard ne porte que le résultat.

## Comprendre certcheck, puis le modifier

5 tâches, 100 points, 20 minutes.

Le répertoire `challenge/work` contient le projet Python certcheck et son
contrat, `CONTRAT.md`. Les tâches 1 à 3 se notent dans `reponses.yaml` et
portent sur le projet **tel que vous l'avez reçu** ; les tâches 4 et 5 se font
dans `src/certcheck/cli.py`.

### Tâche 1 : la commande est déclarée par le projet (20 pts)

`fichier_declaration` nomme le fichier qui déclare la commande `certcheck`, et
`commande_declaree` recopie ce qu'il déclare, sous la forme `module:fonction`.

### Tâche 2 : où est quoi (20 pts)

`module_decision` donne le fichier qui contient la fonction `statut`, et
`lanceur` le fichier que cron ou un pipeline lance, chemins depuis le
répertoire de travail.

### Tâche 3 : les codes de sortie observés (20 pts)

Les trois codes de `reponses.yaml` sont ceux qu'on observe en lançant les
commandes indiquées sur le projet reçu.

### Tâche 4 : le seuil vient de l'environnement (20 pts)

`CERTCHECK_DAYS` règle le seuil quand `--days` est absent, `--days` l'emporte
sur la variable, et une valeur qui n'est pas un entier positif rend 2, avec un
message sur la sortie d'erreur.

### Tâche 5 : les erreurs vont sur la sortie d'erreur (20 pts)

Un inventaire absent rend 2, avec un message d'une ligne sur la sortie
d'erreur, ni trace Python ni rien sur la sortie standard. Un certificat absent
reste dans le JSON en `error`, et son hôte est nommé sur la sortie d'erreur.

Pour faire noter : `dsoxlab check script-en-outil`.
