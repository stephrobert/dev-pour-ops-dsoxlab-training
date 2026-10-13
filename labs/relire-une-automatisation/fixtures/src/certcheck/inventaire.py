"""Lecture de l'inventaire : une ligne par hôte, « <hôte> <certificat PEM> »."""

from __future__ import annotations

import os
from pathlib import Path

from certcheck.erreurs import ErreurUsage


def lire_inventaire(chemin: Path) -> list[tuple[str, Path]]:
    """Les couples (hôte, certificat) de l'inventaire, chemins résolus depuis son dossier."""
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as exc:
        raise ErreurUsage(f"inventaire illisible : {chemin} ({exc.strerror})") from exc
    entrees = []
    for numero, ligne in enumerate(texte.splitlines(), 1):
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        champs = ligne.split()
        if len(champs) != 2:
            raise ErreurUsage(f"{chemin}, ligne {numero} : « <hôte> <certificat> » attendu")
        hote, certificat = champs
        entrees.append((hote, (chemin.parent / certificat)))
    return entrees
