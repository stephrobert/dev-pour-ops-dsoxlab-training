"""Les tests de certcheck : ce qu'ils protègent, et comment.

Deux étages. Les fonctions de décision s'appellent directement, avec une date
du jour passée en argument (horloge injectée). L'outil entier se lance par
bin/certcheck, comme cron le fait, avec CERTCHECK_NOW pour fixer la date.

La publication ne touche jamais une vraie forge : une doublure, un petit
serveur HTTP local, enregistre ce qu'elle reçoit. Le test de --dry-run se
joue avec une forge CONFIGURÉE et joignable : sans cela, « aucune requête »
ne prouverait rien.

    uv run pytest -v
"""

import json
import os
import subprocess
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import certcheck
import pytest

RACINE = Path(__file__).resolve().parent.parent
CERTS = RACINE / "certs"
OUTIL = RACINE / "bin" / "certcheck"


# --- Décision : des fonctions, une date injectée ------------------------------


def test_un_certificat_lointain_est_ok():
    resultats = certcheck.analyser([("web-01", CERTS / "web-01.pem")], 30, date(2026, 6, 1))
    assert resultats[0]["status"] == "ok"
    assert resultats[0]["not_after"] == "2045-06-15"


@pytest.mark.parametrize(
    ("jours", "attendu"),
    [(-1, "expired"), (0, "warning"), (29, "warning"), (30, "warning"), (31, "ok")],
)
def test_le_seuil_est_inclusif(jours, attendu):
    # La frontière est le cas qui casse : 30 jours avec un seuil de 30 alerte.
    assert certcheck.statut(jours, 30) == attendu


def test_un_jour_a_un_chiffre_se_lit():
    # openssl écrit « Mar  5 » avec deux espaces.
    assert certcheck.date_expiration(CERTS / "vpn-01.pem") == date(2031, 3, 5)


def test_un_certificat_illisible_est_en_erreur(tmp_path):
    faux = tmp_path / "faux.pem"
    faux.write_text("ceci n'est pas un certificat\n")
    resultats = certcheck.analyser(
        [("faux", faux), ("absent", tmp_path / "absent.pem")], 30, date(2026, 6, 1)
    )
    assert [r["status"] for r in resultats] == ["error", "error"]
    assert certcheck.code_de_sortie(resultats) == 2


@pytest.mark.parametrize(
    ("statuts", "code"),
    [(["ok"], 0), (["ok", "warning"], 1), (["expired"], 1), (["warning", "error"], 2)],
)
def test_le_code_de_sortie_suit_les_statuts(statuts, code):
    assert certcheck.code_de_sortie([{"status": s} for s in statuts]) == code


# --- L'outil entier, lancé comme cron le lance --------------------------------


def lancer(*args, cwd, env=None):
    propre = {k: v for k, v in os.environ.items() if not k.startswith(("CERTCHECK_", "FORGE_"))}
    return subprocess.run([str(OUTIL), *args], cwd=cwd, env={**propre, **(env or {})},
                          capture_output=True, text=True, timeout=60, check=False)


def inventaire(dossier, *hotes):
    lignes = [f"{h} {CERTS / (h + '.pem')}" for h in hotes]
    chemin = dossier / "inventaire.txt"
    chemin.write_text("\n".join(lignes) + "\n")
    return chemin


def test_un_parc_en_warning_seulement_sort_en_1(tmp_path):
    # vpn-01 expire le 2031-03-05 : le 2031-02-20, il reste 13 jours.
    res = lancer("--inventory", str(inventaire(tmp_path, "vpn-01", "web-01")), "--format", "json",
                 cwd=tmp_path, env={"CERTCHECK_NOW": "2031-02-20"})
    assert res.returncode == 1, res.stderr
    statuts = {c["host"]: c["status"] for c in json.loads(res.stdout)["certificates"]}
    assert statuts == {"vpn-01": "warning", "web-01": "ok"}


def test_un_certificat_absent_sort_en_2(tmp_path):
    chemin = inventaire(tmp_path, "web-01")
    chemin.write_text(chemin.read_text() + "web-03 certs/web-03.pem\n")
    res = lancer("--inventory", str(chemin), cwd=tmp_path, env={"CERTCHECK_NOW": "2026-06-01"})
    assert res.returncode == 2


# --- La publication, contre une doublure de la forge ---------------------------


@pytest.fixture
def forge():
    """Un serveur HTTP local qui répond comme la forge et note chaque requête."""
    requetes = []

    class Gestionnaire(BaseHTTPRequestHandler):
        def _repondre(self, code, corps):
            charge = json.dumps(corps).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(charge)))
            self.end_headers()
            self.wfile.write(charge)

        def do_GET(self):
            requetes.append(("GET", self.path))
            self._repondre(200, [])

        def do_POST(self):
            longueur = int(self.headers.get("Content-Length") or 0)
            requetes.append(("POST", self.path, self.rfile.read(longueur)))
            self._repondre(201, {"number": 1})

        def log_message(self, *args):
            pass

    serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    env = {"FORGE_URL": f"http://127.0.0.1:{serveur.server_address[1]}",
           "FORGE_TOKEN": "jeton-de-test", "FORGE_REPO": "exploitation/certificats"}
    yield env, requetes
    serveur.shutdown()
    serveur.server_close()


def test_publish_ouvre_un_ticket_sur_la_doublure(tmp_path, forge):
    # Le témoin : sans --dry-run, la doublure reçoit bien le ticket. Sans ce
    # test, celui du --dry-run pourrait passer parce que la forge est injoignable.
    env, requetes = forge
    res = lancer("--inventory", str(inventaire(tmp_path, "web-02")), "--publish",
                 cwd=tmp_path, env={**env, "CERTCHECK_NOW": "2026-06-01"})
    assert res.returncode == 1, res.stderr
    assert [r[0] for r in requetes].count("POST") == 1


def test_dry_run_n_envoie_rien_meme_forge_configuree(tmp_path, forge):
    env, requetes = forge
    res = lancer("--inventory", str(inventaire(tmp_path, "web-02")), "--publish", "--dry-run",
                 cwd=tmp_path, env={**env, "CERTCHECK_NOW": "2026-06-01"})
    assert requetes == []
    assert res.returncode == 1
    assert "web-02" in res.stderr
