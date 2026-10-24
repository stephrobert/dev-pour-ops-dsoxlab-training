# Écrire le contrat de déploiement

La commande de déploiement `fleetctl` doit rejeter une demande mal formée
avant de modifier un service. `deployment.schema.json` est volontairement trop
permissif. Complétez-le avec JSON Schema draft 2020-12.

## Contrat

Un document de déploiement porte exactement ces propriétés à la racine :

- `service` : une chaîne non vide ;
- `version` : une chaîne de forme version sémantique (`majeur.mineur.patch`) ;
- `environment` : une valeur parmi `development`, `staging`, `production` ;
- `replicas` : un entier de 1 à 20 ;
- `strategy` : un objet avec `type` requis (`rolling` ou `canary`) et
  `max_unavailable` facultatif entre 0 et 5.

Chaque objet rejette les propriétés supplémentaires. `validate.py FICHIER`
affiche `valid: FICHIER` et rend 0 si le document est valide. Un JSON ou des
données invalides rendent un code non nul, avec un message lisible et un
chemin JSON pour les erreurs de validation des données.
Respectez la grammaire RFC 8259 : rejetez `NaN`, `Infinity` et les clés
d'objet dupliquées au lieu de les accepter ou de les écraser silencieusement.

## Étapes

1. Installez la dépendance épinglée : `uv sync --frozen`.
2. Ajoutez les champs requis, types, limites, énumérations et
   `additionalProperties`.
3. Vérifiez les exemples invalides pour la grammaire JSON et le schéma, puis
   confirmez que l'entrée valide passe toujours.
4. Lancez `dsoxlab check json-schema`.
