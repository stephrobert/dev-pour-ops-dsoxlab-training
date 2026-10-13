"""La suite de certcheck, en boîte noire : elle lance l'exécutable, jamais le code.

L'exécutable testé est celui de CERTCHECK_BIN (bin/certcheck par défaut). La
même suite juge ainsi l'outil livré, une version installée, ou une version
d'avant : ce qu'elle vérifie est le contrat, pas une implémentation.

Les certificats de certs/ ont des dates d'expiration connues, et CERTCHECK_NOW
fixe le jour : les verdicts ne dépendent pas de la date à laquelle la suite
tourne.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
CERTS = RACINE / "certs"
BINAIRE = Path(os.environ.get("CERTCHECK_BIN") or RACINE / "bin" / "certcheck").resolve()
# Dates d'expiration des certificats de certs/ (openssl x509 -enddate).
EXPIRATIONS = {"web-01": "2045-06-15", "web-02": "2025-11-20", "vpn-01": "2031-03-05", "mail-01": "2040-01-10"}


def certcheck(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    propre = {k: v for k, v in os.environ.items() if not k.startswith(("CERTCHECK_", "FORGE_"))}
    propre.update(env or {})
    return subprocess.run([str(BINAIRE), *args], capture_output=True, text=True, env=propre,
                          cwd=cwd, timeout=60, check=False)


def inventaire(dossier: Path, lignes: list[str], fin: str = "\n") -> Path:
    for nom in EXPIRATIONS:
        (dossier / "certs").mkdir(exist_ok=True)
        shutil.copy(CERTS / f"{nom}.pem", dossier / "certs" / f"{nom}.pem")
    chemin = dossier / "inventaire.txt"
    chemin.write_bytes((fin.join(lignes) + fin).encode())
    return chemin


def certificats(res: subprocess.CompletedProcess) -> dict[str, dict]:
    return {c["host"]: c for c in json.loads(res.stdout)["certificates"]}


# --- Interface ----------------------------------------------------------------


def test_l_aide_cite_chaque_option() -> None:
    res = certcheck("--help")
    assert res.returncode == 0
    for option in ("--inventory", "--days", "--format", "--version"):
        assert option in res.stdout


def test_la_version_suit_le_format_du_contrat() -> None:
    res = certcheck("--version")
    assert res.returncode == 0
    assert re.fullmatch(r"certcheck \d+\.\d+\.\d+", res.stdout.strip())


@pytest.mark.parametrize("args", [["--inconnue"], ["--days", "abc"], ["--format", "xml"], ["--days", "-3"]])
def test_un_usage_incorrect_sort_en_2_sans_rien_sur_la_sortie(args: list[str]) -> None:
    res = certcheck(*args)
    assert res.returncode == 2
    assert res.stdout == ""
    assert res.stderr.strip()


# --- Décision et codes de sortie -------------------------------------------------


@pytest.mark.parametrize(
    ("jour", "statut", "code"),
    [
        ("2031-02-02", "ok", 0),        # 31 jours avant le 2031-03-05
        ("2031-02-03", "warning", 1),   # 30 jours pile : le seuil est inclusif
        ("2031-03-05", "warning", 1),   # le jour même : 0 jour
        ("2031-03-06", "expired", 1),
    ],
)
def test_le_statut_suit_le_seuil(tmp_path: Path, jour: str, statut: str, code: int) -> None:
    inv = inventaire(tmp_path, ["vpn-01 certs/vpn-01.pem"])
    res = certcheck("--inventory", str(inv), "--days", "30", "--format", "json", env={"CERTCHECK_NOW": jour})
    assert certificats(res)["vpn-01"]["status"] == statut
    assert res.returncode == code


def test_le_seuil_est_inclusif(tmp_path: Path) -> None:
    inv = inventaire(tmp_path, ["vpn-01 certs/vpn-01.pem"])
    res = certcheck("--inventory", str(inv), "--days", "30", "--format", "json",
                    env={"CERTCHECK_NOW": "2031-02-03"})  # 30 jours pile
    vpn = certificats(res)["vpn-01"]
    assert (vpn["days_left"], vpn["status"]) == (30, "warning")
    assert res.returncode == 1


def test_le_json_porte_la_date_d_un_jour_a_un_chiffre(tmp_path: Path) -> None:
    inv = inventaire(tmp_path, ["vpn-01 certs/vpn-01.pem", "web-01 certs/web-01.pem"])
    res = certcheck("--inventory", str(inv), "--format", "json", env={"CERTCHECK_NOW": "2026-06-01"})
    lus = certificats(res)
    assert lus["vpn-01"]["not_after"] == "2031-03-05"
    assert lus["web-01"]["not_after"] == "2045-06-15"
    assert res.returncode == 0


def test_un_certificat_absent_est_une_erreur_jamais_zero_jour(tmp_path: Path) -> None:
    """Le défaut du script hérité : un certificat absent comptait « 0 jour », en silence."""
    inv = inventaire(tmp_path, ["web-01 certs/web-01.pem", "web-03 certs/web-03.pem"])
    res = certcheck("--inventory", str(inv), "--format", "json", env={"CERTCHECK_NOW": "2026-06-01"})
    absent = certificats(res)["web-03"]
    assert absent["status"] == "error"
    assert absent["days_left"] is None
    assert res.returncode == 2


def test_un_inventaire_absent_sort_en_2(tmp_path: Path) -> None:
    res = certcheck("--inventory", str(tmp_path / "absent.txt"))
    assert res.returncode == 2
    assert res.stderr.strip()


# --- Inventaire et configuration ----------------------------------------------------


def test_tabulations_et_commentaires_sont_acceptes(tmp_path: Path) -> None:
    inv = inventaire(tmp_path, ["# parc", "", "web-01\tcerts/web-01.pem", "web-02 \t certs/web-02.pem"])
    res = certcheck("--inventory", str(inv), "--format", "json", env={"CERTCHECK_NOW": "2026-06-01"})
    assert {h: c["status"] for h, c in certificats(res).items()} == {"web-01": "ok", "web-02": "expired"}
    assert res.returncode == 1


def test_l_option_l_emporte_sur_la_variable(tmp_path: Path) -> None:
    inv = inventaire(tmp_path, ["vpn-01 certs/vpn-01.pem"])
    env = {"CERTCHECK_NOW": "2031-02-13", "CERTCHECK_DAYS": "10"}  # vpn-01 expire dans 20 jours
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()
    assert certcheck("--inventory", str(inv), cwd=ailleurs, env=env).returncode == 0
    assert certcheck("--inventory", str(inv), "--days", "30", cwd=ailleurs, env=env).returncode == 1
    assert certcheck("--inventory", str(inv), cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "dix"}).returncode == 2
