# Épreuve : intervenir sur un petit outil d'exploitation

5 tâches, 100 points, 45 minutes. Seuil de réussite : 70 points.

Aucun indice n'est proposé. Clonez d'abord le dépôt :
`git clone depot.bundle certcheck`. Les tâches 1 et 2 se notent dans
`reponses.yaml` et portent sur le dépôt **reçu** ; les tâches 3 à 5 portent
sur `certcheck/`.

### Tâche 1 : l'outil est compris (20 pts)

`role`, `commande_declaree` et `hote_mal_classe` décrivent l'outil reçu.

### Tâche 2 : la CI et l'historique sont lus (20 pts)

`etape_en_echec` nomme l'étape rouge de `ci/run-12.log` comme `ci.yml` la
nomme, `commande_locale` la rejoue sur votre poste, et `commit_fautif` désigne
le commit qui a introduit le défaut.

### Tâche 3 : le défaut est corrigé (20 pts)

`bin/certcheck` respecte la décision du contrat (seuil inclusif, expiré,
codes de sortie) sur des hôtes, des seuils et des dates tirés au hasard.

### Tâche 4 : les tests sont verts, et complets (20 pts)

`uv run pytest` est vert, et les cinq tests reçus sont toujours là.

### Tâche 5 : la qualité et la CI passent (20 pts)

Chaque étape `run:` du `ci.yml` reçu (dépendances, qualité, tests, paquet)
passe, rejouée dans une copie propre de `certcheck/`.

Pour faire noter : `dsoxlab check level-exams-intervenir`.
