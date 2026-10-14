# Intervenir sur un outil qu'on n'a pas écrit

## Situation

L'équipe exploitation fait tourner chaque nuit `certcheck`, un petit outil
Python qui signale les certificats TLS à renouveler. Un ticket vient d'arriver
(`TICKET.md`) : le rapport du 31 octobre a laissé passer un certificat qui
expirait au seuil. Et la pipeline de CI est rouge depuis quelques jours ; son
dernier journal est dans `ci/run-12.log`.

Le dépôt de l'outil est livré en bundle, `depot.bundle` : clonez-le avec
`git clone depot.bundle certcheck`, et travaillez dans `certcheck/`.

## Ce qui est attendu

1. **Comprendre** l'outil et noter dans `reponses.yaml` son rôle, la commande
   qu'il déclare et l'hôte qu'il classe mal à la date du ticket.
2. **Lire** le journal de CI et l'historique : l'étape en échec, la commande
   qui la rejoue sur votre poste, le commit qui a introduit le défaut.
3. **Corriger**, en limitant le changement au défaut.
4. **Vérifier** : `uv run pytest -v` vert, `uv run ruff check .` et
   `uv run ruff format --check .` verts, et chaque étape de la CI qui repasse.

## Ce qui est noté

L'état du répertoire de travail et de `certcheck/`, jamais les commandes
tapées. L'outil est lancé comme cron le lance, sur des cas tirés au hasard, et
les étapes de la CI sont rejouées dans une copie propre. Aucun indice n'est
proposé : l'épreuve mesure ce que vous savez déjà faire. Seuil de réussite :
70 points.
