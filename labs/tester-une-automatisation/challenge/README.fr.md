# Challenge : une suite qui attrape quatre vrais bogues

5 tâches, 100 points, 45 minutes.

Votre suite vit dans `tests/` et se lance par `uv run pytest`. Le contrôle la
joue sur une copie du projet où `certcheck.py` est remplacé : d'abord par
l'outil juste, puis par chacun des quatre mutants. Chaque tâche de mutant
exige aussi que la suite passe sur l'outil juste.

### Tâche 1 : une suite verte sur l'outil juste (20 pts)

Au moins six tests, tous verts sur la référence, quel que soit le jour où ils
tournent : la date se fixe par `CERTCHECK_NOW` ou se passe aux fonctions.

### Tâche 2 : attraper un seuil exclusif (20 pts)

La suite échoue sur un outil où un certificat qui expire dans exactement N
jours, avec un seuil de N, passe en `ok` au lieu de `warning`.

### Tâche 3 : attraper une erreur avalée (20 pts)

La suite échoue sur un outil qui compte un certificat illisible comme `ok`,
sans que le code de sortie le signale.

### Tâche 4 : attraper un code de sortie muet (20 pts)

La suite échoue sur un outil qui sort en 0 alors que des certificats sont en
`warning`.

### Tâche 5 : attraper une simulation qui envoie (20 pts)

La suite échoue sur un outil dont `--publish --dry-run` envoie quand même le
ticket à la forge. Le réseau est remplacé par une doublure : serveur HTTP
local ou remplacement de la fonction de requête.
