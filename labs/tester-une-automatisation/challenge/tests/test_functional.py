"""Se servir des tests : cinq contrôles, vingt points chacun.

## Ce que ce lab note

L'apprenant reçoit un projet dont la suite de tests est ROUGE : un test
attrape un vrai défaut. Il doit lire l'échec, corriger le code (pas le test),
relancer, puis ajouter un test en copiant un modèle.

- Les deux premiers contrôles lisent `reponses.yaml`. Les réponses attendues
  se recalculent en jouant la suite livrée sur le code livré
  (`fixtures/`), dans une copie : rien n'est écrit en dur.
- Le troisième juge la correction en boîte noire, par `bin/certcheck`, sur des
  hôtes, des seuils et des dates tirés au hasard.
- Le quatrième exige la suite verte sur le code de l'apprenant, avec les quatre
  tests reçus toujours présents : supprimer le test rouge ne corrige rien.
- Le cinquième joue la suite sur un MUTANT (la référence avec un défaut, un
  warning seul qui sort en 0) : le test ajouté doit l'attraper, et la suite
  doit rester verte sur la référence.
"""

from __future__ import annotations

import ast
import random
import re
import tempfile
from datetime import timedelta
from functools import cache
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    REFERENCE_PAQUET,
    Passage,
    copie_temporaire,
    ecrire_inventaire,
    executer,
    exiger_executable,
    exiger_outil,
    exiger_workdir,
    jouer_suite_paquet,
    lancer,
    lire_yaml,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "tester-une-automatisation"
LIVRE = Path(__file__).resolve().parents[2] / "fixtures"
MUTANTS = Path(__file__).resolve().parent / "mutants"
TESTS_RECUS = {
    "test_un_certificat_lointain_est_ok",
    "test_un_certificat_expire_est_signale",
    "test_le_seuil_est_inclusif",
    "test_un_certificat_absent_est_en_erreur",
}


def reponses() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    return lire_yaml(WORKDIR / "reponses.yaml")


def nettoyer(valeur: object) -> str:
    return str(valeur or "").strip().strip("`").strip().strip("'\"")


@cache
def echec_livre() -> tuple[str, str, str]:
    """Le test rouge du projet livré, et les deux valeurs de son assertion."""
    uv = exiger_outil("uv")
    with copie_temporaire(LIVRE) as copie:
        res = executer([uv, "run", "--quiet", "--directory", str(copie), "pytest", "-q", "-p", "no:cacheprovider"],
                       timeout=300)
    sortie = res.stdout + res.stderr
    noms = re.findall(r"FAILED \S+::(\w+)", sortie)
    assert len(noms) == 1, f"La suite livrée devait avoir un seul test rouge :\n{sortie[-1500:]}"
    valeurs = re.search(r"assert '(\w+)' == '(\w+)'", sortie)
    assert valeurs, f"Assertion introuvable dans la sortie de la suite livrée :\n{sortie[-1500:]}"
    obtenue, attendue = valeurs.group(1), valeurs.group(2)
    return noms[0], attendue, obtenue


@cache
def jouer(certificats: str | None) -> Passage:
    exiger_workdir(WORKDIR, LAB_ID)
    return jouer_suite_paquet(WORKDIR, Path(certificats) if certificats else None)


def noms_des_tests() -> set[str]:
    noms = set()
    for fichier in sorted((WORKDIR / "tests").rglob("test_*.py")):
        try:
            arbre = ast.parse(fichier.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        noms |= {n.name for n in ast.walk(arbre) if isinstance(n, ast.FunctionDef) and n.name.startswith("test")}
    return noms


def test_le_test_en_echec_est_nomme() -> None:
    r = reponses()
    nom, _, _ = echec_livre()
    donne = nettoyer(r.get("test_en_echec")).split("::")[-1].removesuffix("()")
    assert donne == nom, (
        f"`test_en_echec` vaut {r.get('test_en_echec')!r}. Lancez `uv run pytest -v` sur le "
        "projet reçu : la ligne FAILED nomme le test rouge, après les deux-points doubles."
    )


def test_l_assertion_est_lue() -> None:
    r = reponses()
    _, attendue, obtenue = echec_livre()
    assert nettoyer(r.get("valeur_attendue")) == attendue and nettoyer(r.get("valeur_obtenue")) == obtenue, (
        f"`valeur_attendue` vaut {r.get('valeur_attendue')!r} et `valeur_obtenue` "
        f"{r.get('valeur_obtenue')!r}. Dans la ligne `E   assert X == Y` de pytest, X est "
        "ce que le code a rendu, Y ce que le test attendait."
    )


def test_le_defaut_est_corrige() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    outil = exiger_executable(WORKDIR)
    graine = random.SystemRandom().randrange(10**6)
    rng = tirage(graine)
    for _ in range(3):
        hote = rng.choice(sorted(EXPIRATIONS))
        seuil = rng.randint(7, 60)
        jour = (EXPIRATIONS[hote] - timedelta(days=seuil)).isoformat()
        with tempfile.TemporaryDirectory(prefix="lab-tester-") as tmp:
            inventaire = ecrire_inventaire(Path(tmp), [hote])
            res = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil), cwd=Path(tmp),
                         env={"CERTCHECK_NOW": jour})
        ligne = next((x for x in res.sortie.splitlines() if x.startswith(hote)), "")
        assert "warning" in ligne and res.code == 1, (
            f"{hote} expire dans exactement {seuil} jours, avec --days {seuil} : warning et "
            f"code 1 attendus (le seuil est inclusif). Corrigez le CODE, la décision de "
            f"src/certcheck/certificats.py, pas le test. Graine {graine}.\n  {res.resume()}"
        )


def test_la_suite_est_verte_et_complete() -> None:
    passage = jouer(None)
    manquants = TESTS_RECUS - noms_des_tests()
    assert not manquants, (
        f"Les tests reçus {sorted(manquants)} ont disparu. Un test rouge signale un défaut : "
        "on corrige le code, on ne supprime pas le témoin."
    )
    assert passage.code == 0 and passage.echoues == 0, (
        "`uv run pytest` doit être vert sur votre version du projet. Lisez la ligne E "
        "du test rouge, corrigez le code, relancez.\n" + passage.resume()
    )


def test_un_test_ajoute_attrape_un_nouveau_defaut() -> None:
    reference = jouer(str(REFERENCE_PAQUET / "certificats.py"))
    assert reference.code == 0, (
        "Votre suite échoue sur l'outil de RÉFÉRENCE, qui respecte CONTRAT.md : un test "
        "attend autre chose que le contrat.\n" + reference.resume()
    )
    assert reference.reussis >= len(TESTS_RECUS) + 1, (
        f"{reference.reussis} test(s) vert(s) : ajoutez au moins un test aux quatre reçus. "
        "Copiez le deuxième test et changez ce qu'il vérifie (étape 4 du scénario).\n" + reference.resume()
    )
    mutant = jouer(str(MUTANTS / "code_zero_sur_alerte.py"))
    assert mutant.code != 0 and mutant.echoues > 0, (
        "Votre suite reste verte sur un outil où un parc dont la seule alerte est un "
        "warning sort en 0, comme si tout allait bien. Ajoutez un test qui vérifie que "
        "`certificats.code_de_sortie([{\"status\": \"warning\"}])` vaut 1.\n" + mutant.resume()
    )
