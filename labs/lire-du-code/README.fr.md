# Lire et modifier un petit script Python

Premier lab du fil rouge de la formation **Développer pour les Ops**, jumelé à
la leçon « Lire et modifier le code Python qu'on n'a pas écrit ». Le point de
départ est la situation la plus courante d'un Ops : un script qui tourne chaque
nuit, que personne autour de lui n'a écrit, et qu'on lui demande de corriger.
Avant d'y toucher, on le **lit** : son rôle, ses entrées, la fonction qui
décide, ce qu'il affiche et son code de sortie. Ensuite seulement, on change
une condition.

| | |
|---|---|
| Cible | votre poste : Python 3 et openssl, aucune VM |
| Durée | environ 25 minutes |
| Leçon jumelée | [Lire et modifier le code Python qu'on n'a pas écrit](https://www.stephane-robert.info/docs/developper/pratiques/lire-du-code/) |
| Suite | `script-en-outil` montre le même outil devenu un projet Python |

```bash
dsoxlab run   lire-du-code
cd labs/lire-du-code/challenge/work
less certcheck.py
python3 certcheck.py --help
CERTCHECK_NOW=2026-10-31 python3 certcheck.py; echo "code : $?"
dsoxlab check lire-du-code
```

Les réponses se notent dans `reponses.yaml`. Le contrôle ne croit rien sur
parole : il rejoue le script reçu pour recalculer chaque réponse, puis lance
votre version sur des inventaires et des dates tirés au hasard.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
