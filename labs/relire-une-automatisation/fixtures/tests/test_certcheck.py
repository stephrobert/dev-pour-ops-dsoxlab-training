"""Tests unitaires de la décision de certcheck."""

from datetime import date
from pathlib import Path

import pytest

from certcheck import certificats, inventaire


@pytest.mark.parametrize(
    ("jours", "attendu"),
    [(-1, "expired"), (0, "warning"), (30, "warning"), (31, "ok")],
)
def test_le_seuil_est_inclusif(jours: int, attendu: str) -> None:
    assert certificats.statut(jours, 30) == attendu


def test_un_certificat_absent_rend_error(tmp_path: Path) -> None:
    resultats = certificats.analyser([("web-03", tmp_path / "absent.pem")], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "error"
    assert certificats.code_de_sortie(resultats) == 2


def test_l_inventaire_ignore_commentaires_et_lignes_vides(tmp_path: Path) -> None:
    fichier = tmp_path / "inventaire.txt"
    fichier.write_text("# parc\n\nweb-01\tcerts/web-01.pem\n", encoding="utf-8")
    assert inventaire.lire_inventaire(fichier) == [("web-01", tmp_path / "certs/web-01.pem")]
