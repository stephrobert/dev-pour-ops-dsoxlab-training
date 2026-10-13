# Le script que personne n'a écrit

## Situation

Chaque nuit, `certcheck.sh` contrôle l'expiration des certificats TLS du
parc. Julien l'a écrit en 2024, Karim l'a complété, et tous deux ont changé
d'équipe. Le mois dernier, un certificat a expiré sans qu'aucune alerte ne
parte : on vous confie le script.

Le répertoire de travail contient le script, l'inventaire qu'il lit, les
certificats collectés sur les hôtes (`certs/`), et son historique Git sous
forme de bundle (`historique.bundle`).

## Objectif

Comprendre ce que fait le script **avant** de le modifier, et le prouver dans
`reponses.yaml` : ses commandes externes, ses effets de bord, ce que son
exécution montre, ses défauts réels, et le commit qui a commencé à masquer
les erreurs.

## Repères

- Lisez du point d'entrée (le code hors fonctions, en bas) vers les fonctions
  qu'il appelle.
- `type -t <mot>` dit si un mot est une commande interne de Bash, un mot-clé
  ou un programme du PATH.
- Exécuter sans risque : sans `FORGE_TOKEN`, le script n'appelle pas la forge.
  Il écrit tout de même un fichier : lequel ?
- `git log -S '<chaîne>'` trouve les commits qui ont ajouté ou retiré une
  chaîne ; `git blame` dit qui a écrit chaque ligne actuelle.
