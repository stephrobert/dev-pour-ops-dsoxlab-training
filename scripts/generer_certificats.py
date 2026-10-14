#!/usr/bin/env python3
"""Fabrique les certificats de test du fil rouge, à dates d'expiration fixes.

Les labs ne génèrent aucun certificat au moment du contrôle : ils lisent
ceux-ci, et fixent « aujourd'hui » par CERTCHECK_NOW. Une date d'expiration
connue d'avance rend chaque résultat attendu calculable.

Seuls les certificats publics sont écrits : la clé privée de chacun est
jetée à la fin du script, rien de secret n'entre dans le dépôt.

    uv run --with cryptography scripts/generer_certificats.py
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "donnees" / "certs"

# hôte -> date d'expiration (midi UTC). Des jours à un chiffre exprès :
# openssl les écrit avec deux espaces (« Mar  5 »), ce qui casse un découpage naïf.
CERTIFICATS = {
    "web-01": "2045-06-15",
    "web-02": "2025-11-20",
    "vpn-01": "2031-03-05",
    "mail-01": "2040-01-10",
    "api-01": "2026-11-02",
    "api-02": "2026-11-30",
    "db-01": "2026-12-09",
    "db-02": "2027-01-15",
    "proxy-01": "2027-02-03",
    "proxy-02": "2027-03-31",
    "ldap-01": "2027-06-07",
    "git-01": "2027-09-21",
    "ci-01": "2028-01-01",
    "monitor-01": "2028-05-17",
    "backup-01": "2029-08-08",
    "dns-01": "2030-10-24",
}


def fabriquer(hote: str, expire: str) -> bytes:
    cle = ec.generate_private_key(ec.SECP256R1())
    nom = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, f"{hote}.lab.example")])
    fin = datetime.fromisoformat(expire).replace(hour=12, tzinfo=UTC)
    debut = datetime(2024, 1, 1, tzinfo=UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(nom)
        .issuer_name(nom)
        .public_key(cle.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(debut)
        .not_valid_after(fin)
        .sign(cle, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM)


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    for hote, expire in CERTIFICATS.items():
        (SORTIE / f"{hote}.pem").write_bytes(fabriquer(hote, expire))
    (SORTIE / "certs.json").write_text(json.dumps(CERTIFICATS, indent=2) + "\n", encoding="utf-8")
    print(f"{len(CERTIFICATS)} certificats écrits dans {SORTIE}")


if __name__ == "__main__":
    main()
