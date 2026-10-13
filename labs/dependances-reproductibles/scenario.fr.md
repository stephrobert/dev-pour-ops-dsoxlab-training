# Ça marche sur mon poste

## Situation

Un collègue a fait évoluer certcheck : la date d'expiration est lue par la
bibliothèque `cryptography`, et la publication sur la forge passe par
`requests`. Il a installé les deux à la main dans son environnement virtuel
(son `README.md` le montre), et n'a rien déclaré : `pyproject.toml` ne cite
aucune dépendance ni aucune version de Python. « Ça marche sur mon poste. »

Sur le vôtre, `bin/certcheck --version` échoue déjà.

## Pourquoi déclarer et épingler

Un **environnement virtuel** (`.venv`) isole les bibliothèques d'un projet de
celles du système. Mais il ne se partage pas : ce qui compte, ce sont les
fichiers du dépôt qui disent quoi y installer. Une bibliothèque installée à
la main n'existe que chez vous. Et une dépendance déclarée sans version
prend la dernière parue : deux postes, deux versions, deux comportements.

## Étapes

### 1. Voir l'échec

```bash
bin/certcheck --version; echo "code : $?"
```

`ModuleNotFoundError: No module named 'cryptography'` : le code l'importe,
rien ne la déclare.

### 2. Déclarer les deux dépendances

Avec uv, une commande écrit la dépendance dans `pyproject.toml` et
l'installe dans `.venv` :

```bash
uv add requests cryptography
```

Regardez `pyproject.toml` : une section `dependencies` est apparue. Un
fichier `uv.lock` aussi.

### 3. Épingler les versions

Ouvrez `uv.lock` : il fige la version **exacte** de chaque paquet, y compris
ceux dont `requests` a besoin (`urllib3`, `idna`...). Ce verrou se versionne
avec le code : un collègue qui lance `uv sync` obtient exactement les mêmes
versions. Sans uv, l'équivalent est un `requirements.txt` dont chaque ligne
porte `==` (`requests==2.34.2`).

### 4. Noter la version de Python

Dans `pyproject.toml`, section `[project]`, ajoutez
`requires-python = ">=3.12"` : la plus ancienne version supportée. Vous
pouvez aussi fixer celle du projet par `uv python pin 3.14`, qui écrit
`.python-version`. Relancez `uv lock` après avoir modifié `pyproject.toml`.

### 5. Vérifier comme un collègue

Dans une copie sans `.venv`, l'outil doit s'installer depuis les fichiers
seuls :

```bash
rsync -a --exclude .venv ./ /tmp/essai/ && cd /tmp/essai
uv sync && uv run certcheck --version
```

Puis `dsoxlab check dependances-reproductibles`.
