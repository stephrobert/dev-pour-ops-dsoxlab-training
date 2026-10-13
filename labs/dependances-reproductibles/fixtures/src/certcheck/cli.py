"""certcheck : signale les certificats TLS d'un parc qui arrivent à expiration.

Lit un inventaire (une ligne par hôte : `<hôte> <chemin du certificat PEM>`),
calcule le nombre de jours avant l'expiration de chaque certificat, et rend un
code de sortie qu'un planificateur ou un pipeline sait exploiter. Avec
--publish, ouvre (une seule fois) un ticket sur la forge pour les certificats
à renouveler.

Depuis la 0.5.0, la date d'expiration est lue par la bibliothèque
`cryptography` (plus d'appel à openssl) et la forge est appelée par
`requests`. Codes de sortie :
  0  tous les certificats sont valides au-delà du seuil
  1  au moins un certificat expire dans le seuil, ou a expiré
  2  usage incorrect ou entrée inexploitable (inventaire, certificat illisible)
  3  la publication sur la forge a échoué
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import UTC, date, datetime
from pathlib import Path

from cryptography import x509

from certcheck import __version__

SEUIL_PAR_DEFAUT = 30
TITRE_TICKET = "certcheck : certificats à renouveler"
DELAI_RESEAU = 5  # secondes, pour chaque requête
ESSAIS = 3
TAILLE_PAGE = 50

log = logging.getLogger("certcheck")


class ErreurUsage(Exception):
    """Entrée ou configuration inexploitable : code de sortie 2."""


class ErreurPublication(Exception):
    """La forge a refusé ou n'a pas répondu : code de sortie 3."""


# --- Lecture ------------------------------------------------------------------


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
        entrees.append((hote, chemin.parent / certificat))
    return entrees


def date_expiration(certificat: Path) -> date:
    """La date notAfter du certificat, lue par la bibliothèque cryptography."""
    try:
        cert = x509.load_pem_x509_certificate(certificat.read_bytes())
    except ValueError as exc:
        raise ValueError(f"certificat illisible : {certificat}") from exc
    return cert.not_valid_after_utc.date()


def aujourd_hui() -> date:
    """La date du jour, ou celle de CERTCHECK_NOW : l'horloge s'injecte pour être testée."""
    valeur = os.environ.get("CERTCHECK_NOW")
    if not valeur:
        return datetime.now(UTC).date()
    try:
        return date.fromisoformat(valeur)
    except ValueError as exc:
        raise ErreurUsage(f"CERTCHECK_NOW invalide : {valeur!r} (AAAA-MM-JJ attendu)") from exc


# --- Décision -----------------------------------------------------------------


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


# --- Sorties ------------------------------------------------------------------


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


# --- Publication sur la forge (API compatible Forgejo et Gitea) ---------------


def requete(session: requests.Session, methode: str, url: str, **kwargs: object) -> requests.Response:
    """Une requête avec délai maximal, reprise sur 429 et 5xx, et jamais le jeton dans l'URL."""
    import requests  # seule la publication en a besoin : importé ici, pas au démarrage

    raison = ""
    for essai in range(1, ESSAIS + 1):
        try:
            reponse = session.request(methode, url, timeout=DELAI_RESEAU, **kwargs)
        except requests.RequestException as exc:
            raison = type(exc).__name__
        else:
            if reponse.status_code != 429 and reponse.status_code < 500:
                if reponse.status_code >= 400:
                    raise ErreurPublication(f"{methode} {url} : HTTP {reponse.status_code}")
                return reponse
            raison = f"HTTP {reponse.status_code}"
        if essai < ESSAIS:
            attente = 0.5 * 2 ** (essai - 1)
            log.warning("%s %s : %s, nouvel essai dans %.1f s", methode, url, raison, attente)
            time.sleep(attente)
    raise ErreurPublication(f"{methode} {url} : {raison} après {ESSAIS} essais")


def ticket_ouvert(session: requests.Session, base: str, depot: str) -> int | None:
    """Le numéro du ticket déjà ouvert par certcheck, en parcourant TOUTES les pages."""
    page = 1
    while True:
        reponse = requete(session, "GET", f"{base}/api/v1/repos/{depot}/issues",
                          params={"state": "open", "type": "issues", "limit": TAILLE_PAGE, "page": page})
        tickets = reponse.json()
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
    import requests  # seule la publication en a besoin : importé ici, pas au démarrage

    base, jeton, depot = forge
    with requests.Session() as session:
        session.headers.update({"Authorization": f"token {jeton}", "Accept": "application/json"})
        numero = ticket_ouvert(session, base, depot)
        if numero is not None:
            log.info("ticket déjà ouvert : #%s, rien de plus à faire", numero)
            return
        reponse = requete(session, "POST", f"{base}/api/v1/repos/{depot}/issues",
                          json={"title": TITRE_TICKET, "body": corps})
        log.info("ticket ouvert : #%s", reponse.json().get("number", "?"))


# --- Interface ----------------------------------------------------------------


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
    p.add_argument("--inventory", type=Path,
                   help="inventaire des hôtes (défaut : $CERTCHECK_INVENTORY, sinon inventaire.txt)")
    p.add_argument("--days", type=jours_positifs,
                   help=f"seuil d'alerte en jours (défaut : $CERTCHECK_DAYS, sinon {SEUIL_PAR_DEFAUT})")
    p.add_argument("--format", choices=("text", "json"), default="text", help="format de la sortie standard")
    p.add_argument("--publish", action="store_true",
                   help="ouvre un ticket sur la forge (FORGE_URL, FORGE_TOKEN, FORGE_REPO)")
    p.add_argument("--dry-run", action="store_true", help="avec --publish : montre le ticket sans rien envoyer")
    p.add_argument("--verbose", action="store_true", help="journal détaillé sur la sortie d'erreur")
    p.add_argument("--version", action="version", version=f"certcheck {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = analyseur().parse_args(argv)  # usage incorrect : argparse sort en 2
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(levelname)s %(message)s", stream=sys.stderr)
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


if __name__ == "__main__":
    sys.exit(main())
