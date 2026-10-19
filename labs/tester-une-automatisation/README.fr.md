# Se servir des tests

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon « Premiers
tests Python avec pytest : le geste de base ». certcheck a quatre tests, et
l'un d'eux est rouge depuis une retouche. Vous lancez la suite, lisez l'échec,
corrigez le code et non le test, relancez jusqu'au vert, puis ajoutez un test
en copiant un modèle.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), openssl |
| Durée | environ 20 minutes |
| Leçon jumelée | [Premiers tests Python avec pytest : le geste de base](https://www.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) |
| Précédent | `dependances-reproductibles` |
| Suite | `deboguer` |

```bash
dsoxlab run   tester-une-automatisation
cd labs/tester-une-automatisation/challenge/work
uv run pytest -v          # un test rouge : lisez la ligne E
# corrigez src/certcheck/certificats.py, relancez, ajoutez un test
dsoxlab check tester-une-automatisation
```

Le contrôle recalcule le test rouge sur le projet livré, lance `bin/certcheck`
sur des cas tirés au hasard, puis joue votre suite sur l'outil juste et sur une
version qui porte un nouveau défaut : votre test ajouté doit l'attraper.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
