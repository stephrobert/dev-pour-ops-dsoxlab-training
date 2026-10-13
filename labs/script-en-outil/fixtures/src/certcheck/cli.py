"""L'interface de certcheck : arguments, configuration, sorties et codes de sortie.

`main` est la fonction que lance la commande `certcheck` (voir
[project.scripts] dans pyproject.toml) : l'entier qu'elle rend devient le
code de sortie du processus.
"""

from __future__ import annotations

import argparse
import json  # noqa: F401  (pour en_json)
import logging  # noqa: F401  (pour main)
import os  # noqa: F401  (pour seuil_depuis)
import sys  # noqa: F401  (pour main : sys.stderr)
from pathlib import Path

from certcheck import __version__  # noqa: F401  (pour --version)
from certcheck.certificats import ErreurUsage, analyser, aujourd_hui, lire_inventaire  # noqa: F401

SEUIL_PAR_DEFAUT = 30


def code_de_sortie(resultats: list[dict]) -> int:
    """Le code de sortie du contrat, calculé sur TOUS les statuts.

        un statut "error"                     -> 2  (l'emporte sur tout)
        sinon un "warning" ou un "expired"    -> 1
        sinon (que des "ok")                  -> 0
    """
    raise NotImplementedError("code_de_sortie : à écrire")


def en_texte(resultats: list[dict]) -> str:
    """Une ligne par hôte : l'hôte, son statut et les jours restants, séparés par des tabulations."""
    return "\n".join(f"{r['host']}\t{r['status']}\t{r['days_left']}" for r in resultats)


def en_json(resultats: list[dict], seuil: int) -> str:
    """UN SEUL document JSON, de cette forme (voir CONTRAT.md) :

        {"threshold_days": 30, "certificates": [ ...les dictionnaires d'analyser... ]}

    `json.dumps(..., ensure_ascii=False, indent=2)` fait l'affaire.
    """
    raise NotImplementedError("en_json : à écrire")


def seuil_depuis(argument: int | None) -> int:
    """Le seuil : --days s'il est donné, sinon CERTCHECK_DAYS, sinon SEUIL_PAR_DEFAUT.

        seuil_depuis(10)                            -> 10  (l'option l'emporte)
        seuil_depuis(None), CERTCHECK_DAYS="45"     -> 45
        seuil_depuis(None), sans CERTCHECK_DAYS     -> 30
        seuil_depuis(None), CERTCHECK_DAYS="dix"    -> lève ErreurUsage

    La variable se lit par `os.environ.get("CERTCHECK_DAYS")`.
    """
    raise NotImplementedError("seuil_depuis : à écrire")


def jours_positifs(valeur: str) -> int:
    """Le type de --days : argparse transforme l'exception en message et en code 2."""
    if not valeur.isdigit():
        raise argparse.ArgumentTypeError(f"nombre de jours positif attendu : {valeur!r}")
    return int(valeur)


def analyseur() -> argparse.ArgumentParser:
    """Les options du contrat. argparse écrit --help sur la sortie standard, et sort en 2,
    message sur la sortie d'erreur, sur une option inconnue ou une valeur refusée."""
    p = argparse.ArgumentParser(
        prog="certcheck",
        description="Signale les certificats TLS d'un parc qui arrivent à expiration.",
        epilog="Codes de sortie : 0 tout est valide, 1 certificat à renouveler, "
               "2 usage ou entrée inexploitable.",
    )
    p.add_argument("--inventory", type=Path, default=Path("inventaire.txt"),
                   help="inventaire des hôtes (défaut : inventaire.txt)")
    p.add_argument("--days", type=jours_positifs, metavar="N",
                   help=f"seuil d'alerte en jours (défaut : $CERTCHECK_DAYS, sinon {SEUIL_PAR_DEFAUT})")
    p.add_argument("--format", choices=("text", "json"), default="text", help="format de la sortie standard")
    # À AJOUTER : l'option --version, qui affiche « certcheck X.Y.Z » et sort en 0.
    # argparse le fait seul : action="version", version=f"certcheck {__version__}".
    return p


def main(argv: list[str] | None = None) -> int:
    """Le point d'entrée : rend le code de sortie du contrat.

    Dans l'ordre :
    1. `args = analyseur().parse_args(argv)` ;
    2. `logging.basicConfig(level=logging.WARNING, stream=sys.stderr)` : les
       messages de log partent sur la sortie d'erreur ;
    3. le seuil (`seuil_depuis(args.days)`), puis l'analyse :
       `analyser(lire_inventaire(args.inventory), seuil, aujourd_hui())` ;
    4. si ErreurUsage est levée en 3 : `print(f"certcheck: {exc}",
       file=sys.stderr)` et rendre 2, sans rien écrire sur la sortie standard ;
    5. écrire `en_json(...)` ou `en_texte(...)` selon `args.format`, avec
       `print`, sur la sortie standard ;
    6. rendre `code_de_sortie(resultats)`.
    """
    raise NotImplementedError("main : à écrire")
