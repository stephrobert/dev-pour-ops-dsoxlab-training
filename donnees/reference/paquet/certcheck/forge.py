"""Publication sur la forge (API compatible Forgejo et Gitea)."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from certcheck.erreurs import ErreurPublication, ErreurUsage

log = logging.getLogger("certcheck")

TITRE_TICKET = "certcheck : certificats à renouveler"
DELAI_RESEAU = 5  # secondes, pour chaque requête
ESSAIS = 3
TAILLE_PAGE = 50


def requete(methode: str, url: str, jeton: str, corps: dict | None = None) -> tuple[object, dict]:
    """Une requête JSON avec délai maximal, reprise sur 429 et 5xx, et jamais le jeton dans l'URL."""
    donnees = json.dumps(corps).encode() if corps is not None else None
    entetes = {"Authorization": f"token {jeton}", "Accept": "application/json"}
    if donnees is not None:
        entetes["Content-Type"] = "application/json"
    for essai in range(1, ESSAIS + 1):
        demande = urllib.request.Request(url, data=donnees, headers=entetes, method=methode)  # noqa: S310  (schéma validé par l'appelant)
        try:
            with urllib.request.urlopen(demande, timeout=DELAI_RESEAU) as reponse:  # noqa: S310
                return json.loads(reponse.read() or b"null"), dict(reponse.headers)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 and exc.code < 500:
                raise ErreurPublication(f"{methode} {url} : HTTP {exc.code}") from exc
            raison = f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError) as exc:
            raison = str(getattr(exc, "reason", exc))
        if essai < ESSAIS:
            attente = 0.5 * 2 ** (essai - 1)
            log.warning("%s %s : %s, nouvel essai dans %.1f s", methode, url, raison, attente)
            time.sleep(attente)
    raise ErreurPublication(f"{methode} {url} : {raison} après {ESSAIS} essais")


def ticket_ouvert(base: str, depot: str, jeton: str) -> int | None:
    """Le numéro du ticket déjà ouvert par certcheck, en parcourant TOUTES les pages."""
    page = 1
    while True:
        query = urllib.parse.urlencode({"state": "open", "type": "issues",
                                        "limit": TAILLE_PAGE, "page": page})
        tickets, _ = requete("GET", f"{base}/api/v1/repos/{depot}/issues?{query}", jeton)
        if not isinstance(tickets, list) or not tickets:
            return None
        for ticket in tickets:
            if ticket.get("title") == TITRE_TICKET:
                return int(ticket["number"])
        if len(tickets) < TAILLE_PAGE:
            return None
        page += 1


def config_forge() -> tuple[str, str, str]:
    """FORGE_URL, FORGE_TOKEN et FORGE_REPO, vérifiées AVANT tout travail."""
    base = os.environ.get("FORGE_URL", "").rstrip("/")
    jeton = os.environ.get("FORGE_TOKEN", "")
    depot = os.environ.get("FORGE_REPO", "")
    manquantes = [n for n, v in (("FORGE_URL", base), ("FORGE_TOKEN", jeton), ("FORGE_REPO", depot)) if not v]
    if manquantes:
        raise ErreurUsage(f"--publish exige {', '.join(manquantes)}")
    return base, jeton, depot


def publier(resultats: list[dict], forge: tuple[str, str, str] | None) -> None:
    """Ouvre le ticket des certificats à renouveler ; `forge` à None : simulation."""
    alertes = [r for r in resultats if r["status"] in ("warning", "expired")]
    if not alertes:
        log.info("aucun certificat à renouveler : rien à publier")
        return
    corps = "\n".join(f"- {r['host']} : {r['status']}, {r['days_left']} jours ({r['not_after']})"
                      for r in alertes)
    if forge is None:
        print(f"[simulation] ticket « {TITRE_TICKET} » :\n{corps}", file=sys.stderr)
        return
    base, jeton, depot = forge
    numero = ticket_ouvert(base, depot, jeton)
    if numero is not None:
        log.info("ticket déjà ouvert : #%s, rien de plus à faire", numero)
        return
    ticket, _ = requete("POST", f"{base}/api/v1/repos/{depot}/issues", jeton,
                        {"title": TITRE_TICKET, "body": corps})
    log.info("ticket ouvert : #%s", ticket.get("number") if isinstance(ticket, dict) else "?")
