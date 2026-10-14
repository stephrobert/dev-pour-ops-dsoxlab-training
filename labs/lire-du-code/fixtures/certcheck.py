#!/usr/bin/env python3
"""certcheck : signale les certificats TLS d'un parc qui arrivent à expiration.

Lancé chaque nuit par cron :

    python3 certcheck.py --inventory inventaire.txt --days 30

Lit l'inventaire (une ligne par hôte : `<hôte> <certificat PEM>`), demande à
openssl la date d'expiration de chaque certificat, et affiche une ligne par
hôte. Le code de sortie vaut 1 si un certificat demande une action, 0 sinon.
"""
import argparse
import os
import subprocess
import sys
from datetime import date, datetime

SEUIL_PAR_DEFAUT = 30


def aujourd_hui():
    """La date du jour, ou celle de CERTCHECK_NOW (AAAA-MM-JJ) pour rejouer un cas."""
    valeur = os.environ.get("CERTCHECK_NOW")
    if valeur:
        return date.fromisoformat(valeur)
    return date.today()


def lire_inventaire(chemin):
    """Les couples (hôte, certificat), sans les lignes vides ni les commentaires."""
    dossier = os.path.dirname(chemin)
    entrees = []
    with open(chemin, encoding="utf-8") as fichier:
        for ligne in fichier:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            hote, certificat = ligne.split()
            entrees.append((hote, os.path.join(dossier, certificat)))
    return entrees


def date_expiration(certificat):
    """La date de fin de validité, lue par openssl (« notAfter=Mar  5 12:00:00 2031 GMT »)."""
    sortie = subprocess.run(
        ["openssl", "x509", "-enddate", "-noout", "-in", certificat],
        capture_output=True, text=True, check=True,
    ).stdout
    brut = sortie.strip().split("=", 1)[1]
    return datetime.strptime(brut, "%b %d %H:%M:%S %Y %Z").date()


def statut(jours, seuil):
    """Le verdict pour un certificat qui expire dans `jours` jours."""
    if jours < seuil:
        return "warning"
    return "ok"


def main():
    parser = argparse.ArgumentParser(description="Signale les certificats qui arrivent à expiration.")
    parser.add_argument("--inventory", default="inventaire.txt", help="l'inventaire des hôtes")
    parser.add_argument("--days", type=int, default=SEUIL_PAR_DEFAUT, help="le seuil d'alerte, en jours")
    args = parser.parse_args()

    alerte = False
    jour = aujourd_hui()
    for hote, certificat in lire_inventaire(args.inventory):
        jours = (date_expiration(certificat) - jour).days
        verdict = statut(jours, args.days)
        print(f"{hote}\t{verdict}\t{jours} jours")
        if verdict != "ok":
            alerte = True
    return 1 if alerte else 0


if __name__ == "__main__":
    sys.exit(main())
