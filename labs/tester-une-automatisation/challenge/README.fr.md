# Un test rouge

## Situation

certcheck tourne chaque nuit et décide si le contrôle passe au rouge. Hier,
quelqu'un a retouché la décision ; ce matin, la suite de tests est rouge.
Personne ne l'a regardée.

Le répertoire de travail est le projet Python de certcheck : son code dans
`src/certcheck/` (la décision est dans `certificats.py`), son lanceur
`bin/certcheck`, le contrat `CONTRAT.md`, quelques certificats à dates fixes,
et `tests/test_certcheck.py`, qui contient quatre tests. pytest est déclaré
dans le groupe `dev` de `pyproject.toml` : `uv run pytest` l'installe au
premier lancement.

## Pourquoi tester

Un test est une petite fonction qui appelle le code avec une entrée connue et
vérifie le résultat par `assert`. Il sert à **voir tout de suite** quand une
retouche change un comportement : c'est exactement ce qui vient de se passer.

## Étapes

### 1. Lancer la suite et lire l'échec

```bash
uv run pytest -v
```

Trois tests passent, un échoue. Notez dans `reponses.yaml` le nom du test
rouge (ligne `FAILED`), puis lisez la ligne qui commence par `E` : `assert X
== Y` met côte à côte ce que le code a rendu (X) et ce que le test attendait
(Y).

### 2. Corriger le code, pas le test

Le test décrit le contrat (`CONTRAT.md`, section « Décision ») ; c'est le code
qui s'en est écarté. Ouvrez `src/certcheck/certificats.py`, trouvez la
fonction que le test appelle, corrigez la condition, puis relancez
`uv run pytest -v` jusqu'à ce que les quatre tests soient verts.

### 3. Vérifier en lançant l'outil

```bash
CERTCHECK_NOW=2026-06-01 bin/certcheck; echo "code : $?"
```

### 4. Ajouter un test

Les quatre tests ne vérifient pas qu'un **warning seul** donne le code 1.
Copiez `test_un_certificat_expire_est_signale`, renommez la copie (son nom
doit commencer par `test_`) et remplacez son contenu par :

```python
assert certificats.code_de_sortie([{"status": "warning"}]) == 1
```

Relancez : cinq tests verts. Le contrôle jouera votre suite sur une version de
certcheck où un warning seul sort en 0 : votre nouveau test doit la faire
échouer.

## Un test rouge, lu, corrigé, et un test de plus

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
