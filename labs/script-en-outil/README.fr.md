# Comprendre un outil Python, puis le modifier

Deuxième lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Structurer un projet Python en outil en ligne de commande ». Le petit script
du lab précédent est devenu un **projet Python**, structuré comme un
développeur le fait : un paquet sous `src/certcheck/`, un `pyproject.toml` qui
déclare la commande `certcheck`, un `uv.lock`, un lanceur `bin/certcheck` et un
contrat écrit. On s'y repère d'abord, puis on comble deux écarts au contrat :
le seuil lu dans l'environnement, et les erreurs écrites sur la sortie
d'erreur.

| | |
|---|---|
| Cible | votre poste : uv et Python (`mise install`), openssl, aucune VM |
| Durée | environ 20 minutes |
| Leçon jumelée | [Structurer un projet Python en outil en ligne de commande](https://dev.stephane-robert.info/docs/developper/pratiques/script-en-outil/) |
| Précédent | `lire-du-code` |
| Suite | `dependances-reproductibles` |

```bash
dsoxlab run   script-en-outil
cd labs/script-en-outil/challenge/work
less CONTRAT.md pyproject.toml src/certcheck/cli.py
CERTCHECK_NOW=2026-06-01 bin/certcheck; echo "code : $?"
dsoxlab check script-en-outil
```

Le contrôle relit le projet livré pour recalculer vos réponses, puis lance
`bin/certcheck` comme cron le ferait, sans lire votre code.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
