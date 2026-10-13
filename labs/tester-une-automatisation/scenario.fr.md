# Une suite qui attrape les vrais bogues

## Situation

certcheck tourne chaque nuit. Il décide si le contrôle passe au rouge, et il
ouvre un ticket sur la forge quand des certificats sont à renouveler. Trois
personnes vont le retoucher ce trimestre. Sa seule suite de tests est un
exemple qui vérifie qu'un certificat valide jusqu'en 2045 est `ok`.

Le répertoire de travail est un petit projet uv : `certcheck.py`, son lanceur
`bin/certcheck`, le contrat `CONTRAT.md`, quatre certificats à dates fixes,
et `tests/test_certcheck.py`. pytest est déclaré dans le groupe `dev` de
`pyproject.toml`, à une version exacte verrouillée par `uv.lock`.

## Objectif

Une suite de **six tests au moins**, verte sur l'outil juste, qui échoue sur
chacun des quatre mutants préparés par l'équipe. Chaque mutant porte un
défaut qu'un développeur introduit vraiment en retouchant ce genre d'outil :
une frontière décalée, une erreur avalée, un code de sortie faux, une
simulation qui n'en est pas une.

## Repères

- **L'horloge s'injecte.** Les certificats ont des dates fixes : un test qui
  dépend du jour où il tourne passera aujourd'hui et cassera dans six mois.
  Passez la date aux fonctions (`analyser(entrees, seuil, date(2031, 2, 20))`)
  ou fixez-la par `CERTCHECK_NOW` quand vous lancez `bin/certcheck`.
- **Deux étages.** Les fonctions de décision (`statut`, `code_de_sortie`,
  `analyser`) se testent en les appelant ; le code de sortie et la simulation
  se testent en lançant `bin/certcheck` avec `subprocess.run`.
- **Le réseau se double.** Un test ne parle jamais à une vraie forge. Une
  doublure, petit serveur HTTP local (`http.server`) ou `monkeypatch` sur
  `certcheck.requete`, enregistre ce que l'outil envoie. Pour prouver que
  `--dry-run` n'envoie rien, il faut une forge configurée et joignable :
  sans elle, « rien n'est parti » ne prouve rien.
- `tmp_path` donne un dossier propre à chaque test, pour y écrire un
  inventaire ou un faux certificat.

## Preuve

`dsoxlab check tester-une-automatisation` copie votre projet, remplace
`certcheck.py` par la référence puis par chaque mutant, et lance
`uv run pytest`. Votre propre `certcheck.py` n'est jamais modifié.
