# Livrer un outil interne

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Livrer un outil ». certcheck s'installe à l'identique ailleurs ; il reste à
en faire une **version** : un numéro à une seule source, un journal des
changements, une étiquette Git, des artefacts construits, et la preuve qu'on
l'installe à partir de l'étiquette seule.

| | |
|---|---|
| Cible | votre poste : uv, Python (`mise install`) et Git |
| Durée | environ 40 minutes |
| Réseau | **requis** : l'installation vierge télécharge les dépendances depuis PyPI (uv construit avec son backend `uv_build` intégré) |
| Leçon jumelée | [Livrer un outil](https://blog.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) |
| Précédent | `dependances-reproductibles`, dont la solution est le point de départ |

```bash
dsoxlab run   livrer-un-outil
cd labs/livrer-un-outil/challenge/work
git init                     # le répertoire de travail n'est pas encore un dépôt
bin/certcheck --version
# version, journal, commit, étiquette, construction
dsoxlab check livrer-un-outil
```

Le contrôle clone votre dépôt à l'étiquette `v1.0.0` dans un dossier
temporaire, y construit la roue, l'installe dans un environnement neuf et
lance certcheck : c'est ce que fait celui qui installe votre version.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
