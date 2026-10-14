# Challenge : comprendre certcheck, puis le modifier

5 tâches, 100 points, 20 minutes.

Le répertoire `challenge/work` contient le projet Python certcheck et son
contrat, `CONTRAT.md`. Les tâches 1 à 3 se notent dans `reponses.yaml` et
portent sur le projet **tel que vous l'avez reçu** ; les tâches 4 et 5 se font
dans `src/certcheck/cli.py`.

### Tâche 1 : la commande est déclarée par le projet (20 pts)

`fichier_declaration` nomme le fichier qui déclare la commande `certcheck`, et
`commande_declaree` recopie ce qu'il déclare, sous la forme `module:fonction`.

### Tâche 2 : où est quoi (20 pts)

`module_decision` donne le fichier qui contient la fonction `statut`, et
`lanceur` le fichier que cron ou un pipeline lance, chemins depuis le
répertoire de travail.

### Tâche 3 : les codes de sortie observés (20 pts)

Les trois codes de `reponses.yaml` sont ceux qu'on observe en lançant les
commandes indiquées sur le projet reçu.

### Tâche 4 : le seuil vient de l'environnement (20 pts)

`CERTCHECK_DAYS` règle le seuil quand `--days` est absent, `--days` l'emporte
sur la variable, et une valeur qui n'est pas un entier positif rend 2, avec un
message sur la sortie d'erreur.

### Tâche 5 : les erreurs vont sur la sortie d'erreur (20 pts)

Un inventaire absent rend 2, avec un message d'une ligne sur la sortie
d'erreur, ni trace Python ni rien sur la sortie standard. Un certificat absent
reste dans le JSON en `error`, et son hôte est nommé sur la sortie d'erreur.

Pour faire noter : `dsoxlab check script-en-outil`.
