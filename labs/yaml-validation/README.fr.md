# Valider une politique de service YAML avant déploiement

Le pipeline de déploiement lit une politique de service YAML modifiée à la
main. Un analyseur seul ne peut pas dire si le document a la bonne structure
ou respecte les règles de l'équipe Ops.

| | |
|---|---|
| Cible | votre poste : Python 3, uv |
| Durée | environ 45 minutes |
| Réseau | requis une fois pour installer PyYAML et `jsonschema`, épinglés |
| Leçon jumelée | [Valider un fichier YAML contre un schéma](https://www.stephane-robert.info/docs/developper/autres-langages/yaml/valider-schema/) |

```bash
dsoxlab run yaml-validation
cd labs/yaml-validation/challenge/work
uv sync --frozen
uv run python validate_config.py production.yaml
uv run python validate_config.py policy-error.yaml
dsoxlab check yaml-validation
```

Le validateur distingue les erreurs de syntaxe, de structure et de politique.
Chaque fichier invalide rend un code non nul, utilisable comme garde-fou CI.
