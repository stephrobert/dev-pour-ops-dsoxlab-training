# Lire le code d'une application Python

Premier lab du fil rouge de la formation **Développer pour les Ops**, jumelé à
la leçon « Lire le code d'une application Python qu'on n'a pas écrite ». Le
point de départ est la situation la plus courante d'un développeur qui arrive
dans une équipe : une application qui tourne en production, que personne
autour de lui n'a écrite, et qu'on lui demande de reprendre. Avant d'y
toucher, on la **lit** : point d'entrée déclaré par le paquet, modules
chargés, effets de bord, configuration, historique.

| | |
|---|---|
| Cible | votre poste : uv et Python (`mise install`), openssl et Git, aucune VM |
| Durée | environ 30 minutes |
| Leçon jumelée | [Lire le code d'une application Python qu'on n'a pas écrite](https://blog.stephane-robert.info/docs/developper/pratiques/lire-du-code/) |
| Suite | `script-en-outil` structure un projet Python qui respecte un contrat |

```bash
dsoxlab run   lire-du-code
cd labs/lire-du-code/challenge/work
less pyproject.toml src/certcheck/cli.py
CERTCHECK_NOW=2026-06-01 uv run certcheck --inventory inventaire.txt; echo "code : $?"
git clone historique.bundle historique
dsoxlab check lire-du-code
```

Les réponses se notent dans `reponses.yaml`. Le contrôle ne croit rien sur
parole : il relit le code, rejoue le paquet et l'historique pour recalculer
chaque réponse.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
