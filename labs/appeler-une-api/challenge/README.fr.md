# Challenge : certcheck publie son ticket sans fragilité

5 tâches, 100 points, 45 minutes.

Chaque contrôle lance `bin/certcheck --publish` contre une forge factice et
compte les requêtes qu'elle reçoit. Le contrat est dans `CONTRAT.md`, section
« Publication sur la forge ».

### Tâche 1 : le jeton reste dans l'en-tête (20 pts)

Chaque requête porte `Authorization: token <jeton>` ; le jeton n'apparaît
dans aucune URL, ni sur la sortie standard, ni sur la sortie d'erreur, même
avec `--verbose` et même quand la forge est en panne.

### Tâche 2 : un seul ticket en deux exécutions (20 pts)

Deux exécutions de suite ouvrent un seul ticket, au titre exact
`certcheck : certificats à renouveler`, dont le corps cite chaque hôte à
renouveler. Un ticket qui cite seulement ce titre ne compte pas.

### Tâche 3 : la recherche parcourt toutes les pages (20 pts)

Avec plus de cent tickets ouverts et celui de certcheck au-delà de la
première page, l'outil le retrouve et n'ouvre rien.

### Tâche 4 : les pannes passagères sont reprises (20 pts)

Deux réponses 503 puis une forge rétablie : l'outil réussit, un ticket, le
code du contrôle. Une forge durablement en panne : code 3, un message sur la
sortie d'erreur, et une poignée de requêtes, pas un déluge.

### Tâche 5 : un délai maximal sur chaque requête (20 pts)

Une forge qui accepte la connexion et ne répond jamais : l'outil rend la main
de lui-même en moins de 60 secondes, avec le code 3 et un message.
