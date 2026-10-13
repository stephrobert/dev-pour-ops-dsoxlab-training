# Ça marche sur mon poste

## Situation

Un collègue a fait évoluer certcheck. La date d'expiration est maintenant lue
par la bibliothèque `cryptography` (plus d'appel à `openssl`), et la
publication sur la forge passe par `requests`. Il en a fait un paquet :
`src/certcheck/`, un point d'entrée `certcheck` déclaré dans
`[project.scripts]`, la version 0.5.0.

Ses dépendances, elles, sont restées dans un `requirements.txt` qu'il a
installé à la main dans son environnement virtuel : deux noms, sans aucune
version. `pyproject.toml` n'en déclare aucune, ne dit pas quelles versions de
Python sont supportées, il n'y a pas de verrou, et rien ne dit quel
interpréteur utiliser. « Ça marche sur mon poste. »

Sur le vôtre, `bin/certcheck --version` échoue déjà.

## Objectif

Que n'importe qui, à partir du dépôt seul, obtienne exactement le même outil :

1. `pyproject.toml` déclare `requests` et `cryptography` (avec une borne basse)
   et un `requires-python` ;
2. un `uv.lock` existe et correspond à `pyproject.toml` ;
3. l'interpréteur est fixé à une version précise, compatible avec
   `requires-python` ;
4. une copie propre, sans `.venv`, s'installe par `uv sync --frozen` et rend
   le résultat du contrat ;
5. il ne reste qu'une source de vérité : `requirements.txt` est supprimé, ou
   généré depuis le verrou.

## Repères

- La borne basse (`>=`) va dans `pyproject.toml` ; la version exacte de chaque
  paquet, dépendances de dépendances comprises, va dans `uv.lock`.
- `uv lock --check` dit si le verrou suit encore `pyproject.toml`.
- Une version de Python fixée doit pouvoir s'obtenir ailleurs : vérifiez que
  uv sait la trouver ou la télécharger (`uv python list`).
- Ce lab demande un accès au réseau : uv télécharge depuis PyPI.
