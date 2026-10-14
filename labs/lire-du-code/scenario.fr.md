# Le script que personne n'a écrit

## Situation

Chaque nuit, cron lance `certcheck.py` pour contrôler l'expiration des
certificats TLS du parc. Julien l'a écrit il y a deux ans, puis il a changé
d'équipe. Le mois dernier, le certificat d'un hôte a expiré alors que le
rapport de la veille le disait `ok`. On vous confie le script.

Le répertoire de travail contient le script (`certcheck.py`, une soixantaine de
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
