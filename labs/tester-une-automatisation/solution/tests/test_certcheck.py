"""Les tests de certcheck.

Ce fichier ne contient encore aucun test : `uv run pytest` répond « no tests
ran ». Le scénario du lab (`scenario.fr.md`, deux dossiers au-dessus du
répertoire de travail) vous guide pas à pas pour écrire les premiers.

Rappel : pytest lance chaque fonction dont le nom commence par `test_`, et
un test échoue dès qu'une ligne `assert` est fausse.

    uv run pytest -v
"""

import os
import subprocess
from datetime import date
from pathlib import Path

from certcheck import certificats

RACINE = Path(__file__).resolve().parent.parent
CERTS = RACINE / "certs"
OUTIL = RACINE / "bin" / "certcheck"

# Écrivez vos tests ci-dessous.


# Étape 1 : un premier test. La date du jour est passée en argument : le
# test rend le même verdict en 2026 et en 2040.
def test_un_certificat_lointain_est_ok():
    resultats = certificats.analyser([("web-01", CERTS / "web-01.pem")], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "ok"
    assert resultats[0]["not_after"] == "2045-06-15"


# Étape 2 : la frontière du seuil. Le contrat dit « inclusif » : 30 jours
# avec un seuil de 30, c'est une alerte.
def test_le_seuil_est_inclusif():
    assert certificats.statut(30, 30) == "warning"
    assert certificats.statut(31, 30) == "ok"
    assert certificats.statut(-1, 30) == "expired"


# Étape 3 : le code de sortie, un statut à la fois.
def test_un_warning_seul_donne_le_code_1():
    assert certificats.code_de_sortie([{"status": "ok"}]) == 0
    assert certificats.code_de_sortie([{"status": "warning"}]) == 1
    assert certificats.code_de_sortie([{"status": "expired"}]) == 1
    assert certificats.code_de_sortie([{"status": "ok"}, {"status": "error"}]) == 2


# Étape 4 : un fichier temporaire. tmp_path est un dossier vide, propre à ce
# test, effacé par pytest : on y écrit un faux certificat sans rien salir.
def test_un_certificat_illisible_est_en_erreur(tmp_path):
    faux = tmp_path / "faux.pem"
    faux.write_text("ceci n'est pas un certificat\n")
    resultats = certificats.analyser([("faux", faux)], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "error"


# Étape 4, variante : l'outil entier, lancé comme cron le lance, avec une
# date fixée par CERTCHECK_NOW. vpn-01 expire le 2031-03-05 : le 2031-02-20,
# il reste 13 jours, donc warning et code 1.
def test_l_outil_sort_en_1_sur_un_warning(tmp_path):
    inventaire = tmp_path / "inventaire.txt"
    inventaire.write_text(f"vpn-01 {CERTS / 'vpn-01.pem'}\n")
    env = {**os.environ, "CERTCHECK_NOW": "2031-02-20"}
    res = subprocess.run([str(OUTIL), "--inventory", str(inventaire)],
                         env=env, capture_output=True, text=True, check=False)
    assert res.returncode == 1
    assert "warning" in res.stdout
