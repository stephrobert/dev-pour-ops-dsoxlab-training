# Changelog

Les changements notables de certcheck. Le format suit
[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), et les versions
suivent le [versionnage sémantique](https://semver.org/lang/fr/).

## [1.0.0] - 2026-10-13

Première version du projet Python qui remplace le script hérité
`certcheck.sh`.

### Ajouté

- Le paquet `certcheck` (src layout), installable : `pip install .` ou
  `uv tool install .` crée la commande `certcheck`.
- Les options `--inventory`, `--days`, `--format text|json`, `--version` et
  `--help`, et le seuil réglable par `CERTCHECK_DAYS`.
- Une suite de tests pytest en boîte noire (`tests/`), qui juge
  l'exécutable désigné par `CERTCHECK_BIN` : `uv run pytest`.

### Corrigé

- Un certificat absent ou illisible est une erreur (`status: error`, code 2,
  message sur la sortie d'erreur), et non plus un certificat « à 0 jour »
  signalé en silence.
- Le code de sortie dit enfin s'il y a des certificats à renouveler (1).
