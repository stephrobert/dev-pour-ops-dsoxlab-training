# Normaliser l'inventaire de services

L'équipe plateforme consomme un inventaire unique fourni par des outils qui
émettent du JSON ou du YAML. Elle veut un fichier JSON prévisible pour
l'étape suivante du pipeline de déploiement.

## Contrat

`go run . [--output CHEMIN] ENTREE` doit :

- lire du JSON ou du YAML selon l'extension du fichier ;
- exiger une liste `services` à la racine, avec `id`, `environment`,
  `replicas` et `expires` pour chaque enregistrement ;
- supprimer les espaces et mettre `id` et `environment` en minuscules,
  analyser `expires` comme une date, et exiger un entier positif pour
  `replicas` (pas un booléen) ;
- trier les enregistrements par `id` normalisé, conserver un ordre stable
  des champs JSON et écrire du JSON UTF-8 terminé par un saut de ligne ;
- rejeter une entrée mal formée ou invalide avec un message utile et un code
  de sortie non nul, sans créer ni remplacer le fichier de sortie demandé.

## Étapes

1. Au premier lancement, laissez Go télécharger le module YAML épinglé.
2. Obtenez les mêmes données normalisées avec les fixtures YAML et JSON.
3. Essayez un nombre de replicas invalide et une extension de fichier non prise en charge.
4. Créez au préalable un fichier de sortie et vérifiez qu'une conversion
   échouée ne le modifie pas.
5. Lancez `dsoxlab check data-json-yaml`.
