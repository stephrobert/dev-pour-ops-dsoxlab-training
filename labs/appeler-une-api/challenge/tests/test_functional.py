"""Appeler une API sans fragilité : cinq contrôles, vingt points chacun.

## Ce que l'on observe : les requêtes reçues par la forge

Les contrôles lancent `bin/certcheck --publish` contre une forge factice
(fixture `forge` du conftest) qui répond comme l'API des tickets de Forgejo :
pagination à 30 tickets par défaut et 50 au plus, jeton exigé dans l'en-tête
`Authorization`, pannes 503 sur commande. Ils ne lisent jamais le code : ils
comptent ce que la forge a reçu (méthode, URL, en-tête, corps) et ce que
l'outil a rendu (code, sorties).

## Ce qui est attendu se calcule

Parcs, dates du jour, seuils et position du ticket existant sont tirés au
hasard (graine affichée en cas d'échec). Le code de sortie attendu et la
liste des hôtes en alerte sont recalculés ici depuis les dates d'expiration
connues des certificats.
"""

from __future__ import annotations

import contextlib
import socket
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    TITRE_TICKET,
    Forge,
    attendus,
    code_attendu,
    ecrire_inventaire,
    exiger_executable,
    exiger_workdir,
    lancer,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "appeler-une-api"
DELAI_MAX = 60  # secondes : au-delà, l'outil est considéré comme bloqué


@pytest.fixture(scope="module")
def outil() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return exiger_executable(WORKDIR)


@dataclass
class Parc:
    """Un parc tiré au hasard qui contient au moins un certificat à renouveler."""

    dossier: Path
    inventaire: Path
    jour: date
    seuil: int
    graine: int
    alertes: list[str]
    sains: list[str]
    code: int

    def env(self, forge: Forge) -> dict[str, str]:
        return {"CERTCHECK_NOW": self.jour.isoformat(), **forge.env()}

    def args(self, *autres: str) -> list[str]:
        return ["--inventory", str(self.inventaire), "--days", str(self.seuil), "--publish", *autres]


def _parc(dossier: Path) -> Parc:
    rnd = tirage()
    graine = rnd.randrange(10**6)
    rnd = tirage(graine)
    while True:
        hotes = rnd.sample(sorted(EXPIRATIONS), rnd.randint(3, 6))
        jour = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900))
        seuil = rnd.choice([15, 30, 45, 90])
        calcul = attendus(hotes, jour, seuil)
        alertes = [h for h, (_, s) in calcul.items() if s in ("warning", "expired")]
        if alertes:
            break
    sains = [h for h in hotes if h not in alertes]
    inventaire = ecrire_inventaire(dossier, hotes)
    code = code_attendu([s for _, s in calcul.values()])
    return Parc(dossier, inventaire, jour, seuil, graine, alertes, sains, code)


def _tickets_certcheck(forge: Forge) -> list[dict]:
    """Les tickets réellement ouverts sur la forge sous le titre de certcheck."""
    return [t for t in forge.tickets if t.get("title") == TITRE_TICKET]


def _resume_requetes(forge: Forge) -> str:
    lignes = [f"{r['methode']} {r['chemin']}{'?' + r['query'] if r['query'] else ''}" for r in forge.requetes]
    return "requêtes reçues par la forge :\n    " + ("\n    ".join(lignes[-12:]) or "(aucune)")


@contextlib.contextmanager
def forge_muette() -> Iterator[tuple[str, list[socket.socket]]]:
    """Un serveur qui accepte les connexions TCP et ne répond jamais.

    C'est la panne la plus sournoise : la connexion s'établit, la requête part,
    et la réponse n'arrive pas. Sans délai maximal, le client attend pour
    toujours, et cron empile les exécutions bloquées.
    """
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.bind(("127.0.0.1", 0))
    serveur.listen(16)
    serveur.settimeout(0.2)
    connexions: list[socket.socket] = []
    arret = threading.Event()

    def accepter() -> None:
        while not arret.is_set():
            try:
                connexion, _ = serveur.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            connexions.append(connexion)  # gardée ouverte, jamais servie

    fil = threading.Thread(target=accepter, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur.getsockname()[1]}", connexions
    finally:
        arret.set()
        fil.join(timeout=2)
        for connexion in connexions:
            connexion.close()
        serveur.close()


