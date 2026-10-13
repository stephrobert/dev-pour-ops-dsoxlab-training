"""Publication sur la forge (API compatible Forgejo et Gitea)."""

from __future__ import annotations

import logging
import os
import sys

from certcheck.erreurs import ErreurPublication, ErreurUsage

log = logging.getLogger("certcheck")

TITRE_TICKET = "certcheck : certificats à renouveler"
DELAI_RESEAU = 5  # secondes : l'attente maximale de chaque requête


def requete(methode: str, url: str, jeton: str, corps: dict | None = None) -> object:
    """Envoie UNE requête JSON à la forge et rend la réponse décodée.

    À ÉCRIRE dans ce lab, avec la bibliothèque requests (voir le scénario) :
    le jeton part dans l'en-tête Authorization, jamais dans l'URL ; l'attente
    est bornée par DELAI_RESEAU ; une erreur HTTP (401, 503...), un délai
    dépassé ou une forge injoignable lèvent ErreurPublication, que l'interface
    traduit en code 3.
    """
    raise NotImplementedError("requete() n'est pas encore écrite : voir le scénario du lab")


def ticket_existe(base: str, depot: str, jeton: str) -> bool:
    """Vrai si un ticket OUVERT porte déjà exactement le titre TITRE_TICKET.

    À ÉCRIRE dans ce lab : lire la première page de
    GET {base}/api/v1/repos/{depot}/issues?state=open&type=issues
    et comparer le titre de chaque ticket. Tant qu'elle rend False, chaque
    exécution ouvre un nouveau ticket.
    """
    return False


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
    if ticket_existe(base, depot, jeton):
        log.info("un ticket « %s » est déjà ouvert : rien de plus à faire", TITRE_TICKET)
        return
    ticket = requete("POST", f"{base}/api/v1/repos/{depot}/issues", jeton,
                     {"title": TITRE_TICKET, "body": corps})
    log.info("ticket ouvert : #%s", ticket.get("number") if isinstance(ticket, dict) else "?")
