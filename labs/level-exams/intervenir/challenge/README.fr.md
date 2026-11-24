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
2. **Lire** le journal de CI et le code : l'étape en échec, la commande
   qui la rejoue sur votre poste, le fichier où se trouve le défaut.
3. **Corriger**, en limitant le changement au défaut.
4. **Vérifier** : `uv run pytest -v` vert, `uv run ruff check .` et
   `uv run ruff format --check .` verts, et chaque étape de la CI qui repasse.

## Ce qui est noté

L'état du répertoire de travail et de `certcheck/`, jamais les commandes
tapées. L'outil est lancé comme cron le lance, sur des cas tirés au hasard, et
les étapes de la CI sont rejouées dans une copie propre. Aucun indice n'est
proposé : l'épreuve mesure ce que vous savez déjà faire. Seuil de réussite :
70 points.

## Épreuve : intervenir sur un petit outil d'exploitation

5 tâches, 100 points, 45 minutes. Seuil de réussite : 70 points.

Aucun indice n'est proposé. Clonez d'abord le dépôt :
`git clone depot.bundle certcheck`. Les tâches 1 et 2 se notent dans
`reponses.yaml` et portent sur le dépôt **reçu** ; les tâches 3 à 5 portent
sur `certcheck/`.

### Tâche 1 : l'outil est compris (20 pts)

`role`, `commande_declaree` et `hote_mal_classe` décrivent l'outil reçu.

### Tâche 2 : la CI est lue et le défaut localisé (20 pts)

`etape_en_echec` nomme l'étape rouge de `ci/run-12.log` comme `ci.yml` la
nomme, `commande_locale` la rejoue sur votre poste, et `fichier_du_defaut`
désigne le fichier où se trouve le défaut du ticket.

### Tâche 3 : le défaut est corrigé (20 pts)

`bin/certcheck` respecte la décision du contrat (seuil inclusif, expiré,
codes de sortie) sur des hôtes, des seuils et des dates tirés au hasard.

### Tâche 4 : les tests sont verts, et complets (20 pts)

`uv run pytest` est vert, les cinq tests reçus sont toujours là, et ces tests, rejoués tels que reçus contre votre code, passent : modifier un test ne corrige rien.

### Tâche 5 : la qualité et la CI passent (20 pts)

Chaque étape `run:` du `ci.yml` reçu (dépendances, qualité, tests, paquet)
passe, rejouée dans une copie propre de `certcheck/`.

Pour faire noter : `dsoxlab check level-exams-intervenir`.
