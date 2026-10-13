# Relire une pull request

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon « Relire
une automatisation ». Cette fois, vous n'écrivez pas le code : vous le
**relisez**. Un collègue propose une pull request sur certcheck, ses tests
passent, et c'est à vous de dire si elle peut être fusionnée. Une revue utile
désigne un défaut précis, à une ligne précise, et propose une correction que
l'auteur peut appliquer. Vous confiez ensuite les défauts mécaniques à une
machine : le linter ruff.

| | |
|---|---|
| Cible | votre poste : uv (`mise install`), Git et un éditeur, aucune VM |
| Durée | environ 25 minutes |
| Leçon jumelée | [Relire une automatisation](https://blog.stephane-robert.info/docs/developper/pratiques/relire-une-automatisation/) |

```bash
dsoxlab run   relire-une-automatisation
cd labs/relire-une-automatisation/challenge/work
less pr/DESCRIPTION.md pr/0042.diff
cp -r . /tmp/pr42 && (cd /tmp/pr42 && git apply pr/0042.diff)
# notez votre revue dans revue.yaml, puis configurez ruff
dsoxlab check relire-une-automatisation
```

Le contrôle applique lui-même le diff sur le point de départ intact pour
savoir à quelles lignes se trouvent les défauts : il n'y a rien à deviner,
tout se lit dans le code.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
