# certcheck

Signale les certificats TLS d'un parc qui arrivent à expiration. Le contrat
de l'outil est dans `CONTRAT.md`, ses évolutions dans `CHANGELOG.md`.

Les dépendances sont déclarées dans `pyproject.toml` et verrouillées dans
`uv.lock` ; l'interpréteur est fixé par `.python-version`.

```bash
uv sync --frozen
bin/certcheck --inventory inventaire.txt
```
