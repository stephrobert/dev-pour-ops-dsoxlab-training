# Challenge : premiers tests, deux vrais bogues attrapés

5 tâches, 100 points, 25 minutes.

Votre suite vit dans `tests/` et se lance par `uv run pytest`. Le contrôle la
joue sur une copie du projet où `src/certcheck/certificats.py` est remplacé :
d'abord par
l'outil juste, puis par chacune de deux versions boguées. Chaque tâche exige
aussi que la suite passe sur l'outil juste.

### Tâche 1 : la suite passe sur l'outil juste (20 pts)

`uv run pytest` trouve au moins un test, et tous sont verts sur la
référence, quel que soit le jour où ils tournent.

### Tâche 2 : au moins trois tests (20 pts)

La suite compte au moins trois tests verts : une règle par test.

### Tâche 3 : attraper un seuil exclusif (20 pts)

La suite échoue sur un outil où un certificat qui expire dans exactement 30
jours, avec un seuil de 30, passe en `ok` au lieu de `warning`.

### Tâche 4 : attraper un code 0 malgré une alerte (20 pts)

La suite échoue sur un outil qui sort en 0 alors qu'un certificat est en
`warning`.

### Tâche 5 : un fichier temporaire ou une date fixée (20 pts)

Un test au moins reçoit `tmp_path` en paramètre, ou fixe la date du jour par
`CERTCHECK_NOW` pour lancer l'outil entier.
