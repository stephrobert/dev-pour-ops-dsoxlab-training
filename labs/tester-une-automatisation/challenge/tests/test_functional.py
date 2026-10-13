"""Tester une automatisation : cinq contrôles, vingt points chacun.

## Ce que ce lab note : la suite de tests de l'apprenant

Une suite de tests ne se juge pas à son nombre de tests verts, mais à ce
qu'elle attrape. On la joue donc, avec `uv run pytest` comme l'apprenant, sur
deux sortes d'outil :

- la RÉFÉRENCE (`donnees/reference/certcheck.py`, la solution des labs
  précédents) : une bonne suite y passe entièrement ;
- quatre MUTANTS (`mutants/`, produits par `scripts/generer_mutants.py`) : la
  référence avec un seul défaut réaliste chacun. Une bonne suite échoue sur
  chacun d'eux ; on dit qu'elle « tue » le mutant.

Chaque passage se fait dans une copie du projet, où seul `certcheck.py` est
remplacé : les tests de l'apprenant ne sont jamais modifiés, et son propre
outil n'est jamais touché.

## Pourquoi chaque mutant exige aussi la référence verte

Une suite qui échoue partout « tue » tous les mutants et ne prouve rien.
Chaque contrôle de mutant exige donc d'abord que la suite passe sur la
référence.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

import pytest

from conftest import REFERENCE, Passage, exiger_workdir, jouer_suite_pytest, workdir_lab

WORKDIR = workdir_lab(__file__)
LAB_ID = "tester-une-automatisation"
MUTANTS = Path(__file__).resolve().parent / "mutants"
MINIMUM_DE_TESTS = 6


@cache
def jouer(outil: str) -> Passage:
    exiger_workdir(WORKDIR, LAB_ID)
    return jouer_suite_pytest(WORKDIR, Path(outil))


def _exiger_reference_verte() -> Passage:
    ref = jouer(str(REFERENCE))
    if "Failed to spawn" in ref.sortie and "pytest" in ref.sortie:
        pytest.fail(
            "pytest n'est pas installé dans le projet : il est déclaré dans le "
            "groupe `dev` de pyproject.toml, `uv sync` ou `uv run pytest` "
            "l'installe. Ne le retirez pas.\n" + ref.resume(),
            pytrace=False,
        )
    assert ref.code == 0, (
        "Votre suite échoue sur l'outil de RÉFÉRENCE, qui respecte CONTRAT.md : un "
        "test attend autre chose que le contrat, ou dépend du jour où il tourne "
        "(fixez la date par CERTCHECK_NOW, ou passez-la aux fonctions).\n" + ref.resume()
    )
    return ref


def test_la_suite_passe_sur_l_outil_juste_et_compte_assez_de_tests() -> None:
    ref = _exiger_reference_verte()
    assert ref.reussis >= MINIMUM_DE_TESTS, (
        f"{ref.reussis} test(s) vert(s) seulement : il en faut au moins {MINIMUM_DE_TESTS}. "
        "L'exemple livré ne vérifie qu'un certificat lointain ; une suite utile exerce "
        "le seuil, les erreurs de lecture, les codes de sortie et la simulation.\n"
        + ref.resume()
    )


def _exiger_mutant_tue(nom: str, defaut: str, piste: str) -> None:
    _exiger_reference_verte()
    passage = jouer(str(MUTANTS / f"{nom}.py"))
    assert passage.code != 0 and passage.echoues > 0, (
        f"Le mutant « {nom} » survit : votre suite passe sur un outil où {defaut}.\n"
        f"Ajoutez un test qui l'attrape : {piste}\n" + passage.resume()
    )


def test_la_suite_attrape_un_seuil_exclusif() -> None:
    _exiger_mutant_tue(
        "seuil_exclusif",
        "un certificat qui expire dans exactement N jours, avec un seuil de N, passe en ok",
        "la frontière elle-même, `statut(30, 30)` ou un certificat à exactement "
        "--days jours, doit rendre warning.",
    )


def test_la_suite_attrape_une_erreur_avalee() -> None:
    _exiger_mutant_tue(
        "erreur_avalee",
        "un certificat illisible est compté ok, sans que le code de sortie le dise",
        "un fichier qui n'est pas un certificat (écrit dans tmp_path) doit "
        "donner le statut error et le code 2.",
    )


def test_la_suite_attrape_un_code_zero_sur_alerte() -> None:
    _exiger_mutant_tue(
        "code_zero_sur_alerte",
        "un parc dont les seules alertes sont des warning sort en 0",
        "testez chaque statut séparément : un parc avec un warning et aucun "
        "expired doit rendre 1. Un test qui ne mélange que des expired ne le voit pas.",
    )


def test_la_suite_attrape_une_simulation_qui_envoie() -> None:
    _exiger_mutant_tue(
        "simulation_qui_envoie",
        "--publish --dry-run envoie le ticket dès que FORGE_URL est défini",
        "jouez --publish --dry-run avec FORGE_URL, FORGE_TOKEN et FORGE_REPO "
        "pointés sur une doublure (un serveur HTTP local qui note ce qu'il reçoit, "
        "ou `monkeypatch` sur certcheck.requete) et vérifiez qu'elle ne reçoit "
        "rien. Sans forge configurée, la simulation n'a rien à retenir.",
    )