def test_le_jeton_part_dans_l_en_tete(outil: Path, tmp_path: Path, forge: Forge) -> None:
    parc = _parc(tmp_path / "parc")
    res = lancer(outil, *parc.args("--verbose"), cwd=parc.dossier, env=parc.env(forge))
    assert forge.requetes, (
        f"--publish n'a envoyé aucune requête à la forge alors que {parc.alertes} sont à "
        f"renouveler (graine {parc.graine}).\n  {res.resume()}"
    )
    dans_l_url = [r for r in forge.requetes if forge.jeton in r["query"] or forge.jeton in r["chemin"]]
    assert not dans_l_url, (
        "Le jeton apparaît dans l'URL d'une requête. Une URL finit dans les journaux du "
        "serveur, des proxys et de l'historique : un jeton qui y passe est un jeton qui "
        "fuit. Il voyage dans l'en-tête `Authorization: token <jeton>`, et seulement là.\n  "
        f"{_resume_requetes(forge)}"
    )
    mauvais = [r["auth"] or "(absent)" for r in forge.requetes
               if r["auth"] not in (f"token {forge.jeton}", f"Bearer {forge.jeton}")]
    assert not mauvais, (
        f"En-tête Authorization reçu : {mauvais[0]!r}. La forge exige "
        "`Authorization: token <jeton>` (ou `Bearer <jeton>`) et répond 401 sans lui.\n  "
        f"{res.resume()}"
    )
    assert res.code == parc.code, (
        f"Code {res.code}, attendu {parc.code} : une publication réussie ne change pas le "
        f"code du contrôle (graine {parc.graine}).\n  {res.resume()}"
    )
    # Une forge en panne : les messages d'erreur ne doivent pas non plus trahir le jeton.
    forge.pannes = 50
    panne = lancer(outil, *parc.args("--verbose"), cwd=parc.dossier, env=parc.env(forge),
                   timeout=DELAI_MAX)
    for execution in (res, panne):
        assert forge.jeton not in execution.sortie and forge.jeton not in execution.erreurs, (
            "Le jeton apparaît sur une sortie de l'outil (journal --verbose ou message "
            "d'erreur). Une sortie d'erreur finit dans les journaux de cron ou du "
            "pipeline : on y écrit l'URL, jamais le secret.\n  "
            f"{execution.resume()}"
        )


def test_une_seule_creation_en_deux_executions(outil: Path, tmp_path: Path, forge: Forge) -> None:
    parc = _parc(tmp_path / "parc")
    forge.ajouter_tickets(5)
    # Un ticket qui CITE le titre sans le porter : seul le titre exact compte.
    forge.tickets.append({"number": len(forge.tickets) + 1, "state": "open",
                          "title": f"Re: {TITRE_TICKET}, faux positif ?"})
    codes = []
    for _ in range(2):
        res = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
        codes.append(res.code)
    ouverts = _tickets_certcheck(forge)
    titres = [r["corps"].get("title") if isinstance(r["corps"], dict) else None
              for r in forge.creations()]
    autres = [t for t in titres if t != TITRE_TICKET]
    assert not autres, (
        f"Titre(s) reçu(s) : {autres}, attendu exactement {TITRE_TICKET!r}. C'est par ce "
        "titre que la prochaine exécution retrouvera le ticket."
    )
    assert len(ouverts) == 1, (
        f"{len(ouverts)} ticket(s) ouvert(s) en deux exécutions, un seul attendu. "
        "L'outil tourne chaque nuit : avant d'ouvrir, il cherche un ticket ouvert qui "
        f"porte EXACTEMENT le titre « {TITRE_TICKET} » (un ticket qui le cite ne compte "
        "pas), et n'ouvre rien s'il existe. C'est ce qui rend l'opération idempotente.\n  "
        f"{_resume_requetes(forge)}\n  {res.resume()}"
    )
    texte = str(ouverts[0].get("body") or "")
    oublies = [h for h in parc.alertes if h not in texte]
    assert not oublies, (
        f"Le corps du ticket ne cite pas {oublies} (graine {parc.graine}, aujourd'hui "
        f"{parc.jour}, seuil {parc.seuil}) : un ticket doit dire quoi renouveler.\n  "
        f"corps reçu : {texte[:400]!r}"
    )
    assert codes == [parc.code, parc.code], (
        f"Codes {codes}, attendu {parc.code} aux deux exécutions : trouver le ticket "
        f"déjà ouvert n'est pas une erreur.\n  {res.resume()}"
    )


