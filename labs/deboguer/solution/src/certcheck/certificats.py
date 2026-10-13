"""La décision : date d'expiration de chaque certificat, statut, code de sortie."""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

from certcheck.erreurs import ErreurUsage

log = logging.getLogger("certcheck")


def date_expiration(certificat: Path) -> date:
    """La date notAfter du certificat, lue par openssl."""
    res = subprocess.run(
        ["openssl", "x509", "-enddate", "-noout", "-in", str(certificat)],
        capture_output=True, text=True, check=False,
    )
    if res.returncode != 0:
        raise ValueError(f"certificat illisible : {certificat}")
    brut = res.stdout.strip().partition("=")[2]  # « Mar  5 12:00:00 2031 GMT »
    # split() sans argument : openssl met DEUX espaces avant un jour à un chiffre.
    mois, jour, _heure, annee, _zone = brut.split()
    return datetime.strptime(f"{mois} {jour} {annee}", "%b %d %Y").date()


def aujourd_hui() -> date:
    """La date du jour, ou celle de CERTCHECK_NOW : l'horloge s'injecte pour être testée."""
    valeur = os.environ.get("CERTCHECK_NOW")
    if not valeur:
        return datetime.now(UTC).date()
    try:
        return date.fromisoformat(valeur)
    except ValueError as exc:
        raise ErreurUsage(f"CERTCHECK_NOW invalide : {valeur!r} (AAAA-MM-JJ attendu)") from exc


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
        except (OSError, ValueError) as exc:
            log.error("%s : %s", hote, exc)
            resultats.append({"host": hote, "path": str(certificat), "not_after": None,
                              "days_left": None, "status": "error"})
            continue
        jours = (fin - jour).days
        resultats.append({"host": hote, "path": str(certificat), "not_after": fin.isoformat(),
                          "days_left": jours, "status": statut(jours, seuil)})
    return resultats


def code_de_sortie(resultats: list[dict]) -> int:
    statuts = {r["status"] for r in resultats}
    if "error" in statuts:
        return 2
    if statuts & {"warning", "expired"}:
        return 1
    return 0
