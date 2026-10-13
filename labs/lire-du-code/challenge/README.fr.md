# Challenge : lire le paquet certcheck

5 tâches, 100 points, 30 minutes.

Le répertoire `challenge/work` contient le projet Python hérité, son
inventaire, les certificats collectés et son historique. Vos réponses vont
dans `reponses.yaml`.

### Tâche 1 : le point d'entrée et ses modules (20 pts)

`point_d_entree` donne la fonction que lance la commande `certcheck`, sous
la forme `module:fonction` déclarée dans `[project.scripts]`, et
`modules_internes` liste exactement les modules du paquet que ce module
importe, y compris un import placé dans une fonction.

### Tâche 2 : les effets de bord (20 pts)

`sous_processus` nomme le programme lancé en sous-processus,
`fonction_appel_reseau` la fonction qui envoie la requête réseau, et
`variable_appel_reseau` la variable qui déclenche cet appel.

### Tâche 3 : l'exécution sans risque (20 pts)

`code_de_sortie` et `hote_mal_classe` sont ceux qu'on observe en lançant
`uv run certcheck` sur l'inventaire fourni, avec `CERTCHECK_NOW=2026-06-01`
et sans `FORGE_TOKEN`.

### Tâche 4 : les défauts réels (20 pts)

`defauts` cite tous les défauts réels de la liste proposée, et aucun autre.

### Tâche 5 : l'historique (20 pts)

`commit_erreur_avalee` donne l'empreinte du commit qui a introduit
`except Exception` dans `src/certcheck/certificats.py`.
