"""L'inventaire du parc et ce que disent ses certificats : date d'expiration, statut."""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

log = logging.getLogger(__name__)

SEUIL = 30  # jours


def lire_inventaire(chemin: Path) -> list[tuple[str, Path]]:
    """Les couples (hôte, certificat), chemins résolus depuis le dossier de l'inventaire."""
    entrees = []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        hote, certificat = ligne.split()
        entrees.append((hote, chemin.parent / certificat))
    return entrees


def date_expiration(certificat: Path) -> date:
    """La date notAfter du certificat, lue par openssl."""
    res = subprocess.run(
        ["openssl", "x509", "-enddate", "-noout", "-in", str(certificat)],
        capture_output=True, text=True, check=True,
    )
    brut = res.stdout.strip().partition("=")[2]  # « Mar  5 12:00:00 2031 GMT »
    return datetime.strptime(brut, "%b %d %H:%M:%S %Y %Z").date()


def aujourd_hui() -> date:
    """La date du jour, ou celle de CERTCHECK_NOW pour rejouer un contrôle passé."""
    valeur = os.environ.get("CERTCHECK_NOW")
    if valeur:
        return date.fromisoformat(valeur)
    return datetime.now(UTC).date()


def statut(jours: int, seuil: int) -> str:
    if jours < 0:
        return "expired"
    if jours <= seuil:
        return "warning"
    return "ok"


def analyser(entrees: list[tuple[str, Path]], seuil: int, jour: date) -> list[dict]:
    resultats = []
    for hote, certificat in entrees:
        try:
            fin = date_expiration(certificat)
        except Exception as exc:
            # Un hôte décommissionné ne doit plus faire échouer le contrôle de la nuit.
            log.debug("%s ignoré : %s", hote, exc)
            resultats.append({"host": hote, "days_left": None, "status": "ok"})
            continue
        jours = (fin - jour).days
        resultats.append({"host": hote, "days_left": jours, "status": statut(jours, seuil)})
    return resultats
