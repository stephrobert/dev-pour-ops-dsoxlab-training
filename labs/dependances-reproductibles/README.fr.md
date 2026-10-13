# Dépendances reproductibles

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Dépendances reproductibles ». certcheck est devenu un paquet Python qui
importe `requests` et `cryptography`, mais rien ne garantit qu'il s'installe
ailleurs comme sur le poste de son auteur. Vous déclarez ses dépendances, les
verrouillez, fixez l'interpréteur, et le prouvez sur une copie propre.

| | |
|---|---|
| Cible | votre poste : uv et Python (`mise install` à la racine du catalogue) |
| Durée | environ 40 minutes |
| Réseau | **requis** : uv télécharge les paquets depuis PyPI, et l'interpréteur fixé s'il manque |
| Leçon jumelée | [Dépendances reproductibles](https://blog.stephane-robert.info/docs/developper/pratiques/dependances-reproductibles/) |
| Suite | `livrer-un-outil` part de la solution de ce lab |

```bash
dsoxlab run   dependances-reproductibles
cd labs/dependances-reproductibles/challenge/work
cat requirements.txt pyproject.toml
bin/certcheck --version; echo "code : $?"     # échoue : rien n'est déclaré
# déclarez, verrouillez, fixez, puis vérifiez comme le ferait un collègue
dsoxlab check dependances-reproductibles
```

Le contrôle copie votre projet **sans** son `.venv`, l'installe par
`uv sync --frozen` et lance certcheck sur un inventaire tiré au hasard : c'est
la situation d'un collègue ou d'un pipeline qui récupère le dépôt.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
