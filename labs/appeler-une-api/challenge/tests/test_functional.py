"""Appeler une API avec requests : cinq contrôles, vingt points chacun.

## Ce que l'on observe : les requêtes reçues par une forge factice

Les contrôles lancent `bin/certcheck --publish` contre une petite forge
factice, démarrée ici, qui répond comme l'API des tickets de Forgejo (une
seule page) et NOTE chaque requête : méthode, URL, en-tête Authorization,
User-Agent, corps. Ils ne lisent pas le code de l'apprenant ; ils comptent ce
que la forge a reçu et ce que l'outil a rendu (code, sorties).

Le User-Agent dit QUI a parlé à la forge : requests envoie
`python-requests/<version>`. C'est ce qui prouve que la bibliothèque déclarée
dans pyproject.toml est bien celle qui appelle l'API.

## Ce lab est une initiation

Il couvre l'appel de base : jeton dans l'en-tête, délai maximal, erreur HTTP
traduite en code 3, création du ticket, pas de doublon sur la première page.
La pagination au-delà de la page 1 et la reprise sur panne passagère
relèvent d'un niveau plus avancé et ne sont pas notées.

## Ce qui est attendu se calcule

Parcs, dates du jour et seuils sont tirés au hasard (graine affichée en cas
d'échec) ; le code de sortie attendu et les hôtes en alerte sont recalculés
depuis les dates d'expiration connues des certificats.
"""

from __future__ import annotations

import json
import re
import threading
import time
import tomllib
import urllib.parse
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    TITRE_TICKET,
    attendus,
    code_attendu,
    ecrire_inventaire,
    exiger_executable,
    exiger_workdir,
    lancer,
    message,
    serveur_muet,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "appeler-une-api"
DELAI_MAX = 30  # secondes : au-delà, l'outil est considéré comme bloqué
DEPOT = "exploitation/certificats"
JETON = "jeton-de-test-7c2e91"


# --- La forge factice ------------------------------------------------------------


@dataclass
class ForgeApi:
    url: str = ""
    tickets: list[dict] = field(default_factory=list)
    requetes: list[dict] = field(default_factory=list)
    panne: bool = False

    def env(self, jeton: str = JETON) -> dict[str, str]:
        return {"FORGE_URL": self.url, "FORGE_TOKEN": jeton, "FORGE_REPO": DEPOT}

    def creations(self) -> list[dict]:
        return [r for r in self.requetes if r["methode"] == "POST"]

    def resume(self) -> str:
        lignes = [f"{r['methode']} {r['chemin']}{'?' + r['query'] if r['query'] else ''}"
                  for r in self.requetes]
        return "requêtes reçues par la forge :\n    " + ("\n    ".join(lignes[-10:]) or "(aucune)")


@pytest.fixture
def forge() -> Iterator[ForgeApi]:
    etat = ForgeApi()
    verrou = threading.Lock()

    class Gestionnaire(BaseHTTPRequestHandler):
        def _repondre(self, code: int, corps: object) -> None:
            charge = json.dumps(corps).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(charge)))
            self.end_headers()
            self.wfile.write(charge)

        def _noter(self, methode: str) -> dict | None:
            url = urllib.parse.urlsplit(self.path)
            longueur = int(self.headers.get("Content-Length") or 0)
            brut = self.rfile.read(longueur) if longueur else b""
            try:
                corps = json.loads(brut) if brut else None
            except json.JSONDecodeError:
                corps = None
            requete = {"methode": methode, "chemin": url.path, "query": url.query,
                       "auth": self.headers.get("Authorization", ""),
                       "agent": self.headers.get("User-Agent", ""), "corps": corps}
            with verrou:
                etat.requetes.append(requete)
            if etat.panne:
                self._repondre(503, {"message": "service indisponible"})
                return None
            if url.path.rstrip("/") != f"/api/v1/repos/{DEPOT}/issues":
                self._repondre(404, {"message": f"route inconnue : {url.path}"})
                return None
            if requete["auth"] not in (f"token {JETON}", f"Bearer {JETON}"):
                self._repondre(401, {"message": "jeton absent ou invalide"})
                return None
            return requete

        def do_GET(self) -> None:
            if self._noter("GET") is not None:
                self._repondre(200, [t for t in etat.tickets if t["state"] == "open"][:30])

        def do_POST(self) -> None:
            requete = self._noter("POST")
            if requete is None:
                return
            corps = requete["corps"] if isinstance(requete["corps"], dict) else {}
            ticket = {"number": len(etat.tickets) + 1, "title": corps.get("title", ""),
                      "body": corps.get("body", ""), "state": "open"}
            etat.tickets.append(ticket)
            self._repondre(201, ticket)

        def log_message(self, *args: object) -> None:
            return

    serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
    serveur.daemon_threads = True
    etat.url = f"http://127.0.0.1:{serveur.server_address[1]}"
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    try:
        yield etat
    finally:
        serveur.shutdown()
        serveur.server_close()


