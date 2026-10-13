# Changelog

Toutes les évolutions notables de certcheck sont consignées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), et
le projet applique le [versionnage sémantique](https://semver.org/lang/fr/).

## [Unreleased]

## [1.0.0] - 2026-10-13

### Ajouté

- Publication d'un ticket sur la forge avec `--publish`, sans doublon, par
  la bibliothèque `requests`.
- Point d'entrée `certcheck`, installé avec le paquet.

### Modifié

- La date d'expiration est lue par la bibliothèque `cryptography` : plus
  aucun appel à `openssl`.
- Les dépendances sont déclarées dans `pyproject.toml` et verrouillées dans
  `uv.lock` ; `requirements.txt` est supprimé.
- `certcheck --version` lit la version dans les métadonnées du paquet.
