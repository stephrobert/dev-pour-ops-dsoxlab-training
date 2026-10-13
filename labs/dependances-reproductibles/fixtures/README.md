# certcheck

Signale les certificats TLS d'un parc qui arrivent à expiration. Le contrat
de l'outil est dans `CONTRAT.md`.

Installation chez moi :

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install requests cryptography
pip install -e .
certcheck --inventory inventaire.txt
```
