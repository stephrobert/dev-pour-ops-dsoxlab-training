# La pull request aux tests verts

## Situation

certcheck tourne chaque nuit depuis le cron du serveur d'exploitation. Malik
propose la **pull request n°42** : purger les anciens rapports, qui ont rempli
le disque, et poster les alertes sur le webhook du chat de l'équipe. Il a
ajouté des tests, ils passent, et il vous demande une relecture avant la
fusion.

Le répertoire de travail contient le projet tel qu'il est sur `main`
(`certcheck.py`, `pyproject.toml`, `tests/`), la description de la PR
(`pr/DESCRIPTION.md`) et son diff (`pr/0042.diff`).

## Objectif

Rendre une revue que Malik peut appliquer sans vous redemander quoi que ce
soit, dans `revue.yaml` : chaque vrai défaut signalé dans le bon fichier, à
la bonne ligne, dans la bonne catégorie, avec une correction concrète, puis
un verdict. Ajoutez enfin au projet un `.pre-commit-config.yaml` qui
refusera au commit les défauts qu'une machine sait voir, pour que la
prochaine revue porte sur l'essentiel.

## Repères

- Lisez la description d'abord, puis vérifiez chaque affirmation dans le
  code : « c'est contourné », « c'est géré » et « tests ajoutés » se
  prouvent ou se réfutent ligne à ligne.
- `git apply pr/0042.diff` dans une copie du projet donne les fichiers tels
  qu'ils seraient fusionnés ; les numéros de ligne de la revue sont ceux-là,
  pas ceux du diff.
- Pour chaque variable d'environnement lue, demandez-vous ce que vaut le code
  quand elle est absente.
- `git ls-remote <dépôt> 'refs/tags/<tag>*'` donne l'empreinte du commit
  d'un tag sans rien cloner. `pre-commit autoupdate --freeze` fait de même
  pour toute une configuration.
