# La 1.0.0

## Situation

certcheck déclare ses dépendances et les verrouille dans `uv.lock` : il
s'installe sur n'importe quel poste. L'équipe veut maintenant le livrer aux
autres équipes, en version **1.0.0**.

Deux choses gênent. La version est écrite **deux fois** : dans
`pyproject.toml` et en dur dans `src/certcheck/__init__.py`. Et le projet
n'est pas encore sous Git. `CHANGELOG.md` ne porte qu'une section
`## [Unreleased]`.

## Pourquoi versionner

Une version est un nom stable pour un état du code : « la 1.0.0 », que
l'équipe d'astreinte peut installer, citer dans un ticket, ou réinstaller
dans six mois. Elle s'écrit à **un seul endroit**, sinon deux fichiers
finissent par dire deux numéros. Le journal des changements dit ce qui
change ; l'étiquette Git marque le commit exact qui porte cette version.

## Étapes

### 1. Une seule source pour la version

Dans `pyproject.toml`, passez `version` à `"1.0.0"`. Dans
`src/certcheck/__init__.py`, remplacez la chaîne en dur par une lecture des
métadonnées du paquet installé :

```python
from importlib.metadata import version

__version__ = version("certcheck")
```

`bin/certcheck --version` doit afficher `certcheck 1.0.0`.

### 2. Le journal des changements

Dans `CHANGELOG.md`, gardez `## [Unreleased]` en tête (vide), et placez
juste dessous une section `## [1.0.0] - AAAA-MM-JJ` (la date du jour) qui
reprend les entrées.

### 3. Le dépôt et l'étiquette

Le répertoire de travail vit dans le dépôt du catalogue : il faut SON propre
dépôt, sinon Git remonterait à celui du catalogue.

```bash
git init
git add -A
git commit -m "certcheck 1.0.0"
git tag -a v1.0.0 -m "certcheck 1.0.0"
```

`.gitignore` exclut déjà `.venv/` et `dist/`. L'étiquette se pose **après**
le commit qui contient la 1.0.0.

### 4. Installer dans un environnement neuf

```bash
python3 -m venv /tmp/essai-env
/tmp/essai-env/bin/pip install .
/tmp/essai-env/bin/certcheck --version
```

### 5. Installer depuis l'étiquette

```bash
git clone --branch v1.0.0 . /tmp/essai-clone
python3 -m venv /tmp/essai-env2
/tmp/essai-env2/bin/pip install /tmp/essai-clone
/tmp/essai-env2/bin/certcheck --version
```

Puis `dsoxlab check livrer-un-outil`.

## Hors de ce lab

Publier une roue sur un index, construire une image de conteneur ou livrer
par un pipeline relèvent d'autres formations : ici, la version reste dans le
dépôt.
