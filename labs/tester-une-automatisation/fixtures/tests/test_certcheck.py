"""Les tests de certcheck.

Ce fichier ne contient encore aucun test : `uv run pytest` répond « no tests
ran ». Le scénario du lab (`scenario.fr.md`, deux dossiers au-dessus du
répertoire de travail) vous guide pas à pas pour écrire les premiers.

Rappel : pytest lance chaque fonction dont le nom commence par `test_`, et
un test échoue dès qu'une ligne `assert` est fausse.

    uv run pytest -v
"""

from datetime import date
from pathlib import Path

from certcheck import certificats

RACINE = Path(__file__).resolve().parent.parent
CERTS = RACINE / "certs"

# Écrivez vos tests ci-dessous.
