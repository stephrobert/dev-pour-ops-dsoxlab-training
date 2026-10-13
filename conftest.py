"""Outils partagés des tests de labs : lancer l'outil de l'apprenant comme une
boîte noire, lui donner des certificats à dates connues, et lui servir une
forge factice.

## Pourquoi une boîte noire

La formation est neutre du langage : l'outil se livre en Bash, en Python ou
en Go. Les contrôles ne l'importent donc jamais. Ils lancent l'exécutable
`bin/certcheck` du répertoire de travail, comme le ferait cron ou un
pipeline, et ne jugent que ce qu'un appelant observe : sorties, code de
sortie, requêtes reçues par la forge.

## Pourquoi des dates fixes et une horloge injectée

Les certificats de `donnees/certs/` ont une date d'expiration connue
(`certs.json`). « Aujourd'hui » se fixe par la variable CERTCHECK_NOW, prévue
par le contrat de l'outil : le résultat attendu se calcule, et un contrôle
joué en 2030 rend le même verdict qu'en 2026.

## Pourquoi une forge factice

Une vraie forge se joue dans la VM partagée avec l'introduction CI/CD. Ici,
le contrôle doit compter ce que l'outil envoie : combien de tickets ouverts,
avec quel en-tête, et aucun jeton dans l'URL. Le serveur ci-dessous répond
comme l'API de Forgejo (`/api/v1/repos/{owner}/{repo}/issues`), pagination
comprise, et sait tomber en panne sur commande.
"""

from __future__ import annotations

import contextlib
import json
import os
import random
import shutil
import stat
import subprocess
import tempfile
import threading
import time
import urllib.parse
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent
LABS_ROOT = REPO_ROOT / "labs"
DONNEES = REPO_ROOT / "donnees"
CERTS = DONNEES / "certs"
REFERENCE = DONNEES / "reference" / "certcheck.py"
TITRE_TICKET = "certcheck : certificats à renouveler"

# hôte -> date d'expiration, telle qu'écrite par scripts/generer_certificats.py
EXPIRATIONS: dict[str, date] = {
    hote: date.fromisoformat(jour)
    for hote, jour in json.loads((CERTS / "certs.json").read_text(encoding="utf-8")).items()
}


# --- Répertoire de travail -----------------------------------------------------


def workdir_lab(fichier_test: str | Path) -> Path:
    """Le répertoire de travail du lab dont `fichier_test` est le test."""
    return Path(fichier_test).resolve().parent.parent / "work"


def exiger_workdir(workdir: Path, lab_id: str) -> Path:
    if not workdir.is_dir():
        pytest.fail(
            f"Le répertoire de travail {workdir} n'existe pas. Lancez "
            f"`dsoxlab run {lab_id}` : il y pose le point de départ.",
            pytrace=False,
        )
    return workdir


def exiger_executable(workdir: Path) -> Path:
    """`bin/certcheck`, présent et exécutable : c'est la seule porte d'entrée testée."""
    outil = workdir / "bin" / "certcheck"
    if not outil.is_file():
        pytest.fail(
            "bin/certcheck est absent du répertoire de travail. C'est le point "
            "d'entrée que le contrat impose, quel que soit le langage : un script "
            "Bash, un lanceur qui appelle Python, ou le binaire Go.",
            pytrace=False,
        )
    if not os.access(outil, os.X_OK):
        pytest.fail("bin/certcheck n'est pas exécutable : `chmod +x bin/certcheck`.", pytrace=False)
    return outil


def lire_yaml(chemin: Path) -> dict:
    if not chemin.is_file():
        pytest.fail(f"{chemin.name} est absent du répertoire de travail.", pytrace=False)
    try:
        donnees = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        pytest.fail(f"{chemin.name} n'est pas un YAML valide : {exc}", pytrace=False)
    if not isinstance(donnees, dict):
        pytest.fail(f"{chemin.name} doit contenir un dictionnaire de réponses.", pytrace=False)
    return donnees


# --- Lancer l'outil ------------------------------------------------------------


@dataclass
class Execution:
    code: int
    sortie: str
    erreurs: str
    commande: list[str]

    def resume(self) -> str:
        return (
            f"commande : {' '.join(self.commande)}\n  code de sortie : {self.code}\n"
            f"  sortie : {self.sortie.strip()[-700:] or '(vide)'}\n"
            f"  erreurs : {self.erreurs.strip()[-700:] or '(vide)'}"
        )


def environnement_propre(env: dict[str, str] | None = None) -> dict[str, str]:
    """L'environnement du contrôle, sans aucune variable de l'outil héritée du shell."""
    environnement = {
        k: v for k, v in os.environ.items()
        if not k.startswith(("CERTCHECK_", "FORGE_")) and k != "VIRTUAL_ENV"
    }
    environnement.update(env or {})
    return environnement


