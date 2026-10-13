# Tester une automatisation

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon « Tester
une automatisation ». certcheck respecte son contrat ; il faut maintenant
qu'il continue à le respecter quand quelqu'un le retouche. Vous écrivez sa
**suite pytest**, et elle est notée sur les défauts qu'elle attrape.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), openssl |
| Durée | environ 45 minutes |
| Leçon jumelée | [Tester une automatisation](https://blog.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) |
| Précédent | `appeler-une-api` |
| Suite | `deboguer` |

```bash
dsoxlab run   tester-une-automatisation
cd labs/tester-une-automatisation/challenge/work
uv run pytest -v          # l'exemple livré passe
# écrivez vos tests dans tests/test_certcheck.py
dsoxlab check tester-une-automatisation
```

Le contrôle joue votre suite, par `uv run pytest`, sur l'outil juste puis sur
quatre mutants : la référence avec un seul défaut chacun. Une suite utile
passe sur le premier et échoue sur chacun des quatre autres.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
