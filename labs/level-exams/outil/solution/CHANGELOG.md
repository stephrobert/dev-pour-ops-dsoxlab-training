# Changelog

Les changements notables de certcheck. Le format suit
[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), et les versions
suivent le [versionnage sémantique](https://semver.org/lang/fr/).

## [1.0.0] - 2026-10-13

Première version de l'outil qui remplace le script hérité `certcheck.sh`.

### Ajouté

- Un contrat écrit (`CONTRAT.md`) : options, configuration par
  l'environnement, sortie JSON, codes de sortie 0, 1, 2 et 3.
- La publication idempotente d'un ticket sur la forge, jeton dans l'en-tête,
  toutes les pages parcourues, délai maximal et reprise sur 429 et 5xx.
- Une suite de tests en boîte noire (`./test.sh`), qui juge l'exécutable
  désigné par `CERTCHECK_BIN`.
- `make install PREFIX=<dossier>`.

### Corrigé

- Un certificat absent ou illisible est une erreur (`status: error`, code 2),
  et non plus un certificat « à 0 jour » signalé en silence.
- Le jeton de la forge ne figure plus dans l'URL ni dans les journaux.