def test_le_ticket_est_cherche_dans_toutes_les_pages(outil: Path, tmp_path: Path, forge: Forge) -> None:
    parc = _parc(tmp_path / "parc")
    rnd = tirage(parc.graine)
    total = rnd.randint(110, 140)
    position = rnd.randint(60, total - 1)  # au-delà de la première page, même à 50 par page
    forge.ajouter_tickets(total, cible_en=position)
    res = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
    lectures = [r for r in forge.requetes if r["methode"] == "GET"]
    assert not forge.creations(), (
        f"Un doublon a été ouvert : le ticket de certcheck existe déjà, en position "
        f"{position + 1} sur {total} tickets ouverts (graine {parc.graine}). La forge rend "
        "30 tickets par page (50 au plus avec `limit`) : il faut demander les pages "
        "suivantes (`page=2`, `page=3`...) tant qu'une page est pleine, ou suivre "
        "l'en-tête `Link: rel=\"next\"`. Lire la première page seulement, c'est conclure "
        f"trop tôt que le ticket n'existe pas.\n  {len(lectures)} lecture(s).\n  "
        f"{_resume_requetes(forge)}"
    )
    assert res.code == parc.code, (
        f"Code {res.code}, attendu {parc.code} : le ticket existe, rien à publier, le "
        f"code reste celui du contrôle.\n  {res.resume()}"
    )


def test_les_pannes_passageres_sont_reprises(outil: Path, tmp_path: Path, forge: Forge) -> None:
    parc = _parc(tmp_path / "parc")
    forge.pannes = 2
    res = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
    ouverts = _tickets_certcheck(forge)
    assert res.code == parc.code and len(ouverts) == 1, (
        "La forge a répondu 503 deux fois, puis normalement. Une 503 (ou une 429, ou "
        "toute 5xx) est passagère : on attend un peu et on rejoue la même requête, trois "
        "essais au total, avant d'abandonner. Attendu : un ticket ouvert et le code "
        f"{parc.code} du contrôle ; obtenu le code {res.code} et "
        f"{len(ouverts)} ticket(s) ouvert(s).\n  {_resume_requetes(forge)}\n  {res.resume()}"
    )
    # Une panne durable : l'outil abandonne proprement, il ne boucle pas.
    avant = len(forge.requetes)
    forge.pannes = 1000
    debut = time.monotonic()
    res = lancer(outil, *parc.args(), cwd=parc.dossier, env=parc.env(forge), timeout=DELAI_MAX)
    duree = time.monotonic() - debut
    envoyees = len(forge.requetes) - avant
    assert res.code == 3 and res.erreurs.strip(), (
        "La forge reste en panne : après ses essais, l'outil abandonne avec le code 3 "
        f"(publication échouée) et un message sur la sortie d'erreur.\n  {res.resume()}"
    )
    assert envoyees <= 10, (
        f"{envoyees} requêtes envoyées à une forge en panne (en {duree:.1f} s). Une reprise "
        "a une limite : trois essais au total par requête, avec une attente qui grandit "
        "entre deux. Au-delà, on charge un service déjà à terre."
    )


def test_un_delai_maximal_borne_chaque_requete(outil: Path, tmp_path: Path, forge: Forge) -> None:
    parc = _parc(tmp_path / "parc")
    with forge_muette() as (url, connexions):
        env = {**parc.env(forge), "FORGE_URL": url}
        debut = time.monotonic()
        res = lancer(outil, *parc.args(), cwd=parc.dossier, env=env, timeout=DELAI_MAX)
        duree = time.monotonic() - debut
        assert connexions, (
            f"L'outil ne s'est jamais connecté à la forge ({url}).\n  {res.resume()}"
        )
    assert res.code == 3 and res.erreurs.strip(), (
        f"La forge accepte la connexion et ne répond jamais. L'outil a rendu la main en "
        f"{duree:.1f} s avec le code {res.code} : attendu 3 (publication échouée) et un "
        "message sur la sortie d'erreur, une fois le délai maximal écoulé à chaque "
        f"essai.\n  {res.resume()}"
    )
