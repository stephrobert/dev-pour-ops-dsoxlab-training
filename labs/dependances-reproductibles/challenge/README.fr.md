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

## Certcheck s'installe aussi ailleurs

5 tâches, 100 points, 25 minutes. Accès réseau requis (PyPI).

Le contrôle lit les fichiers du projet, puis l'installe dans un
**environnement neuf**, sans votre `.venv` : par `uv sync --frozen` s'il
trouve un `uv.lock`, sinon par `pip install -r requirements.txt` (s'il
existe) puis `pip install .`.

### Tâche 1 : les dépendances sont déclarées (20 pts)

`requests` et `cryptography` sont déclarées, dans `pyproject.toml`
(`[project] dependencies`) ou dans `requirements.txt`.

### Tâche 2 : les versions sont épinglées (20 pts)

Chacune porte une version exacte (`==`), ou un `uv.lock` fige les deux.

### Tâche 3 : la version de Python est notée (20 pts)

`pyproject.toml` porte un `requires-python`, ou le projet a un fichier
`.python-version`.

### Tâche 4 : installation dans un environnement neuf (20 pts)

Installé depuis les seuls fichiers du projet, `certcheck --version` affiche
`certcheck 0.5.0`.

### Tâche 5 : rien d'installé à la main (20 pts)

Dans ce même environnement neuf, certcheck analyse un parc et publie son
ticket sur une forge factice : tout ce qu'il importe, `requests` compris,
vient des fichiers du projet.
