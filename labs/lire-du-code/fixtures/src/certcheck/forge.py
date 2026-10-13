"""Ouverture d'un ticket sur la forge de l'équipe (API compatible Forgejo)."""

from __future__ import annotations

import json
import logging
import os
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

TITRE = "certcheck : certificats à renouveler"


def ouvrir_ticket(alertes: list[dict]) -> int:
    """Ouvre le ticket des certificats à renouveler et rend son numéro."""
    base = os.environ.get("FORGE_URL", "https://forge.exploitation.example").rstrip("/")
    depot = os.environ.get("FORGE_REPO", "exploitation/certificats")
    jeton = os.environ["FORGE_TOKEN"]
    query = urllib.parse.urlencode({"access_token": jeton})
    url = f"{base}/api/v1/repos/{depot}/issues?{query}"
    corps = "\n".join(f"- {a['host']} : {a['status']}, {a['days_left']} jours" for a in alertes)
    demande = urllib.request.Request(
        url,
        data=json.dumps({"title": TITRE, "body": corps}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    log.info("POST %s", url)
    with urllib.request.urlopen(demande) as reponse:
        return int(json.load(reponse)["number"])
