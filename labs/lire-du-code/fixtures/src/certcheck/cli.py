"""La commande certcheck : lit l'inventaire, classe chaque certificat, alerte."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from certcheck import __version__
from certcheck.certificats import SEUIL, analyser, aujourd_hui, lire_inventaire

log = logging.getLogger("certcheck")


def code_de_sortie(resultats: list[dict]) -> int:
    statuts = {r["status"] for r in resultats}
    if "error" in statuts:
        return 2
    if statuts & {"warning", "expired"}:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(prog="certcheck", description=__doc__)
    analyseur.add_argument("--inventory", type=Path, default=Path("inventaire.txt"))
    analyseur.add_argument("--days", type=int, default=SEUIL)
    analyseur.add_argument("--verbose", action="store_true")
    analyseur.add_argument("--version", action="version", version=f"certcheck {__version__}")
    args = analyseur.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(levelname)s %(message)s", stream=sys.stderr)

    resultats = analyser(lire_inventaire(args.inventory), args.days, aujourd_hui())
    for r in resultats:
        print(f"{r['host']}\t{r['status']}\t{r['days_left']}")

    alertes = [r for r in resultats if r["status"] in ("warning", "expired")]
    if alertes:
        if os.environ.get("FORGE_TOKEN"):
            # Import tardif : la forge n'est chargée que si l'on publie.
            from certcheck.forge import ouvrir_ticket

            numero = ouvrir_ticket(alertes)
            log.info("ticket ouvert : #%s", numero)
        else:
            print("FORGE_TOKEN absent : pas de ticket ouvert.", file=sys.stderr)
    return code_de_sortie(resultats)


def lancer() -> None:
    """Le point d'entrée de la commande : le code rendu par main() devient celui du processus."""
    sys.exit(main())
