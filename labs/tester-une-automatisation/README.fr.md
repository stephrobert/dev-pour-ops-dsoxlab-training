# Premiers tests

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon « Tester
une automatisation ». certcheck respecte son contrat ; il faut maintenant
qu'il continue à le respecter quand quelqu'un le retouche. Vous écrivez ses
**premiers tests pytest**, pas à pas, et la suite est notée sur les bogues
qu'elle attrape.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), openssl |
| Durée | environ 25 minutes |
| Leçon jumelée | [Tester une automatisation](https://blog.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) |
| Précédent | `appeler-une-api` |
| Suite | `deboguer` |

```bash
dsoxlab run   tester-une-automatisation
cd labs/tester-une-automatisation/challenge/work
uv run pytest -v          # « no tests ran » : à vous d'écrire le premier
# suivez les étapes du scénario dans tests/test_certcheck.py
dsoxlab check tester-une-automatisation
```

Le contrôle joue votre suite, par `uv run pytest`, sur l'outil juste puis sur
deux versions boguées : la référence avec un seul défaut chacune. Une suite
utile passe sur la première et échoue sur chacune des deux autres.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
