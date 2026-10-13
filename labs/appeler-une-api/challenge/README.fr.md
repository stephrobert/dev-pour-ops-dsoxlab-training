# Challenge : certcheck ouvre son ticket avec requests

5 tâches, 100 points, 30 minutes. Accès réseau requis une fois (PyPI).

Chaque contrôle lance `bin/certcheck --publish` contre une forge factice et
regarde les requêtes qu'elle reçoit.

### Tâche 1 : requests déclaré, jeton dans l'en-tête (20 pts)

`pyproject.toml` déclare `requests` à une version exacte (`==`), et c'est
lui qui appelle la forge (User-Agent `python-requests/<cette version>`).
Chaque requête porte `Authorization: token <jeton>` ; le jeton n'apparaît
ni dans une URL, ni sur une sortie, même avec `--verbose`.

### Tâche 2 : un délai maximal (20 pts)

Une forge qui accepte la connexion et ne répond jamais : l'outil rend la main
de lui-même, avec le code 3 et un message sur la sortie d'erreur.

### Tâche 3 : une erreur HTTP donne le code 3 (20 pts)

Un jeton refusé (401) ou une forge en panne (503) : code 3, et un message
sur la sortie d'erreur qui cite le code HTTP, sans le jeton.

### Tâche 4 : le ticket est créé avec le bon titre (20 pts)

Des certificats sont à renouveler : un seul ticket est créé, au titre exact
`certcheck : certificats à renouveler`, dont le corps cite chaque hôte, et
le code de sortie reste celui du contrôle.

### Tâche 5 : pas de doublon (20 pts)

Un ticket ouvert porte déjà ce titre, sur la première page de la liste :
l'outil lit la liste, ne crée rien, et garde le code du contrôle.
