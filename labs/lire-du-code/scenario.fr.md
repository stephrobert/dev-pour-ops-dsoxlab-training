# L'application que personne n'a écrite

## Situation

Chaque nuit, la commande `certcheck` contrôle l'expiration des certificats
TLS du parc. C'est un paquet Python : Julien l'a structuré en 2024, Karim
l'a complété, et tous deux ont changé d'équipe. Le mois dernier, un
certificat a expiré sans qu'aucune alerte ne parte : on vous confie le code.

Le répertoire de travail contient le projet (`pyproject.toml`, `uv.lock`,
le paquet sous `src/certcheck/`), l'inventaire qu'il lit, les certificats
collectés sur les hôtes (`certs/`), et son historique Git sous forme de
bundle (`historique.bundle`).

## Objectif

Comprendre ce que fait l'application **avant** de la modifier, et le prouver
dans `reponses.yaml` : son point d'entrée et les modules qu'il charge, ses
effets de bord, ce que son exécution montre, ses défauts réels, et le commit
qui a commencé à avaler les erreurs.

## Repères

- Une commande installée par un paquet Python ne commence pas forcément
  dans une fonction `main` : `pyproject.toml` la déclare dans
  `[project.scripts]`, sous la forme `module:fonction`.
- Lisez du point d'entrée vers les fonctions qu'il appelle, en ouvrant
  chaque module importé. Un import peut se cacher dans une fonction.
- Exécuter sans risque : sans `FORGE_TOKEN`, certcheck n'appelle pas la
  forge, et `CERTCHECK_NOW` fixe la date du jour.
- `git log -S '<chaîne>'` trouve les commits qui ont ajouté ou retiré une
  chaîne ; `git blame` dit qui a écrit chaque ligne actuelle.
