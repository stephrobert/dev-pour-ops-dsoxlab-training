"""L'interface de certcheck : arguments, configuration, sorties et codes de sortie."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from certcheck import __version__
from certcheck.certificats import analyser, aujourd_hui, code_de_sortie
from certcheck.erreurs import ErreurPublication, ErreurUsage
from certcheck.forge import config_forge, publier
from certcheck.inventaire import lire_inventaire

SEUIL_PAR_DEFAUT = 30


def en_texte(resultats: list[dict]) -> str:
    lignes = []
    for r in resultats:
        if r["status"] == "error":
            lignes.append(f"{r['host']}\terror\tcertificat illisible")
        else:
            lignes.append(f"{r['host']}\t{r['status']}\t{r['days_left']} jours\t{r['not_after']}")
    return "\n".join(lignes)


def en_json(resultats: list[dict], seuil: int) -> str:
    return json.dumps({"threshold_days": seuil, "certificates": resultats}, ensure_ascii=False, indent=2)


def seuil_depuis(argument: int | None) -> int:
    if argument is not None:
        return argument
    valeur = os.environ.get("CERTCHECK_DAYS")
    if valeur is None:
        return SEUIL_PAR_DEFAUT
    try:
        seuil = int(valeur)
    except ValueError as exc:
        raise ErreurUsage(f"CERTCHECK_DAYS invalide : {valeur!r}") from exc
    if seuil < 0:
        raise ErreurUsage("CERTCHECK_DAYS doit être positif")
    return seuil


def jours_positifs(valeur: str) -> int:
    try:
        jours = int(valeur)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"nombre de jours attendu : {valeur!r}") from exc
    if jours < 0:
        raise argparse.ArgumentTypeError("le seuil doit être positif")
    return jours


def analyseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="certcheck",
        description="Signale les certificats TLS d'un parc qui arrivent à expiration.",
        epilog="Codes de sortie : 0 tout est valide, 1 certificat à renouveler, "
        "2 usage ou entrée inexploitable, 3 publication échouée.",
    )
    p.add_argument(
        "--inventory", type=Path, help="inventaire des hôtes (défaut : $CERTCHECK_INVENTORY, sinon inventaire.txt)"
    )
    p.add_argument(
        "--days",
        type=jours_positifs,
        help=f"seuil d'alerte en jours (défaut : $CERTCHECK_DAYS, sinon {SEUIL_PAR_DEFAUT})",
    )
    p.add_argument("--format", choices=("text", "json"), default="text", help="format de la sortie standard")
    p.add_argument(
        "--publish", action="store_true", help="ouvre un ticket sur la forge (FORGE_URL, FORGE_TOKEN, FORGE_REPO)"
    )
    p.add_argument("--dry-run", action="store_true", help="avec --publish : montre le ticket sans rien envoyer")
    p.add_argument("--verbose", action="store_true", help="journal détaillé sur la sortie d'erreur")
    p.add_argument("--version", action="version", version=f"certcheck {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = analyseur().parse_args(argv)  # usage incorrect : argparse sort en 2
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(message)s", stream=sys.stderr
    )
    try:
        seuil = seuil_depuis(args.days)
        forge = config_forge() if args.publish and not args.dry_run else None
        inventaire = args.inventory or Path(os.environ.get("CERTCHECK_INVENTORY", "inventaire.txt"))
        resultats = analyser(lire_inventaire(inventaire), seuil, aujourd_hui())
        print(en_json(resultats, seuil) if args.format == "json" else en_texte(resultats))
        if args.publish:
            publier(resultats, forge)
    except ErreurUsage as exc:
        print(f"certcheck: {exc}", file=sys.stderr)
        return 2
    except ErreurPublication as exc:
        print(f"certcheck: publication impossible : {exc}", file=sys.stderr)
        return 3
    return code_de_sortie(resultats)
