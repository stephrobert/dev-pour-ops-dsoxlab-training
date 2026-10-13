# Challenge : certcheck s'installe aussi ailleurs

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
