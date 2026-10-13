"""Les tests de certcheck.

Un exemple pour démarrer : il appelle une fonction de l'outil avec une date
du jour FIXÉE, et vérifie son verdict. Il passe, et il ne prouve presque
rien. L'énoncé dit ce que votre suite doit attraper (`dsoxlab challenge`).

    uv run pytest -v
"""

from datetime import date
from pathlib import Path

import certcheck

RACINE = Path(__file__).resolve().parent.parent
CERTS = RACINE / "certs"


def test_un_certificat_lointain_est_ok():
    # L'horloge s'injecte : la date du jour est un argument, pas un appel à
    # date.today(). Le test rend le même verdict en 2026 et en 2040.
    resultats = certcheck.analyser([("web-01", CERTS / "web-01.pem")], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "ok"
    assert resultats[0]["not_after"] == "2045-06-15"
