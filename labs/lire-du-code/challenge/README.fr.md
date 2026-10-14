# Challenge : lire et modifier le script certcheck

5 tâches, 100 points, 25 minutes.

Le répertoire `challenge/work` contient `certcheck.py`, son inventaire et les
certificats collectés. Les tâches 1 à 3 se notent dans `reponses.yaml` et
portent sur le script **tel que vous l'avez reçu** ; les tâches 4 et 5 se font
dans `certcheck.py`.

### Tâche 1 : ce que fait le script (20 pts)

`role` est choisi dans la liste de `reponses.yaml`, et `programme_externe`
nomme le programme que le script lance pour lire un certificat.

### Tâche 2 : ses entrées (20 pts)

`option_seuil` donne l'option qui règle le seuil d'alerte, `variable_date` la
variable d'environnement qui remplace la date du jour, et `fonction_verdict`
le nom de la fonction qui décide du verdict d'un certificat.

### Tâche 3 : ce que montre l'exécution (20 pts)

`code_de_sortie`, `hotes_en_alerte` et `hote_au_seuil` sont ceux qu'on observe
en lançant `CERTCHECK_NOW=2026-10-31 python3 certcheck.py` sur l'inventaire
fourni, avant toute modification.

### Tâche 4 : le seuil est inclusif (20 pts)

Un certificat qui expire dans exactement N jours, avec `--days N`, est affiché
`warning` et le script sort en 1 ; à N + 1 jours, il reste `ok` et le script
sort en 0. Contrôlé sur des hôtes, des seuils et des dates tirés au hasard.

### Tâche 5 : un certificat expiré est signalé (20 pts)

Un certificat dont la date est dépassée est affiché `expired`, et le script
sort en 1.

Pour faire noter : `dsoxlab check lire-du-code`.
