# Valider une politique de service en trois couches

Le pipeline de déploiement ne doit pas confondre un YAML illisible avec un
document lisible qui viole son contrat ou une règle Ops. Complétez
`validate_config.py` et `service.schema.json`.

## Contrat

`validate_config.py FICHIER` doit effectuer les contrôles dans cet ordre :

1. **Syntaxe :** analyser de façon sûre un document YAML. En cas d'erreur de
   lecture ou d'analyse, afficher un diagnostic `syntax:` et rendre un code
   non nul.
2. **Structure :** valider le document avec `service.schema.json`. Les champs
   requis sont `service` (chaîne non vide), `environment` (`staging` ou
   `production`) et `replicas` (entier de 1 à 20). Les clés inconnues sont
   rejetées. Afficher un diagnostic `structure:` avec le chemin de la
   propriété invalide.
3. **Politique :** un service en production exige au moins deux replicas.
   Afficher un diagnostic `policy:` si cette règle est violée.

Afficher `valid: FICHIER` et rendre 0 seulement si toutes les couches
passent. Ne pas afficher de trace Python pour les erreurs d'entrée.

## Étapes

1. Lancez `uv sync --frozen`.
2. Complétez le JSON Schema, avec `additionalProperties: false`.
3. Implémentez l'analyse sûre, la validation du schéma, puis la règle de
   production.
4. Essayez chaque fixture et lancez `dsoxlab check yaml-validation`.
