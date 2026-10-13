# Épreuve : reprendre un outil d'exploitation

Cette épreuve clôt la formation **Développer pour les Ops**. Ce n'est pas un
cours : elle mesure, sur une situation neuve, ce que le fil rouge a
travaillé, de la lecture du script hérité à la livraison d'une version.

| | |
|---|---|
| Cible | votre poste : Bash, Python ou Go, au choix (`mise install`), plus Git, make et openssl |
| Durée | environ 120 minutes |
| Seuil de réussite | 70 points sur 100 |
| Indices | aucun |
| Parcours | [Développer pour les Ops](https://blog.stephane-robert.info/docs/developper/parcours/) |

| Tâche | Ce qui est vérifié |
|---|---|
| Le contrat | interface, codes 0, 1 et 2, JSON, configuration, tabulations, CRLF, jour à un chiffre, certificat absent en 2, sur des tirages au hasard |
| La publication | jeton en en-tête et jamais dans l'URL, idempotence, pagination, reprise sur 503, délai maximal face à une forge muette (code 3 en moins de 60 s) |
| Vos tests | `./test.sh` passe contre votre outil et contre la référence, et échoue contre une variante qui reproduit le défaut hérité |
| La livraison | étiquette annotée, CHANGELOG, verrou des versions, `make install` depuis un clone de l'étiquette |
| La revue | au moins quatre des cinq défauts de la PR n°57, commentaires actionnables, verdict |

```bash
dsoxlab run   level-exams-outil
cd labs/level-exams/outil/challenge/work
dsoxlab challenge level-exams-outil
# ... votre travail ...
dsoxlab check level-exams-outil
```

`CHOIX.md` n'est pas noté par le contrôle : il se juge sur la grille
d'auto-évaluation qu'il contient.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
