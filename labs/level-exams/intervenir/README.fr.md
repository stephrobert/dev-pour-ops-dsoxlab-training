# Épreuve : intervenir sur un petit outil d'exploitation

Épreuve de fin du niveau o1 de **Développer pour les Ops** : une mesure, pas
un cours. Un petit outil Python, une modification récente qui a introduit un
défaut, un run de CI rouge. Vous lisez le code, l'historique et le journal de
CI, faites une correction limitée et rendez tests, qualité et CI verts.

| | |
|---|---|
| Cible | votre poste : uv et Python (`mise install`), openssl et Git, aucune VM |
| Durée | environ 45 minutes, seuil 70 points, sans indice |
| Page de l'épreuve | [Épreuve : intervenir sur un petit outil d'exploitation](https://blog.stephane-robert.info/docs/developper/pratiques/epreuve-intervenir/) |

```bash
dsoxlab run   level-exams-intervenir
cd labs/level-exams/intervenir/challenge/work
git clone depot.bundle certcheck
less TICKET.md ci/run-12.log
dsoxlab check level-exams-intervenir
```

Ce que la réussite prouve : intervenir sur un petit projet Python accompagné.
Ce qu'elle ne prouve pas : écrire un outil, une pipeline ou une version, ni
l'autonomie d'un développeur Python.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
