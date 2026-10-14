"""Les tests de certcheck.

Quatre tests, écrits par l'équipe. Lancez-les avant de toucher à quoi que ce
soit, et lisez ce que pytest affiche :

    uv run pytest -v

Rappel : pytest lance chaque fonction dont le nom commence par `test_`, et un
test échoue dès qu'une ligne `assert` est fausse. La ligne `E` de la sortie
montre la valeur obtenue et la valeur attendue.
"""

from datetime import date
from pathlib import Path

from certcheck import certificats

RACINE = Path(__file__).resolve().parent.parent
CERTS = RACINE / "certs"
AUJOURD_HUI = date(2026, 6, 1)  # la date est passée en argument : le verdict ne dépend pas du jour


def test_un_certificat_lointain_est_ok():
    resultats = certificats.analyser([("web-01", CERTS / "web-01.pem")], 30, AUJOURD_HUI)
    assert resultats[0]["status"] == "ok"
    assert resultats[0]["not_after"] == "2045-06-15"


def test_un_certificat_expire_est_signale():
    resultats = certificats.analyser([("web-02", CERTS / "web-02.pem")], 30, AUJOURD_HUI)
    assert resultats[0]["status"] == "expired"
    assert certificats.code_de_sortie(resultats) == 1


def test_le_seuil_est_inclusif():
    # Un certificat qui expire dans exactement 30 jours, avec un seuil de 30.
    assert certificats.statut(30, 30) == "warning"
    assert certificats.statut(31, 30) == "ok"


def test_un_certificat_absent_est_en_erreur(tmp_path):
    # tmp_path est un dossier vide, propre à ce test : le certificat n'y existe pas.
    resultats = certificats.analyser([("absent", tmp_path / "absent.pem")], 30, AUJOURD_HUI)
    assert resultats[0]["status"] == "error"
    assert certificats.code_de_sortie(resultats) == 2