def lancer(outil: Path, *args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
           timeout: int = 120) -> Execution:
    cmd = [str(outil), *args]
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                             env=environnement_propre(env), check=False)
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"`{' '.join(cmd)}` n'a pas rendu la main en {timeout} s. Un appel réseau "
            "sans délai maximal attend indéfiniment.",
            pytrace=False,
        )
    return Execution(res.returncode, res.stdout, res.stderr, cmd)


def executer(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None,
             timeout: int = 300) -> subprocess.CompletedProcess[str]:
    """Lance une commande et rend le résultat sans lever : c'est le test qui juge."""
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                              env=environnement_propre(env), check=False)
    except subprocess.TimeoutExpired as exc:
        sortie = exc.stdout if isinstance(exc.stdout, str) else ""
        return subprocess.CompletedProcess(cmd, 124, stdout=sortie, stderr=f"délai de {timeout} s dépassé")


# --- Inventaires et certificats ------------------------------------------------


def tirage(graine: int | None = None) -> random.Random:
    # Des données de test, pas un secret : un générateur ordinaire suffit.
    return random.Random(graine if graine is not None else time.time_ns())  # noqa: S311


def statut_attendu(jours: int, seuil: int) -> str:
    if jours < 0:
        return "expired"
    if jours <= seuil:
        return "warning"
    return "ok"


def ecrire_inventaire(dossier: Path, hotes: list[str], *, separateur: str = " ",
                      absents: list[str] | None = None, entete: bool = True) -> Path:
    """Un inventaire et ses certificats copiés dans `dossier/certs/`.

    `absents` : des hôtes dont le certificat n'existe pas (entrée inexploitable).
    """
    certs = dossier / "certs"
    certs.mkdir(parents=True, exist_ok=True)
    lignes = ["# inventaire généré par le contrôle", ""] if entete else []
    for hote in hotes:
        shutil.copy(CERTS / f"{hote}.pem", certs / f"{hote}.pem")
        lignes.append(f"{hote}{separateur}certs/{hote}.pem")
    for hote in absents or []:
        lignes.append(f"{hote}{separateur}certs/{hote}.pem")
    inventaire = dossier / "inventaire.txt"
    inventaire.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return inventaire


def attendus(hotes: list[str], jour: date, seuil: int) -> dict[str, tuple[int, str]]:
    """hôte -> (jours restants, statut), recalculés ici."""
    sortie = {}
    for hote in hotes:
        jours = (EXPIRATIONS[hote] - jour).days
        sortie[hote] = (jours, statut_attendu(jours, seuil))
    return sortie


def code_attendu(statuts: list[str]) -> int:
    if "error" in statuts:
        return 2
    if set(statuts) & {"warning", "expired"}:
        return 1
    return 0


def lire_json_sortie(execution: Execution) -> dict:
    try:
        donnees = json.loads(execution.sortie)
    except json.JSONDecodeError as exc:
        pytest.fail(
            "La sortie standard de --format json n'est pas un JSON valide "
            f"({exc}). Rien d'autre que le document ne doit y être écrit : les "
            f"journaux vont sur la sortie d'erreur.\n  {execution.resume()}",
            pytrace=False,
        )
    if not isinstance(donnees, dict) or not isinstance(donnees.get("certificates"), list):
        pytest.fail(
            "Le JSON doit être un objet portant la liste `certificates` (voir "
            f"CONTRAT.md).\n  {execution.resume()}",
            pytrace=False,
        )
    return donnees


# --- Forge factice ---------------------------------------------------------------


@dataclass
class Forge:
    """Un serveur HTTP local qui répond comme l'API des tickets de Forgejo.

    `tickets` : les tickets déjà présents (ouverts) sur le dépôt ;
    `requetes` : chaque requête reçue (méthode, chemin, paramètres, en-têtes,
    corps) ; `pannes` : nombre de réponses 503 à rendre avant de répondre
    normalement ; `jeton` : le seul accepté.
    """

    depot: str = "exploitation/certificats"
    jeton: str = "jeton-de-test-0f3a9c"
    tickets: list[dict] = field(default_factory=list)
    requetes: list[dict] = field(default_factory=list)
    pannes: int = 0
    url: str = ""

    def ajouter_tickets(self, n: int, *, cible_en: int | None = None) -> None:
        """`n` tickets ouverts sans rapport ; avec `cible_en`, celui de certcheck à cette position."""
        for i in range(n):
            titre = TITRE_TICKET if cible_en == i else f"Demande d'accès n°{i + 1}"
            self.tickets.append({"number": len(self.tickets) + 1, "title": titre, "state": "open"})

    def creations(self) -> list[dict]:
        return [r for r in self.requetes if r["methode"] == "POST"]

    def env(self) -> dict[str, str]:
        return {"FORGE_URL": self.url, "FORGE_TOKEN": self.jeton, "FORGE_REPO": self.depot}


