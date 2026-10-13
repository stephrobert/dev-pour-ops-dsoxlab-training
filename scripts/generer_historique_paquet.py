#!/usr/bin/env python3
"""Fabrique historique.bundle, l'historique Git du paquet certcheck hérité.

Jumeau Python de `generer_historique.sh`, pour le lab lire-du-code. Le point
d'arrivée est le paquet posé dans `labs/lire-du-code/fixtures/` (pyproject,
uv.lock, src/certcheck/) ; les états antérieurs s'en déduisent par des
remplacements exacts, chacun vérifié (une chaîne attendue absente arrête
tout, au lieu de produire un historique faux en silence).

Cinq commits datés, deux auteurs, et un commit de Karim qui introduit
l'erreur avalée (`except Exception` et `log.debug`, certificat illisible
classé `ok`) : le lab demande de le retrouver avec `git log -S` ou
`git blame`. Dates et identités fixes : le bundle se reconstruit à
l'identique, empreintes comprises.

    python3 scripts/generer_historique_paquet.py labs/lire-du-code/fixtures/historique.bundle
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FINAL = RACINE / "labs" / "lire-du-code" / "fixtures"
FICHIERS = [
    "pyproject.toml",
    "uv.lock",
    "src/certcheck/__init__.py",
    "src/certcheck/certificats.py",
    "src/certcheck/cli.py",
    "src/certcheck/forge.py",
]

ERREUR_AVALEE = '''        except Exception as exc:
            # Un hôte décommissionné ne doit plus faire échouer le contrôle de la nuit.
            log.debug("%s ignoré : %s", hote, exc)
            resultats.append({"host": hote, "days_left": None, "status": "ok"})
'''
ERREUR_SIGNALEE = '''        except (subprocess.CalledProcessError, ValueError) as exc:
            log.error("%s : certificat illisible (%s)", hote, exc)
            resultats.append({"host": hote, "days_left": None, "status": "error"})
'''
BLOC_FORGE = '''
    alertes = [r for r in resultats if r["status"] in ("warning", "expired")]
    if alertes:
        if os.environ.get("FORGE_TOKEN"):
            # Import tardif : la forge n'est chargée que si l'on publie.
            from certcheck.forge import ouvrir_ticket

            numero = ouvrir_ticket(alertes)
            log.info("ticket ouvert : #%s", numero)
        else:
            print("FORGE_TOKEN absent : pas de ticket ouvert.", file=sys.stderr)
'''
HORLOGE_INJECTEE = '''def aujourd_hui() -> date:
    """La date du jour, ou celle de CERTCHECK_NOW pour rejouer un contrôle passé."""
    valeur = os.environ.get("CERTCHECK_NOW")
    if valeur:
        return date.fromisoformat(valeur)
    return datetime.now(UTC).date()
'''
HORLOGE_SYSTEME = '''def aujourd_hui() -> date:
    """La date du jour, en UTC."""
    return datetime.now(UTC).date()
'''


def remplacer(texte: str, avant: str, apres: str) -> str:
    if texte.count(avant) != 1:
        sys.exit(f"remplacement impossible, chaîne trouvée {texte.count(avant)} fois : {avant[:60]!r}")
    return texte.replace(avant, apres)


def version(etat: dict[str, str], ancienne: str, nouvelle: str) -> None:
    for nom in ("pyproject.toml", "uv.lock", "src/certcheck/__init__.py"):
        etat[nom] = remplacer(etat[nom], f'"{ancienne}"', f'"{nouvelle}"')


def etats() -> list[tuple[str, str, str, str, dict[str, str]]]:
    """(auteur, courriel, date, message, fichiers), du plus ancien au plus récent."""
    final = {nom: (FINAL / nom).read_text(encoding="utf-8") for nom in FICHIERS}

    # 4. La forge, avant le passage du seuil à 30 jours.
    e4 = dict(final)
    e4["src/certcheck/certificats.py"] = remplacer(e4["src/certcheck/certificats.py"],
                                                   "SEUIL = 30  # jours", "SEUIL = 15  # jours")
    version(e4, "0.3.0", "0.2.0")

    # 3. L'erreur avalée, avant la forge.
    e3 = dict(e4)
    del e3["src/certcheck/forge.py"]
    cli = remplacer(e3["src/certcheck/cli.py"], BLOC_FORGE, "")
    e3["src/certcheck/cli.py"] = remplacer(cli, "import os\n", "")
    version(e3, "0.2.0", "0.1.0")

    # 2. L'horloge injectable, avant l'erreur avalée.
    e2 = dict(e3)
    e2["src/certcheck/certificats.py"] = remplacer(e2["src/certcheck/certificats.py"],
                                                   ERREUR_AVALEE, ERREUR_SIGNALEE)

    # 1. La première version du paquet.
    e1 = dict(e2)
    certificats = remplacer(e1["src/certcheck/certificats.py"], HORLOGE_INJECTEE, HORLOGE_SYSTEME)
    e1["src/certcheck/certificats.py"] = remplacer(certificats, "import os\n", "")

    julien = ("Julien Marchand", "julien.marchand@exploitation.example")
    karim = ("Karim Benali", "karim.benali@exploitation.example")
    return [
        (*julien, "2024-03-04T09:12:00+01:00",
         "certcheck devient un paquet Python : inventaire, certificats, commande", e1),
        (*julien, "2024-05-21T16:40:00+02:00",
         "lit la date du jour dans CERTCHECK_NOW pour rejouer un contrôle", e2),
        (*karim, "2025-01-14T08:05:00+01:00",
         "ne fait plus échouer le contrôle de la nuit sur un hôte décommissionné", e3),
        (*karim, "2025-06-02T11:30:00+02:00",
         "ouvre un ticket sur la forge quand des certificats sont à renouveler", e4),
        (*julien, "2025-09-08T10:00:00+02:00",
         "seuil à 30 jours, demande de l'équipe sécurité", final),
    ]


def git(*args: str, cwd: Path, env: dict[str, str] | None = None) -> str:
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         env={**os.environ, **(env or {})}, check=False)
    if res.returncode != 0:
        sys.exit(f"git {' '.join(args)} : {res.stderr.strip()}")
    return res.stdout


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sortie = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="historique-certcheck-") as tmp:
        depot = Path(tmp)
        git("init", "-q", "-b", "main", cwd=depot)
        git("config", "commit.gpgsign", "false", cwd=depot)
        for auteur, courriel, jour, message, fichiers in etats():
            for nom in FICHIERS:
                chemin = depot / nom
                if nom in fichiers:
                    chemin.parent.mkdir(parents=True, exist_ok=True)
                    chemin.write_text(fichiers[nom], encoding="utf-8")
                elif chemin.exists():
                    chemin.unlink()
            git("add", "--all", cwd=depot)
            identite = {"GIT_AUTHOR_NAME": auteur, "GIT_AUTHOR_EMAIL": courriel, "GIT_AUTHOR_DATE": jour,
                        "GIT_COMMITTER_NAME": auteur, "GIT_COMMITTER_EMAIL": courriel,
                        "GIT_COMMITTER_DATE": jour}
            git("commit", "-q", "-m", message, cwd=depot, env=identite)
        # Le dernier état doit être le paquet du lab, octet pour octet.
        for nom in FICHIERS:
            if (depot / nom).read_bytes() != (FINAL / nom).read_bytes():
                sys.exit(f"le dernier commit diffère du point de départ du lab : {nom}")
        git("bundle", "create", "-q", str(sortie), "HEAD", "main", cwd=depot)
        print(f"historique écrit : {sortie}")
        print(git("log", "--format=%h %an %s", cwd=depot), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