# --- Le parc et l'outil ------------------------------------------------------------


@dataclass
class Parc:
    dossier: Path
    inventaire: Path
    jour: date
    seuil: int
    graine: int
    alertes: list[str]
    code: int

    def args(self, *autres: str) -> list[str]:
        return ["--inventory", str(self.inventaire), "--days", str(self.seuil), "--publish", *autres]

    def env(self, forge: ForgeApi, jeton: str = JETON) -> dict[str, str]:
        return {"CERTCHECK_NOW": self.jour.isoformat(), **forge.env(jeton)}


def _parc(dossier: Path) -> Parc:
    graine = tirage().randrange(10**6)
    rnd = tirage(graine)
    while True:
        hotes = rnd.sample(sorted(EXPIRATIONS), rnd.randint(3, 5))
        jour = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900))
        seuil = rnd.choice([15, 30, 45, 90])
        calcul = attendus(hotes, jour, seuil)
        alertes = [h for h, (_, s) in calcul.items() if s in ("warning", "expired")]
        if alertes:
            break
    inventaire = ecrire_inventaire(dossier, hotes)
    return Parc(dossier, inventaire, jour, seuil, graine, alertes,
                code_attendu([s for _, s in calcul.values()]))


@pytest.fixture(scope="module")
def outil() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return exiger_executable(WORKDIR)


def _exiger_un_appel(forge: ForgeApi, res) -> None:
    if not forge.requetes:
        indice = ""
        if "NotImplementedError" in res.erreurs:
            indice = " requete() lève encore NotImplementedError : c'est l'étape 2 du scénario."
        elif "ModuleNotFoundError" in res.erreurs and "requests" in res.erreurs:
            indice = (" `import requests` échoue : la bibliothèque n'est pas déclarée dans "
                      "pyproject.toml (étape 1, `uv add requests==...`).")
        pytest.fail(
            message(
            en=f"--publish sent no request to the forge.{indice}\n  {res.resume()}",
            fr=f"--publish n'a envoyé aucune requête à la forge.{indice}\n  {res.resume()}",
        ),
            pytrace=False,
        )


# --- Les contrôles ----------------------------------------------------------------


def _version_requests_declaree() -> str:
    chemin = WORKDIR / "pyproject.toml"
    try:
        projet = tomllib.loads(chemin.read_text(encoding="utf-8")).get("project") or {}
    except (OSError, tomllib.TOMLDecodeError) as exc:
        pytest.fail(message(
            en=f"pyproject.toml is unreadable: {exc}",
            fr=f"pyproject.toml est illisible : {exc}",
        ), pytrace=False)
    for dependance in projet.get("dependencies") or []:
        m = re.fullmatch(r"\s*requests\s*==\s*([0-9][^\s;,]*)\s*(;.*)?", str(dependance), re.IGNORECASE)
        if m:
            return m.group(1)
    declarees = projet.get("dependencies") or []
    pytest.fail(
        message(
        en=f"pyproject.toml does not declare requests at an exact version (dependencies: "
        f"{declarees}). A library installed \"by hand\" exists only on your "
        "machine; declared and pinned (`uv add requests==2.34.2`), it installs "
        "identically wherever the tool runs.",
        fr=f"pyproject.toml ne déclare pas requests à une version exacte (dependencies : "
        f"{declarees}). Une bibliothèque installée « à la main » n'existe que sur votre "
        "poste ; déclarée et épinglée (`uv add requests==2.34.2`), elle s'installe à "
        "l'identique partout où l'outil tourne.",
    ),
        pytrace=False,
    )


