# Vos premiers tests

## Situation

certcheck tourne chaque nuit. Il décide si le contrôle passe au rouge, et
trois personnes vont le retoucher ce trimestre. Aujourd'hui, rien ne prouve
qu'une retouche ne casse pas une règle du contrat : il n'a aucun test.

Le répertoire de travail est le paquet Python de certcheck : son code dans
`src/certcheck/` (la décision est dans `certificats.py`), son lanceur
`bin/certcheck`, le contrat `CONTRAT.md`, quatre certificats à dates
fixes, et `tests/test_certcheck.py`, encore vide. pytest est déclaré dans le
groupe `dev` de `pyproject.toml` : `uv run pytest` l'installe au premier
lancement.

## Pourquoi tester

Un test est une petite fonction qui appelle le code avec une entrée connue
et vérifie le résultat par `assert`. Il ne sert pas à prouver que le code
marche aujourd'hui : il sert à **voir tout de suite** quand une retouche
change un comportement. Le contrôle de ce lab le vérifie concrètement : il
joue votre suite sur deux versions de certcheck qui portent chacune un
bogue, et elle doit les attraper.

## Étapes

### 1. Un premier test

Lancez `uv run pytest -v` : pytest répond « no tests ran ». Ajoutez à la fin
de `tests/test_certcheck.py` :

```python
def test_un_certificat_lointain_est_ok():
    resultats = certificats.analyser([("web-01", CERTS / "web-01.pem")], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "ok"
```

Relancez : `1 passed`. La date du jour est un **argument** : le test rend le
même verdict en 2026 et en 2040. Un test qui dépend du jour où il tourne
finit toujours par casser.

### 2. La frontière du seuil

Le contrat dit que le seuil est **inclusif** : un certificat qui expire dans
exactement 30 jours, avec un seuil de 30, est en `warning`. Les bogues se
cachent aux limites. Écrivez un test qui vérifie `certificats.statut(30, 30)`,
et un autre cas de part et d'autre (`statut(31, 30)`, `statut(-1, 30)`).

### 3. Le code de sortie

`certificats.code_de_sortie(resultats)` rend 0, 1 ou 2 selon les statuts (voir
`CONTRAT.md`). Vérifiez qu'une liste qui ne contient qu'un warning,
`[{"status": "warning"}]`, rend bien 1. Testez un statut à la fois : un test
qui ne regarde que des `expired` laisse passer un oubli sur les `warning`.

### 4. Un fichier temporaire ou une date fixée

Ajoutez un paramètre `tmp_path` à un test : pytest lui donne un dossier
vide, propre à ce test, sous `/tmp/pytest-of-<utilisateur>/`. Il ne l'efface
pas tout de suite : il garde les dossiers des trois dernières exécutions,
pour qu'on puisse inspecter ce qu'un test a écrit, et supprime les plus
anciens. Écrivez-y un faux certificat et vérifiez qu'il est en `error` :

```python
def test_un_certificat_illisible_est_en_erreur(tmp_path):
    faux = tmp_path / "faux.pem"
    faux.write_text("ceci n'est pas un certificat\n")
    resultats = certificats.analyser([("faux", faux)], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "error"
```

Pour tester l'outil entier, lancez `bin/certcheck` avec `subprocess.run` en
fixant la date par la variable `CERTCHECK_NOW` (exemple dans les indices).

### 5. Vérifier

`uv run pytest -v` doit être vert, puis `dsoxlab check
tester-une-automatisation`.

## Preuve

`dsoxlab check tester-une-automatisation` copie votre projet, remplace
le module `src/certcheck/certificats.py` par la référence puis par chaque
version boguée, et lance `uv run pytest`. Votre propre code n'est jamais
modifié.
