"""L'inventaire et ses certificats : lecture, date d'expiration, statut.

Les fonctions déjà écrites montrent la forme attendue. Celles qui lèvent
NotImplementedError sont à compléter : leur docstring dit ce qu'elles
rendent, avec des exemples.
"""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

log = logging.getLogger("certcheck")


class ErreurUsage(Exception):
    """Entrée ou configuration inexploitable : l'interface la traduit en code 2."""


def lire_inventaire(chemin: Path) -> list[tuple[str, Path]]:
    """Les couples (hôte, certificat) de l'inventaire, dans l'ordre du fichier.

    Règles :
    - les champs sont séparés par des espaces OU des tabulations : `ligne.split()`
      sans argument accepte les deux ;
    - les lignes vides et celles qui commencent par `#` sont ignorées ;
    - un chemin de certificat relatif se résout depuis le DOSSIER de
      l'inventaire : `chemin.parent / certificat` ;
    - un inventaire absent lève ErreurUsage (attrapez OSError autour de
      `chemin.read_text(...)`), avec un message qui nomme le fichier.

    Exemple, pour /parc/inventaire.txt contenant :

        # hôte   certificat
        web-01   certs/web-01.pem

    la fonction rend [("web-01", Path("/parc/certs/web-01.pem"))].
    """
    raise NotImplementedError("lire_inventaire : à écrire")


def date_expiration(certificat: Path) -> date:
    """La date notAfter du certificat, lue par openssl. ValueError s'il est absent ou illisible."""
    res = subprocess.run(
        ["openssl", "x509", "-enddate", "-noout", "-in", str(certificat)],
        capture_output=True, text=True, check=False,
    )
    if res.returncode != 0:
        raise ValueError(f"certificat illisible : {certificat}")
    brut = res.stdout.strip().partition("=")[2]  # « Mar  5 12:00:00 2031 GMT »
    return datetime.strptime(brut, "%b %d %H:%M:%S %Y %Z").date()


def aujourd_hui() -> date:
    """La date du jour, ou celle de CERTCHECK_NOW (AAAA-MM-JJ) : l'horloge s'injecte pour être testée."""
    valeur = os.environ.get("CERTCHECK_NOW")
    if not valeur:
        return datetime.now(UTC).date()
    try:
        return date.fromisoformat(valeur)
    except ValueError as exc:
        raise ErreurUsage(f"CERTCHECK_NOW invalide : {valeur!r} (AAAA-MM-JJ attendu)") from exc


def statut(jours: int, seuil: int) -> str:
    """Le statut d'un certificat qui expire dans `jours` jours.

    Le seuil est INCLUSIF :

        statut(-1, 30)  -> "expired"   (déjà expiré)
        statut(0, 30)   -> "warning"
        statut(30, 30)  -> "warning"   (exactement au seuil)
        statut(31, 30)  -> "ok"
    """
    raise NotImplementedError("statut : à écrire")


def analyser(entrees: list[tuple[str, Path]], seuil: int, jour: date) -> list[dict]:
    """Un dictionnaire par hôte, dans l'ordre de l'inventaire.

    Pour chaque (hôte, certificat) : `date_expiration`, puis le nombre de
    jours `(fin - jour).days`, puis `statut`. Exemple d'élément :

        {"host": "web-01", "not_after": "2045-06-15", "days_left": 6954, "status": "ok"}

    Un certificat absent ou illisible (date_expiration lève ValueError) ne
    doit JAMAIS disparaître ni passer pour valide : il donne

        {"host": "web-03", "not_after": None, "days_left": None, "status": "error"}

    et un message sur la sortie d'erreur, par exemple
    `log.error("%s : %s", hote, exc)`.
    """
    raise NotImplementedError("analyser : à écrire")