def test_requests_appelle_la_forge_avec_le_jeton_en_en_tete(outil: Path, tmp_path: Path,
                                                            forge: ForgeApi) -> None:
    version = _version_requests_declaree()
    parc = _parc(tmp_path / "parc")
    res = lancer(outil, *parc.args("--verbose"), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
    _exiger_un_appel(forge, res)
    agents = sorted({r["agent"] for r in forge.requetes})
    assert agents == [f"python-requests/{version}"], message(
        en=f"The forge received the User-Agent {agents}, expected python-requests/{version}: "
        "it is requests, at the version declared in pyproject.toml, that must call "
        "the API. Another client (urllib, curl) does not count here.",
        fr=f"La forge a reçu le User-Agent {agents}, attendu python-requests/{version} : "
        "c'est requests, à la version déclarée dans pyproject.toml, qui doit appeler "
        "l'API. Un autre client (urllib, curl) ne compte pas ici.",
    )
    dans_l_url = [r for r in forge.requetes if JETON in r["query"] or JETON in r["chemin"]]
    assert not dans_l_url, message(
        en="The token appears in a request's URL. A URL ends up in the server's logs, "
        "in proxies' and in history: the token travels in the "
        f"`Authorization: token <token>` header, and only there.\n  {forge.resume()}",
        fr="Le jeton apparaît dans l'URL d'une requête. Une URL finit dans les journaux "
        "du serveur, des proxys et de l'historique : le jeton voyage dans l'en-tête "
        f"`Authorization: token <jeton>`, et seulement là.\n  {forge.resume()}",
    )
    mauvais = [r["auth"] or "(absent)" for r in forge.requetes
               if r["auth"] not in (f"token {JETON}", f"Bearer {JETON}")]
    assert not mauvais, message(
        en=f"Authorization header received: {mauvais[0]!r}. The forge expects "
        "`Authorization: token <token>`: headers={\"Authorization\": f\"token {jeton}\"}.\n  "
        f"{res.resume()}",
        fr=f"En-tête Authorization reçu : {mauvais[0]!r}. La forge attend "
        "`Authorization: token <jeton>` : headers={\"Authorization\": f\"token {jeton}\"}.\n  "
        f"{res.resume()}",
    )
    assert JETON not in res.sortie and JETON not in res.erreurs, message(
        en="The token appears on one of the tool's outputs (the --verbose log or a message). "
        f"One writes the URL there, never the secret.\n  {res.resume()}",
        fr="Le jeton apparaît sur une sortie de l'outil (journal --verbose ou message). "
        f"On y écrit l'URL, jamais le secret.\n  {res.resume()}",
    )


def test_un_delai_borne_l_attente(outil: Path, tmp_path: Path, forge: ForgeApi) -> None:
    parc = _parc(tmp_path / "parc")
    with serveur_muet() as url:
        env = {**parc.env(forge), "FORGE_URL": url}
        debut = time.monotonic()
        res = lancer(outil, *parc.args(), cwd=parc.dossier, env=env, timeout=DELAI_MAX)
        duree = time.monotonic() - debut
    assert res.code == 3 and res.erreurs.strip(), message(
        en="The forge accepts the connection and never answers. Expected: code 3 "
        "(publication failed) and a message on standard error once the timeout "
        f"has elapsed; got code {res.code} in {duree:.1f} s. Without `timeout=`, requests "
        "waits forever; with `timeout=5`, it raises requests.Timeout, to be translated "
        f"into ErreurPublication.\n  {res.resume()}",
        fr="La forge accepte la connexion et ne répond jamais. Attendu : le code 3 "
        "(publication échouée) et un message sur la sortie d'erreur une fois le délai "
        f"écoulé ; obtenu le code {res.code} en {duree:.1f} s. Sans `timeout=`, requests "
        "attend indéfiniment ; avec `timeout=5`, il lève requests.Timeout, à traduire "
        f"en ErreurPublication.\n  {res.resume()}",
    )


def test_une_erreur_http_donne_le_code_3(outil: Path, tmp_path: Path, forge: ForgeApi) -> None:
    parc = _parc(tmp_path / "parc")
    refus = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge, jeton="jeton-revoque"),
                   timeout=DELAI_MAX)
    _exiger_un_appel(forge, refus)
    assert refus.code == 3 and "401" in refus.erreurs, message(
        en="With a refused token, the forge answers 401. Expected: code 3 and a message "
        "on standard error naming the HTTP code (401), so that whoever is on call knows "
        "what to fix. `reponse.raise_for_status()` turns a 4xx or a 5xx into an "
        f"exception.\n  {refus.resume()}",
        fr="Avec un jeton refusé, la forge répond 401. Attendu : le code 3 et un message "
        "sur la sortie d'erreur qui cite le code HTTP (401), pour que l'astreinte sache "
        "quoi corriger. `reponse.raise_for_status()` transforme un 4xx ou un 5xx en "
        f"exception.\n  {refus.resume()}",
    )
    assert "jeton-revoque" not in refus.sortie + refus.erreurs, message(
        en=f"The error message contains the token: it must name only the method, "
        f"the URL and the cause.\n  {refus.resume()}",
        fr=f"Le message d'erreur contient le jeton : il ne doit citer que la méthode, "
        f"l'URL et la cause.\n  {refus.resume()}",
    )
    forge.panne = True
    panne = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
    assert panne.code == 3 and "503" in panne.erreurs, message(
        en="The forge, when down, answers 503. Expected: code 3 and a message naming 503, "
        f"never a Python traceback.\n  {panne.resume()}",
        fr="La forge en panne répond 503. Attendu : le code 3 et un message qui cite 503, "
        f"jamais une trace Python.\n  {panne.resume()}",
    )


