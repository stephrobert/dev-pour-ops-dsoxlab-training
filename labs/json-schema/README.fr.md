# Imposer un contrat de déploiement avec JSON Schema

Un outil de déploiement consomme du JSON modifié par plusieurs équipes.
Appliquez la grammaire JSON stricte ainsi qu'un contrat JSON Schema, pour
rejeter les données ambiguës ou inattendues avant le déploiement.

| | |
|---|---|
| Cible | votre poste : Python 3, uv |
| Durée | environ 45 minutes |
| Réseau | requis une fois pour installer la dépendance `jsonschema` épinglée |
| Leçon jumelée | [Écrire un JSON Schema](https://www.stephane-robert.info/docs/developper/autres-langages/json/ecrire-un-schema/) |

```bash
dsoxlab run json-schema
cd labs/json-schema/challenge/work
uv sync --frozen
uv run python validate.py valid.json
uv run python validate.py invalid-extra.json
dsoxlab check json-schema
```

Le contrôle essaie l'analyse JSON stricte, une entrée valide, des champs
manquants, des types incorrects, des champs inconnus et les chemins JSON des
erreurs. Il évalue le comportement, pas la mise en forme du schéma.
