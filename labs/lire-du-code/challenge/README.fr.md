# Le script que personne n'a écrit

## Situation

Chaque nuit, cron lance `certcheck.py` pour contrôler l'expiration des
certificats TLS du parc. Julien l'a écrit il y a deux ans, puis il a changé
d'équipe. Le mois dernier, le certificat d'un hôte a expiré alors que le
rapport de la veille le disait `ok`. On vous confie le script.

Le répertoire de travail contient le script (`certcheck.py`, environ quatre-vingts
lignes), l'inventaire qu'il lit (`inventaire.txt`) et les certificats collectés
sur les hôtes (`certs/`).

## Objectif

D'abord **comprendre** le script tel que vous l'avez reçu, et le noter dans
`reponses.yaml` : son rôle, ses entrées, la fonction qui décide, ce qu'il
affiche et son code de sortie. Ensuite seulement, le **modifier** :

1. un certificat qui expire **exactement** au seuil doit passer en `warning` ;
2. un certificat **déjà expiré** doit afficher `expired`, et non `warning`.

## Repères

- Lisez du bas vers le haut : `if __name__ == "__main__"` appelle `main()`,
  et `main()` appelle les autres fonctions.
- `python3 certcheck.py --help` liste les options sans rien exécuter d'autre.
- Le script ne fait que **lire** : il lance `openssl` sur chaque certificat et
  affiche une ligne par hôte. Le lancer ne modifie rien.
- `CERTCHECK_NOW=2026-10-31 python3 certcheck.py` rejoue le contrôle comme si
  l'on était le 31 octobre 2026 ; `echo "code : $?"` affiche ensuite son code
  de sortie.
- Une condition se change d'un caractère : `<` et `<=` ne disent pas la même
  chose à la frontière.

## Lire et modifier le script certcheck

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
