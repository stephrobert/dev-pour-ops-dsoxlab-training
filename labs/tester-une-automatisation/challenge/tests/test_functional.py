"""Tester une automatisation : cinq contrôles, vingt points chacun.

## Ce que ce lab note : la suite de tests de l'apprenant

Une suite de tests ne se juge pas à son nombre de tests verts, mais à ce
qu'elle attrape. On la joue donc, avec `uv run pytest` comme l'apprenant, sur
deux sortes d'outil :

- la RÉFÉRENCE (`donnees/reference/paquet/certcheck/certificats.py`) : une
  bonne suite y passe entièrement ;
- deux MUTANTS (`mutants/`, produits par `scripts/generer_mutants.py`) : la
  référence avec un seul défaut réaliste chacun. Une bonne suite échoue sur
  chacun d'eux ; on dit qu'elle « attrape » le mutant.

Chaque passage se fait dans une copie du projet, où seul le module
`src/certcheck/certificats.py` (la décision) est remplacé : les tests de l'apprenant ne sont jamais modifiés, et son propre
outil n'est jamais touché.

## Pourquoi chaque contrôle exige aussi la référence verte

Une suite qui échoue partout « attrape » tous les mutants et ne prouve rien.
Chaque contrôle exige donc d'abord que la suite passe sur la référence.

## Le dernier contrôle lit les fichiers de tests

Il vérifie qu'un test au moins isole ce qui varie : un dossier temporaire
(`tmp_path`, paramètre d'une fonction de test) ou une date fixée
(`CERTCHECK_NOW`). Ce sont les fichiers de l'apprenant, son livrable : on les
lit avec `ast`, sans rien exécuter de plus.
"""

from __future__ import annotations

import ast
from functools import cache
from pathlib import Path

import pytest

from conftest import REFERENCE_PAQUET, Passage, exiger_workdir, jouer_suite_paquet, workdir_lab

WORKDIR = workdir_lab(__file__)
LAB_ID = "tester-une-automatisation"
MUTANTS = Path(__file__).resolve().parent / "mutants"
MINIMUM_DE_TESTS = 3


@cache
def jouer(outil: str) -> Passage:
    exiger_workdir(WORKDIR, LAB_ID)
    return jouer_suite_paquet(WORKDIR, Path(outil))


def _exiger_reference_verte() -> Passage:
    ref = jouer(str(REFERENCE_PAQUET / "certificats.py"))
    if "Failed to spawn" in ref.sortie and "pytest" in ref.sortie:
        pytest.fail(
            "pytest n'est pas installé dans le projet : il est déclaré dans le "
            "groupe `dev` de pyproject.toml, `uv run pytest` l'installe. Ne le "
            "retirez pas.\n" + ref.resume(),
            pytrace=False,
        )
    if ref.code == 5 or ref.reussis == 0:
        pytest.fail(
            "pytest ne trouve aucun test (« no tests ran », code 5). Un test est une "
            "fonction dont le nom commence par `test_`, dans un fichier `tests/test_*.py`. "
            "Recopiez le premier test de l'étape 1 du scénario dans "
            "tests/test_certcheck.py, puis relancez `uv run pytest -v`.\n" + ref.resume(),
            pytrace=False,
        )
    assert ref.code == 0, (
        "Votre suite échoue sur l'outil de RÉFÉRENCE, qui respecte CONTRAT.md : un "
        "test attend autre chose que le contrat, ou dépend du jour où il tourne "
        "(passez la date aux fonctions, ou fixez-la par CERTCHECK_NOW). Lisez la "
        "ligne `assert` que pytest affiche : elle dit ce qui était attendu.\n" + ref.resume()
    )
    return ref


def test_la_suite_passe_sur_l_outil_juste() -> None:
    _exiger_reference_verte()


def test_la_suite_compte_au_moins_trois_tests() -> None:
    ref = _exiger_reference_verte()
    assert ref.reussis >= MINIMUM_DE_TESTS, (
        f"{ref.reussis} test(s) vert(s) : il en faut au moins {MINIMUM_DE_TESTS}. Un "
        "test ne vérifie qu'une règle ; écrivez-en un pour la frontière du seuil, "
        "un pour le code de sortie, un pour un certificat illisible (étapes 2 à 4 "
        "du scénario).\n" + ref.resume()
    )


def _exiger_mutant_attrape(nom: str, defaut: str, piste: str) -> None:
    _exiger_reference_verte()
    passage = jouer(str(MUTANTS / f"{nom}.py"))
    assert passage.code != 0 and passage.echoues > 0, (
        f"Le mutant « {nom} » passe inaperçu : votre suite reste verte sur un outil "
        f"où {defaut}.\nAjoutez un test qui l'attrape : {piste}\n" + passage.resume()
    )


def test_la_suite_attrape_un_seuil_exclusif() -> None:
    _exiger_mutant_attrape(
        "seuil_exclusif",
        "un certificat qui expire dans exactement 30 jours, avec un seuil de 30, passe en ok",
        "la frontière elle-même, `assert certificats.statut(30, 30) == \"warning\"`. "
        "Les bogues se cachent aux limites : 29 et 31 ne voient rien.",
    )


def test_la_suite_attrape_un_code_zero_malgre_une_alerte() -> None:
    _exiger_mutant_attrape(
        "code_zero_sur_alerte",
        "un parc dont la seule alerte est un warning sort en 0, comme si tout allait bien",
        "`assert certificats.code_de_sortie([{\"status\": \"warning\"}]) == 1`. Un "
        "test qui ne regarde qu'un parc expired ne le voit pas : testez chaque statut.",
    )


def _parametres(fonction: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    args = fonction.args
    return {a.arg for a in [*args.posonlyargs, *args.args, *args.kwonlyargs]}


def test_un_test_isole_un_fichier_ou_la_date() -> None:
    _exiger_reference_verte()
    fichiers = sorted((WORKDIR / "tests").rglob("test_*.py"))
    avec_tmp_path, avec_date_fixee = [], []
    for fichier in fichiers:
        try:
            arbre = ast.parse(fichier.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for noeud in ast.walk(arbre):
            if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)) and noeud.name.startswith("test"):
                if "tmp_path" in _parametres(noeud):
                    avec_tmp_path.append(noeud.name)
            if isinstance(noeud, ast.Constant) and noeud.value == "CERTCHECK_NOW":
                avec_date_fixee.append(fichier.name)
    assert avec_tmp_path or avec_date_fixee, (
        "Aucun test n'utilise `tmp_path` ni `CERTCHECK_NOW`. Un test répétable "
        "isole ce qui varie : `def test_x(tmp_path):` donne un dossier vide, propre "
        "à ce test, pour y écrire un faux certificat ; `CERTCHECK_NOW` fixe la date "
        "du jour quand on lance bin/certcheck. Voir l'étape 4 du scénario."
    )
