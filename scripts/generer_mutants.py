#!/usr/bin/env python3
"""Fabrique, depuis la référence de certcheck, les variantes défectueuses des labs.

Deux labs du fil rouge jouent une version de l'outil qui porte un défaut :

- `tester-une-automatisation` note la suite de tests de l'apprenant sur
  deux MUTANTS (`challenge/tests/mutants/`) : la référence avec UN défaut
  réaliste chacun, celui qu'un développeur introduit en retouchant le code.
  La suite doit passer sur la référence et échouer sur chacun d'eux. Ce sont
  deux défauts qu'un premier test simple attrape (frontière du seuil, code
  de sortie) : le lab est une initiation.
- `deboguer` part d'une version qui porte UN bogue signalé par un ticket
  (`fixtures/src/certcheck/certificats.py`) ; sa solution est générée aussi.

Le fil rouge est un paquet en src layout : seul le module `certificats.py`
(la décision) varie. Ces variantes se GÉNÈRENT depuis
`donnees/reference/paquet/certcheck/certificats.py`, elles ne
s'écrivent pas à la main : quand la référence évolue, `python3
scripts/generer_mutants.py` les refait, et chaque remplacement est vérifié
(exactement une occurrence) pour qu'une variante ne soit jamais, en silence,
identique à l'original.
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
REFERENCE = RACINE / "donnees" / "reference" / "paquet" / "certcheck" / "certificats.py"
LABS = RACINE / "labs"

# chemin de sortie -> liste de (avant, après), chaque « avant » présent une fois.
VARIANTES: dict[Path, list[tuple[str, str]]] = {
    # Le seuil devient exclusif : un certificat à exactement N jours avec --days N passe en ok.
    LABS / "tester-une-automatisation/challenge/tests/mutants/seuil_exclusif.py": [
        ("    if jours <= seuil:\n", "    if jours < seuil:\n"),
    ],
    # Une faute de frappe dans un statut : un parc en warning seulement sort en 0.
    LABS / "tester-une-automatisation/challenge/tests/mutants/code_zero_sur_alerte.py": [
        ('    if statuts & {"warning", "expired"}:\n', '    if statuts & {"warn", "expired"}:\n'),
    ],
    # Le bogue du lab deboguer : la date est découpée sur UN espace, ce qui
    # casse sur les jours à un chiffre (« Mar  5 »), et l'exception est avalée
    # sans trace par un `except Exception` trop large.
    LABS / "deboguer/fixtures/src/certcheck/certificats.py": [
        (
            '    brut = res.stdout.strip().partition("=")[2]  # « Mar  5 12:00:00 2031 GMT »\n'
            '    return datetime.strptime(brut, "%b %d %H:%M:%S %Y %Z").date()\n',
            '    brut = res.stdout.strip().partition("=")[2]  # « Nov 20 12:00:00 2025 GMT »\n'
            '    mois, jour, _heure, annee, _zone = brut.split(" ")\n'
            '    return datetime.strptime(f"{mois} {jour} {annee}", "%b %d %Y").date()\n',
        ),
        (
            "        except (OSError, ValueError) as exc:\n"
            '            log.error("%s : %s", hote, exc)\n',
            "        except Exception:\n"
            "            # Un certificat qu'on ne sait pas lire ne doit pas arrêter la tournée.\n",
        ),
    ],
    # La solution du formateur pour deboguer : split() sans argument, et
    # l'exception attendue journalisée au lieu d'être avalée.
    LABS / "deboguer/solution/src/certcheck/certificats.py": [
        (
            '    brut = res.stdout.strip().partition("=")[2]  # « Mar  5 12:00:00 2031 GMT »\n'
            '    return datetime.strptime(brut, "%b %d %H:%M:%S %Y %Z").date()\n',
            '    brut = res.stdout.strip().partition("=")[2]  # « Mar  5 12:00:00 2031 GMT »\n'
            '    # split() sans argument : openssl met DEUX espaces avant un jour à un chiffre.\n'
            '    mois, jour, _heure, annee, _zone = brut.split()\n'
            '    return datetime.strptime(f"{mois} {jour} {annee}", "%b %d %Y").date()\n',
        ),
    ],
}


def main() -> int:
    source = REFERENCE.read_text(encoding="utf-8")
    for cible, remplacements in VARIANTES.items():
        texte = source
        for avant, apres in remplacements:
            n = texte.count(avant)
            if n != 1:
                print(f"{cible.relative_to(RACINE)} : {n} occurrence(s) du passage visé, 1 "
                      "attendue. La référence a changé : mettez VARIANTES à jour.", file=sys.stderr)
                return 1
            texte = texte.replace(avant, apres)
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(texte, encoding="utf-8")
        relu = cible.read_text(encoding="utf-8")
        assert relu != source, f"{cible} est identique à la référence"
        compile(relu, str(cible), "exec")
        print(cible.relative_to(RACINE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
