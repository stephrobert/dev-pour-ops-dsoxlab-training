# Dépendances : certcheck s'installe aussi ailleurs

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Dépendances reproductibles ». certcheck est devenu un paquet Python qui
importe `requests` et `cryptography`, mais son auteur les a installées à la
main : rien ne garantit qu'il s'installe ailleurs. Vous déclarez ses
dépendances, épinglez leurs versions, notez la version de Python, et le
prouvez dans un environnement neuf.

| | |
|---|---|
| Cible | votre poste : uv et Python (`mise install` à la racine du catalogue) |
| Durée | environ 25 minutes |
| Réseau | **requis** : les paquets se téléchargent depuis PyPI |
| Leçon jumelée | [Dépendances reproductibles](https://blog.stephane-robert.info/docs/developper/pratiques/dependances-reproductibles/) |
| Suite | `livrer-un-outil` |

```bash
dsoxlab run   dependances-reproductibles
cd labs/dependances-reproductibles/challenge/work
cat README.md pyproject.toml
bin/certcheck --version; echo "code : $?"     # échoue : rien n'est déclaré
# suivez les étapes du scénario
dsoxlab check dependances-reproductibles
```

Le contrôle copie votre projet **sans** son `.venv`, l'installe dans un
environnement neuf à partir de ses seuls fichiers, et lance certcheck :
c'est la situation d'un collègue ou d'un pipeline qui récupère le dépôt.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
