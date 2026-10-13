# Du script à l'outil

Deuxième lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Structurer un script en outil ». Le script hérité du lab précédent devient
un **outil** : une interface qu'on découvre par `--help`, des codes de sortie
qu'un planificateur sait lire, une sortie JSON, une configuration par
l'environnement et un mode simulation.

| | |
|---|---|
| Cible | votre poste : Python (`mise install`), Go ou Bash, au choix |
| Durée | environ 60 minutes |
| Leçon jumelée | [Structurer un script en outil](https://blog.stephane-robert.info/docs/developper/pratiques/script-en-outil/) |
| Précédent | `lire-du-code` |
| Suite | `appeler-une-api` part de la solution de référence |

```bash
dsoxlab run   script-en-outil
cd labs/script-en-outil/challenge/work
less CONTRAT.md
# écrivez votre outil, puis faites pointer bin/certcheck dessus
CERTCHECK_NOW=2031-02-20 bin/certcheck --format json; echo "code : $?"
dsoxlab check script-en-outil
```

Le contrôle ne lit jamais votre code : il lance `bin/certcheck` comme cron le
ferait, avec des inventaires et des dates tirés au hasard.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
