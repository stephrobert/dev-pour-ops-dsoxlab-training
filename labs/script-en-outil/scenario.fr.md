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