@pytest.fixture
def forge() -> Iterator[Forge]:
    etat = Forge()
    verrou = threading.Lock()

    class Gestionnaire(BaseHTTPRequestHandler):
        def _repondre(self, code: int, corps: object, entetes: dict[str, str] | None = None) -> None:
            charge = json.dumps(corps).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(charge)))
            for cle, valeur in (entetes or {}).items():
                self.send_header(cle, valeur)
            self.end_headers()
            self.wfile.write(charge)

        def _noter(self, methode: str) -> dict | None:
            url = urllib.parse.urlsplit(self.path)
            longueur = int(self.headers.get("Content-Length") or 0)
            brut = self.rfile.read(longueur) if longueur else b""
            try:
                corps = json.loads(brut) if brut else None
            except json.JSONDecodeError:
                corps = {"_illisible": brut.decode(errors="replace")}
            requete = {
                "methode": methode, "chemin": url.path, "query": url.query,
                "params": dict(urllib.parse.parse_qsl(url.query)),
                "auth": self.headers.get("Authorization", ""), "corps": corps,
            }
            with verrou:
                etat.requetes.append(requete)
                if etat.pannes > 0:
                    etat.pannes -= 1
                    self._repondre(503, {"message": "service indisponible"})
                    return None
            attendu = f"/api/v1/repos/{etat.depot}/issues"
            if url.path.rstrip("/") != attendu:
                self._repondre(404, {"message": f"route inconnue : {url.path}"})
                return None
            if requete["auth"] not in (f"token {etat.jeton}", f"Bearer {etat.jeton}"):
                self._repondre(401, {"message": "jeton absent ou invalide"})
                return None
            return requete

        def do_GET(self) -> None:
            requete = self._noter("GET")
            if requete is None:
                return
            params = requete["params"]
            limite = min(int(params.get("limit") or 30), 50)  # comme Forgejo : 30 par défaut, 50 au plus
            page = max(int(params.get("page") or 1), 1)
            ouverts = [t for t in etat.tickets if t["state"] == "open"]
            tranche = ouverts[(page - 1) * limite: page * limite]
            entetes = {"X-Total-Count": str(len(ouverts))}
            if page * limite < len(ouverts):
                suivante = f"{etat.url}{requete['chemin']}?state=open&type=issues&limit={limite}&page={page + 1}"
                entetes["Link"] = f'<{suivante}>; rel="next"'
            self._repondre(200, tranche, entetes)

        def do_POST(self) -> None:
            requete = self._noter("POST")
            if requete is None:
                return
            corps = requete["corps"] if isinstance(requete["corps"], dict) else {}
            ticket = {"number": len(etat.tickets) + 1, "title": corps.get("title", ""),
                      "body": corps.get("body", ""), "state": "open"}
            etat.tickets.append(ticket)
            self._repondre(201, ticket)

        def log_message(self, *args: object) -> None:  # silence
            return

    serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
    serveur.daemon_threads = True
    etat.url = f"http://127.0.0.1:{serveur.server_address[1]}"
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield etat
    finally:
        serveur.shutdown()
        serveur.server_close()


# --- Copies et git ---------------------------------------------------------------

EXCLUS_COPIE = (".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build")


@contextlib.contextmanager
def copie_temporaire(source: Path, *, avec_git: bool = False) -> Iterator[Path]:
    """Une copie du répertoire de travail, à modifier ou à jouer, détruite à la sortie."""
    exclus = tuple(e for e in EXCLUS_COPIE if not (avec_git and e == ".git"))
    with tempfile.TemporaryDirectory(prefix="lab-devops-") as tmp:
        cible = Path(tmp) / "depot"
        shutil.copytree(source, cible, ignore=shutil.ignore_patterns(*exclus), symlinks=True)
        yield cible


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    cmd = ["git", "-c", "user.name=lab", "-c", "user.email=lab@example.invalid",
           "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", "-c", "init.defaultBranch=main", *args]
    return executer(cmd, cwd=cwd, timeout=60)


def rendre_executable(chemin: Path) -> None:
    chemin.chmod(chemin.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def exiger_outil(nom: str) -> str:
    chemin = shutil.which(nom)
    if not chemin:
        pytest.fail(
            f"L'outil `{nom}` n'est pas sur le PATH. Il est épinglé dans mise.toml "
            "à la racine du catalogue : lancez `mise install`, puis rejouez "
            "`dsoxlab check`.",
            pytrace=False,
        )
    return chemin
