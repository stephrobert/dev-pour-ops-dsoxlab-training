# Challenge : certcheck s'installe à l'identique ailleurs

5 tâches, 100 points, 40 minutes. Accès réseau requis (PyPI).

Le contrôle lit les fichiers du projet, puis l'installe dans une **copie
propre**, sans `.venv`, comme le ferait un collègue ou un pipeline.

### Tâche 1 : des dépendances déclarées (20 pts)

`pyproject.toml` déclare `requests` et `cryptography` dans
`[project] dependencies`, chacune avec une borne basse (`>=` ou `~=`), et
porte un `requires-python`.

### Tâche 2 : un verrou à jour (20 pts)

`uv.lock` existe, fige `requests` et `cryptography`, et `uv lock --check`
l'accepte : il correspond à `pyproject.toml`.

### Tâche 3 : un interpréteur fixé (20 pts)

`.python-version` (ou `mise.toml`) porte une version précise `X.Y.Z`,
comprise dans `requires-python`.

### Tâche 4 : reproductible ailleurs (20 pts)

Dans une copie sans `.venv`, `uv sync --frozen` réussit, puis
`uv run certcheck --version` et une exécution sur un inventaire tiré au
hasard, avec `CERTCHECK_NOW`, rendent le résultat du contrat.

### Tâche 5 : une seule source de vérité (20 pts)

`requirements.txt` est supprimé ou, s'il est gardé, généré depuis le verrou :
chaque ligne en `==`, avec ses empreintes `--hash`, aux versions de
`uv.lock`.
