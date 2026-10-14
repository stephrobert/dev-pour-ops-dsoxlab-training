# Challenge : un test rouge, lu, corrigé, et un test de plus

5 tâches, 100 points, 20 minutes.

Votre suite vit dans `tests/` et se lance par `uv run pytest -v`. Les tâches 1
et 2 se notent dans `reponses.yaml` et portent sur le projet **tel que vous
l'avez reçu**.

### Tâche 1 : le test rouge est nommé (20 pts)

`test_en_echec` donne le nom de la fonction de test qui échoue.

### Tâche 2 : l'assertion est lue (20 pts)

`valeur_attendue` et `valeur_obtenue` reprennent les deux valeurs que compare
la ligne `E   assert ...` de pytest.

### Tâche 3 : le défaut est corrigé (20 pts)

`bin/certcheck` classe en `warning`, avec le code 1, un certificat qui expire
exactement au seuil, sur des hôtes, des seuils et des dates tirés au hasard.

### Tâche 4 : la suite est verte, et complète (20 pts)

`uv run pytest` est vert sur votre version, et les quatre tests reçus sont
toujours là.

### Tâche 5 : un test ajouté attrape un nouveau défaut (20 pts)

La suite compte au moins cinq tests, passe sur l'outil de référence, et
échoue sur une version où un warning seul sort en 0.

Pour faire noter : `dsoxlab check tester-une-automatisation`.
