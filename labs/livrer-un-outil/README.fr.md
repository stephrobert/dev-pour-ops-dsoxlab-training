# Livrer un outil

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon « Livrer un
outil Python : version, étiquette, installation ». certcheck s'installe
ailleurs ; il reste à en faire une **version** : un numéro écrit à un seul
endroit, un journal des changements, une étiquette Git, et la preuve qu'on
l'installe dans un environnement neuf. Rien n'est publié : la livraison reste
dans le dépôt.

| | |
|---|---|
| Cible | votre poste : uv, Python (`mise install`) et Git |
| Durée | environ 25 minutes |
| Réseau | **requis** : l'installation neuve télécharge les dépendances depuis PyPI |
| Leçon jumelée | [Livrer un outil Python : version, étiquette, installation](https://blog.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) |
| Précédent | `dependances-reproductibles` |

```bash
dsoxlab run   livrer-un-outil
cd labs/livrer-un-outil/challenge/work
bin/certcheck --version      # certcheck 0.5.0
# suivez les étapes du scénario
dsoxlab check livrer-un-outil
```

Le contrôle installe votre projet dans un environnement neuf, puis clone
votre dépôt à l'étiquette `v1.0.0` et l'installe de même : c'est ce que fait
celui qui récupère votre version.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
