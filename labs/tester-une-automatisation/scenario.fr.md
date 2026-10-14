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
