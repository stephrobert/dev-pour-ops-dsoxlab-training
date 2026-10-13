# Structurer un projet Python en outil

Deuxième lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Structurer un projet Python en outil en ligne de commande ». Le script Bash
hérité est remplacé par un **projet Python** comme un développeur le
structure : un paquet sous `src/certcheck/`, un `pyproject.toml` qui déclare
la commande `certcheck`, un `uv.lock`, et un contrat court respecté : une
interface qu'on découvre par `--help`, des codes de sortie qu'un planificateur
sait lire, une sortie JSON, un seuil réglable par l'environnement et des
erreurs sur la sortie d'erreur. Le squelette est fourni : on complète des
fonctions guidées.

| | |
|---|---|
| Cible | votre poste : uv et Python (`mise install`), openssl, aucune VM |
| Durée | environ 30 minutes |
| Leçon jumelée | [Structurer un projet Python en outil en ligne de commande](https://blog.stephane-robert.info/docs/developper/pratiques/script-en-outil/) |
| Précédent | `lire-du-code` |
| Suite | `appeler-une-api` part de la solution de référence |

```bash
dsoxlab run   script-en-outil
cd labs/script-en-outil/challenge/work
less CONTRAT.md pyproject.toml src/certcheck/certificats.py src/certcheck/cli.py
# écrivez les fonctions qui lèvent NotImplementedError, puis :
CERTCHECK_NOW=2031-02-20 bin/certcheck --format json; echo "code : $?"
dsoxlab check script-en-outil
```

Le contrôle vérifie que `bin/certcheck` lance bien le paquet du projet, puis
ne lit plus votre code : il lance `bin/certcheck` comme cron le ferait, avec
des inventaires et des dates tirés au hasard.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
