# Challenge : lire certcheck.sh

5 tâches, 100 points, 30 minutes.

Le répertoire `challenge/work` contient le script hérité, son inventaire,
les certificats collectés et son historique. Vos réponses vont dans
`reponses.yaml`.

### Tâche 1 : les commandes externes (20 pts)

`commandes_externes` liste exactement les programmes du PATH que le script
appelle, sans les commandes internes de Bash.

### Tâche 2 : les effets de bord (20 pts)

`fichier_ecrit` nomme le fichier que le script écrit, et
`variable_appel_reseau` la variable qui déclenche l'appel à la forge.

### Tâche 3 : l'exécution sans risque (20 pts)

`code_de_sortie` et `hote_mal_signale` sont ceux qu'on observe en lançant le
script sur l'inventaire fourni, sans `FORGE_TOKEN`.

### Tâche 4 : les défauts réels (20 pts)

`defauts` cite tous les défauts réels de la liste proposée, et aucun autre.

### Tâche 5 : l'historique (20 pts)

`commit_erreur_avalee` donne l'empreinte du commit qui a introduit
`2>/dev/null` sur l'appel à openssl.
