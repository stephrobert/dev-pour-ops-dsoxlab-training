# Épreuve : reprendre un outil d'exploitation

Cette épreuve clôt la formation **Développer pour les Ops**. Ce n'est pas un
cours : elle mesure, sur une situation neuve, les gestes de base que le fil
rouge a travaillés, de la lecture d'un code hérité à la livraison d'une
version d'un projet Python.

| | |
|---|---|
| Cible | votre poste : uv et Python (`mise install`), plus Git et openssl |
| Durée | environ 60 minutes |
| Seuil de réussite | 70 points sur 100 |
| Indices | aucun |
| Parcours | [Développer pour les Ops](https://blog.stephane-robert.info/docs/developper/parcours/) |
| Leçon jumelée | [Livrer un outil Python : version, étiquette, installation](https://blog.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) |

| Tâche | Ce qui est vérifié |
|---|---|
| Le contrat | interface, codes 0, 1 et 2, JSON, seuil par `CERTCHECK_DAYS`, tabulations, jour à un chiffre, certificat absent en 2, sur des tirages au hasard |
| Vos tests | `uv run pytest tests` passe contre votre outil (3 tests au moins) et contre la référence, et échoue contre une variante qui reproduit le bogue hérité |
| L'installation | `pyproject.toml` et paquet sous `src/`, dépendances de développement épinglées, installation dans un environnement neuf, `certcheck --version` |
| La version | une étiquette `vX.Y.Z`, la section `## [X.Y.Z]` du CHANGELOG et la version de `pyproject.toml` au commit étiqueté |
| La revue | au moins trois des quatre défauts de la PR n°57, commentaires actionnables, verdict |

```bash
dsoxlab run   level-exams-outil
cd labs/level-exams/outil/challenge/work
dsoxlab challenge level-exams-outil
# ... votre travail ...
dsoxlab check level-exams-outil
```

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