def test_le_ticket_est_cree_avec_le_bon_titre(outil: Path, tmp_path: Path, forge: ForgeApi) -> None:
    parc = _parc(tmp_path / "parc")
    res = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
    _exiger_un_appel(forge, res)
    creations = forge.creations()
    assert len(creations) == 1, message(
        en=f"{len(creations)} ticket creation(s), a single one expected: some certificates "
        f"are due for renewal ({parc.alertes}, seed {parc.graine}).\n  {forge.resume()}\n  "
        f"{res.resume()}",
        fr=f"{len(creations)} création(s) de ticket, une seule attendue : des certificats "
        f"sont à renouveler ({parc.alertes}, graine {parc.graine}).\n  {forge.resume()}\n  "
        f"{res.resume()}",
    )
    corps = creations[0]["corps"] if isinstance(creations[0]["corps"], dict) else {}
    assert corps.get("title") == TITRE_TICKET, message(
        en=f"Title received: {corps.get('title')!r}, exactly {TITRE_TICKET!r} expected: "
        "it is by that title that the next run will find the ticket. The body "
        "is passed as JSON: requests.request(…, json={\"title\": …, \"body\": …}).",
        fr=f"Titre reçu : {corps.get('title')!r}, attendu exactement {TITRE_TICKET!r} : "
        "c'est par ce titre que la prochaine exécution retrouvera le ticket. Le corps "
        "se passe en JSON : requests.request(..., json={\"title\": ..., \"body\": ...}).",
    )
    oublies = [h for h in parc.alertes if h not in str(corps.get("body") or "")]
    assert not oublies, message(
        en=f"The ticket's body does not name {oublies} (seed {parc.graine}): a ticket "
        "says what to renew.",
        fr=f"Le corps du ticket ne cite pas {oublies} (graine {parc.graine}) : un ticket "
        "dit quoi renouveler.",
    )
    assert res.code == parc.code, message(
        en=f"Code {res.code}, expected {parc.code}: a successful publication does not change "
        f"the check's code (seed {parc.graine}).\n  {res.resume()}",
        fr=f"Code {res.code}, attendu {parc.code} : une publication réussie ne change pas "
        f"le code du contrôle (graine {parc.graine}).\n  {res.resume()}",
    )


def test_pas_de_doublon_si_le_ticket_est_deja_ouvert(outil: Path, tmp_path: Path, forge: ForgeApi) -> None:
    parc = _parc(tmp_path / "parc")
    rnd = tirage(parc.graine)
    total = rnd.randint(3, 12)
    position = rnd.randrange(total)
    for i in range(total):
        titre = TITRE_TICKET if i == position else f"Demande d'accès n°{i + 1}"
        forge.tickets.append({"number": i + 1, "title": titre, "state": "open"})
    res = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
    _exiger_un_appel(forge, res)
    lectures = [r for r in forge.requetes if r["methode"] == "GET" and r["auth"]]
    assert lectures, message(
        en="The tool did not read the list of tickets before acting: GET "
        f"/api/v1/repos/{DEPOT}/issues?state=open&type=issues, then compare the "
        f"titles (the ticket_existe function).\n  {forge.resume()}\n  {res.resume()}",
        fr="L'outil n'a pas lu la liste des tickets avant d'agir : GET "
        f"/api/v1/repos/{DEPOT}/issues?state=open&type=issues, puis comparer les "
        f"titres (fonction ticket_existe).\n  {forge.resume()}\n  {res.resume()}",
    )
    assert not forge.creations(), message(
        en=f"A duplicate was opened: the ticket \"{TITRE_TICKET}\" is already open "
        f"(position {position + 1} of {total}, first page). The tool runs every "
        "night; without that check, it would open one ticket per night.\n  "
        f"{forge.resume()}",
        fr=f"Un doublon a été ouvert : le ticket « {TITRE_TICKET} » est déjà ouvert "
        f"(position {position + 1} sur {total}, première page). L'outil tourne chaque "
        "nuit ; sans cette vérification, il ouvrirait un ticket par nuit.\n  "
        f"{forge.resume()}",
    )
    assert res.code == parc.code, message(
        en=f"Code {res.code}, expected {parc.code}: finding the ticket already open is not "
        f"an error (seed {parc.graine}).\n  {res.resume()}",
        fr=f"Code {res.code}, attendu {parc.code} : trouver le ticket déjà ouvert n'est pas "
        f"une erreur (graine {parc.graine}).\n  {res.resume()}",
    )
