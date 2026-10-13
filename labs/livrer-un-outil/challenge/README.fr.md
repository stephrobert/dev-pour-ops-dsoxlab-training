# Challenge : certcheck 1.0.0, étiqueté et installable

5 tâches, 100 points, 40 minutes. Accès réseau requis (PyPI).

### Tâche 1 : une version à une seule source (20 pts)

`pyproject.toml` porte la version 1.0.0, `bin/certcheck --version` affiche
exactement `certcheck 1.0.0`, aucune chaîne `1.0.0` n'est écrite en dur sous
`src/`, et une copie dont `pyproject.toml` change de version affiche la
nouvelle sans toucher au code.

### Tâche 2 : un journal des changements daté (20 pts)

`CHANGELOG.md` porte `## [1.0.0] - AAAA-MM-JJ`, avec au moins une rubrique
(Ajouté, Modifié, Corrigé ou Added, Changed, Fixed) et une entrée, sous
`[Unreleased]` et au-dessus des versions précédentes.

### Tâche 3 : une étiquette annotée sur la bonne révision (20 pts)

Le répertoire de travail est un dépôt Git ; `v1.0.0` est une étiquette
annotée ; au commit étiqueté, `pyproject.toml` vaut 1.0.0 et `uv.lock` le
suit ; l'arbre de travail est propre.

### Tâche 4 : les artefacts construits (20 pts)

`dist/` contient `certcheck-1.0.0-py3-none-any.whl` et
`certcheck-1.0.0.tar.gz` ; la roue déclare sa version, ses dépendances et le
point d'entrée `certcheck`.

### Tâche 5 : une installation vierge depuis l'étiquette (20 pts)

Le dépôt cloné à `v1.0.0` se construit, la roue s'installe dans un
environnement neuf, `certcheck --version` y affiche `certcheck 1.0.0` et une
exécution sur un inventaire tiré au hasard rend le résultat du contrat.
