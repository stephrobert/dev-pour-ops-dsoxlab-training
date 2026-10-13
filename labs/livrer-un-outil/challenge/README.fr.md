# Challenge : certcheck 1.0.0, versionné et installable

5 tâches, 100 points, 25 minutes. Accès réseau requis (PyPI).

### Tâche 1 : une version à une seule source (20 pts)

`pyproject.toml` porte la version 1.0.0, `bin/certcheck --version` affiche
exactement `certcheck 1.0.0`, aucune chaîne `1.0.0` n'est écrite en dur sous
`src/`, et une copie dont `pyproject.toml` change de version affiche la
nouvelle sans toucher au code.

### Tâche 2 : le journal des changements (20 pts)

`CHANGELOG.md` porte une section `## [1.0.0]` avec au moins une entrée
`- ...`.

### Tâche 3 : l'étiquette v1.0.0 (20 pts)

Le répertoire de travail est un dépôt Git, et l'étiquette `v1.0.0` (annotée
ou légère) désigne un commit où `pyproject.toml` vaut 1.0.0.

### Tâche 4 : installation dans un environnement neuf (20 pts)

`pip install .` du projet dans un environnement neuf réussit, et
`certcheck --version` y affiche `certcheck 1.0.0`.

### Tâche 5 : installation depuis l'étiquette (20 pts)

Le dépôt cloné à `v1.0.0` s'installe dans un environnement neuf,
`certcheck --version` y affiche `certcheck 1.0.0`, et une exécution sur un
inventaire tiré au hasard rend le résultat du contrat.
