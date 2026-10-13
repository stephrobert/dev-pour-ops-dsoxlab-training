# La pull request aux tests verts

## Situation

certcheck tourne chaque nuit depuis le cron du serveur d'exploitation. Malik
propose la **pull request n°42** : purger les anciens rapports, qui ont
rempli le disque, et poster les alertes sur le webhook du chat de l'équipe.
Il a ajouté un test, la suite passe, et il vous demande une relecture avant
la fusion.

Le répertoire de travail contient le projet tel qu'il est sur `main` (le
paquet `src/certcheck/`, `pyproject.toml`, `tests/`), la description de la PR
(`pr/DESCRIPTION.md`) et son diff (`pr/0042.diff`).

## Pourquoi relire

Des tests verts ne prouvent que ce qu'ils testent. Une relecture cherche ce
qu'aucun test ne voit : un secret qui fuit, une suppression qui peut viser
le mauvais dossier, une erreur qu'on fait taire. Elle n'est utile que si
l'auteur peut agir : un fichier, une ligne, le problème, une correction.

## Étapes

### 1. Lire la description, puis le code

Lisez `pr/DESCRIPTION.md`, puis appliquez le diff dans une copie pour voir
les fichiers tels qu'ils seraient fusionnés :

```bash
cp -r . /tmp/pr42 && cd /tmp/pr42 && git apply pr/0042.diff
grep -n "" src/certcheck/maintenance.py | less
```

Vérifiez chaque affirmation de la description dans le code : « c'est géré »
se prouve ou se réfute ligne à ligne.

### 2. Chercher les quatre défauts

La PR en porte quatre, un par catégorie de la liste écrite dans
`revue.yaml` : une erreur avalée, un secret affiché, un chemin dangereux,
un test absent. Trois suffisent pour réussir. Pour chaque variable
d'environnement lue, demandez-vous ce que vaut le code quand elle est
absente.

### 3. Écrire la revue

Dans `revue.yaml` (le vrai, celui du répertoire de travail), un commentaire
par défaut : `fichier`, `ligne` (lue APRÈS le `git apply`), `categorie`,
`commentaire` et `proposition`. Puis le `verdict`.

### 4. Confier le mécanique à ruff

Un linter voit sans fatigue ce qu'une revue ne devrait pas avoir à chercher.
Ajoutez une configuration ruff au projet, par exemple dans `pyproject.toml` :

```toml
[tool.ruff]
line-length = 120
```

Lancez `uv run ruff check .` : il signale des défauts dans le code de base.
Lisez chaque ligne (code de la règle, fichier, ligne), puis `uv run ruff
check --fix .` corrige ceux marqués `[*]`. Relancez : `All checks passed!`.

### 5. Vérifier

`dsoxlab check relire-une-automatisation`.
