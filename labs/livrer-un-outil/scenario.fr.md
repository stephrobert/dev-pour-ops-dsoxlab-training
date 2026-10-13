# La 1.0.0

## Situation

certcheck déclare ses dépendances, les verrouille dans `uv.lock` et fixe son
interpréteur : il s'installe à l'identique sur n'importe quel poste. L'équipe
veut maintenant le **livrer** aux autres équipes, en version 1.0.0.

Le point de départ est la solution du lab précédent, avec deux différences :
le projet n'est pas encore sous Git (à vous le `git init` et les commits), et
`CHANGELOG.md`, au format Keep a Changelog, ne porte qu'une section
`## [Unreleased]`. La version, elle, est écrite deux fois : dans
`pyproject.toml` et en dur dans `src/certcheck/__init__.py`.

## Objectif

1. La version 1.0.0 n'a qu'une source, `pyproject.toml` ; `certcheck
   --version` affiche `certcheck 1.0.0` en la lisant dans les métadonnées du
   paquet installé.
2. `CHANGELOG.md` porte une section `## [1.0.0] - AAAA-MM-JJ` non vide, sous
   `[Unreleased]` et au-dessus des versions précédentes.
3. Une étiquette Git **annotée** `v1.0.0` désigne le commit qui porte la
   1.0.0, et l'arbre de travail est propre.
4. `dist/` contient la roue et le sdist de la 1.0.0, construits par `uv build`.
5. Un environnement vierge installe la roue construite depuis l'étiquette, et
   certcheck y tourne.

## Repères

- Le répertoire de travail est rangé dans le dépôt du catalogue : sans
  `git init` ici, Git remonterait au dépôt du catalogue.
- `importlib.metadata.version("certcheck")` lit la version du paquet
  installé ; une roue n'emporte pas `pyproject.toml`.
- Le verrou enregistre aussi la version du projet : après avoir changé
  `pyproject.toml`, relancez `uv lock` avant de committer.
- La roue Python n'est qu'une des formes de livraison vues dans la leçon. Le
  binaire Go statique et l'image de conteneur en sont deux autres ; elles
  restent hors de ce lab.
- Ce lab demande un accès au réseau : uv télécharge depuis PyPI.
