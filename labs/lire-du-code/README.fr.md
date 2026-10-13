# Lire un code qu'on n'a pas écrit

Premier lab du fil rouge de la formation **Développer pour les Ops**, jumelé
à la leçon « Lire un code qu'on n'a pas écrit ». Le point de départ est la
situation la plus courante d'un ops : un script qui tourne en production,
que personne dans l'équipe n'a écrit, et qu'on vous demande de reprendre.
Avant d'y toucher, on le **lit** : point d'entrée, commandes appelées, effets
de bord, configuration, historique.

| | |
|---|---|
| Cible | votre poste : Bash, openssl et Git, aucune VM |
| Durée | environ 30 minutes |
| Leçon jumelée | [Lire un code qu'on n'a pas écrit](https://blog.stephane-robert.info/docs/developper/pratiques/lire-du-code/) |
| Suite | `script-en-outil` transforme ce script en outil |

```bash
dsoxlab run   lire-du-code
cd labs/lire-du-code/challenge/work
less certcheck.sh
bash certcheck.sh inventaire.txt; echo "code : $?"
git clone historique.bundle historique
dsoxlab check lire-du-code
```

Les réponses se notent dans `reponses.yaml`. Le contrôle ne croit rien sur
parole : il rejoue le script et l'historique pour recalculer chaque réponse.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
