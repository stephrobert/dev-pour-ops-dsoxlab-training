"""Épreuve : intervenir sur un petit outil d'exploitation. Cinq contrôles.

## Ce que l'épreuve mesure, et ce qu'elle ne mesure pas

L'apprenant reçoit un dépôt Git (`depot.bundle`), un ticket et le journal d'un
run de CI rouge. Il clone le dépôt dans `certcheck/`, lit le code, comprend le
défaut et l'échec de la CI, fait une correction limitée, et rend des tests et
des contrôles de qualité verts. On ne lui demande d'écrire ni outil, ni
pipeline, ni version : ce sont les gestes de l'initiation, pas ceux d'un
développeur autonome.

## Rien n'est écrit en dur

- Les réponses attendues se recalculent depuis le bundle livré : la commande
  se relit dans son `pyproject.toml`, l'hôte mal classé en lançant l'outil
  livré à la date du ticket, l'étape en échec en relisant `ci/run-12.log`, le
  commit fautif par `git log -S`.
- La correction se juge en boîte noire, par `bin/certcheck`, sur des hôtes,
  des seuils et des dates tirés au hasard.
- Les étapes de CI rejouées sont celles du `ci.yml` LIVRÉ, pas d'une copie que
  l'apprenant aurait allégée.
"""

from __future__ import annotations

import ast
import json
import random
import re
import tempfile
import tomllib
from datetime import date, timedelta
from functools import cache
from pathlib import Path

import pytest
import yaml

from conftest import (
    EXPIRATIONS,
    copie_temporaire,
    ecrire_inventaire,
    executer,
    exiger_executable,
    exiger_outil,
    exiger_workdir,
    git,
    lancer,
    lire_yaml,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "level-exams-intervenir"
LIVRE = Path(__file__).resolve().parents[2] / "fixtures"
JOUR_DU_TICKET = date(2026, 10, 31)
TESTS_RECUS = {
    "test_un_certificat_lointain_est_ok",
    "test_un_certificat_expire_est_signale",
    "test_le_seuil_est_inclusif",
    "test_un_jour_a_un_chiffre_est_lu",
    "test_un_certificat_absent_est_en_erreur",
}


def reponses() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    return lire_yaml(WORKDIR / "reponses.yaml")


def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    chemin = WORKDIR / "certcheck"
    if not (chemin / "pyproject.toml").is_file():
        pytest.fail("Le dépôt n'est pas cloné : `git clone depot.bundle certcheck`, puis travaillez dans certcheck/.",
                    pytrace=False)
    return chemin


def nettoyer(valeur: object) -> str:
    return str(valeur or "").strip().strip("`").strip().strip("'\"").strip()


@cache
def depot_livre() -> Path:
    """Le dépôt livré, cloné une fois pour toute la session de contrôle."""
    dossier = Path(tempfile.mkdtemp(prefix="intervenir-livre-"))
    res = git("clone", "-q", str(LIVRE / "depot.bundle"), str(dossier / "certcheck"), cwd=dossier)
    assert res.returncode == 0, res.stderr
    return dossier / "certcheck"


@cache
def statuts_livres() -> dict[str, str]:
    livre = depot_livre()
    res = lancer(livre / "bin" / "certcheck", "--inventory", "inventaire.txt", cwd=livre,
                 env={"CERTCHECK_NOW": JOUR_DU_TICKET.isoformat()})
    return {c[0]: c[1] for c in (x.split("\t") for x in res.sortie.splitlines()) if len(c) >= 2}


def etapes_livrees() -> list[dict]:
    doc = yaml.safe_load((depot_livre() / ".forgejo" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
    return doc["jobs"]["integrer"]["steps"]


def test_l_outil_est_compris() -> None:
    r = reponses()
    assert nettoyer(r.get("role")).lower() == "verifier-expiration", (
        f"`role` vaut {r.get('role')!r} : relisez README.md et CONTRAT.md du dépôt."
    )
    declaree = tomllib.loads((depot_livre() / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
    assert nettoyer(r.get("commande_declaree")) == declaree["certcheck"], (
        f"`commande_declaree` vaut {r.get('commande_declaree')!r} : c'est la valeur de "
        "`certcheck = ...` dans [project.scripts] de pyproject.toml."
    )
    seuil = 30
    mal_classes = sorted(h for h, s in statuts_livres().items()
                         if s == "ok" and (EXPIRATIONS[h] - JOUR_DU_TICKET).days <= seuil)
    assert nettoyer(r.get("hote_mal_classe")) in mal_classes, (
        f"`hote_mal_classe` vaut {r.get('hote_mal_classe')!r}. Lancez l'outil reçu à la date "
        "du ticket et comparez chaque ligne au contrat : un hôte à 30 jours ou moins doit "
        "être en warning."
    )


def test_la_ci_et_l_historique_sont_lus() -> None:
    r = reponses()
    journal = (LIVRE / "ci" / "run-12.log").read_text(encoding="utf-8")
    echec = re.search(r"== Étape « (.+?) » : échec", journal)
    assert echec, "journal livré illisible"
    noms = {e["name"] for e in etapes_livrees()}
    assert nettoyer(r.get("etape_en_echec")) == echec.group(1) and echec.group(1) in noms, (
        f"`etape_en_echec` vaut {r.get('etape_en_echec')!r}. Dans ci/run-12.log, cherchez la "
        "ligne « échec » : elle nomme l'étape comme ci.yml la nomme (name:)."
    )
    commande = nettoyer(r.get("commande_locale"))
    assert "ruff check" in commande, (
        f"`commande_locale` vaut {commande!r}. La première commande de l'étape en échec, "
        "lancée dans le dépôt, rejoue le même échec sur votre poste."
    )
    res = git("log", "--format=%H", "-S", "import sys", "--", "src/certcheck/certificats.py", cwd=depot_livre())
    fautif = res.stdout.split()[0]
    donne = nettoyer(r.get("commit_fautif")).lower()
    assert len(donne) >= 7 and fautif.startswith(donne), (
        f"`commit_fautif` vaut {donne!r}. `git log --oneline` liste les commits, et "
        "`git show <empreinte>` montre ce que chacun a changé : cherchez celui qui touche "
        "à la décision, dans src/certcheck/certificats.py."
    )


def test_le_defaut_est_corrige() -> None:
    outil = exiger_executable(projet())
    graine = random.SystemRandom().randrange(10**6)
    rng = tirage(graine)
    for _ in range(3):
        hotes = rng.sample(sorted(EXPIRATIONS), 3)
        limite = hotes[0]
        seuil = rng.randint(7, 60)
        jour = EXPIRATIONS[limite] - timedelta(days=seuil)
        with tempfile.TemporaryDirectory(prefix="intervenir-") as tmp:
            inventaire = ecrire_inventaire(Path(tmp), hotes)
            res = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil), "--format", "json",
                         cwd=Path(tmp), env={"CERTCHECK_NOW": jour.isoformat()})
        try:
            lus = {c["host"]: c["status"] for c in json.loads(res.sortie)["certificates"]}
        except (ValueError, KeyError, TypeError):
            pytest.fail(f"La sortie --format json n'est plus exploitable. Graine {graine}.\n  {res.resume()}",
                        pytrace=False)
        for hote in hotes:
            jours = (EXPIRATIONS[hote] - jour).days
            attendu = "expired" if jours < 0 else "warning" if jours <= seuil else "ok"
            assert lus.get(hote) == attendu, (
                f"{hote} expire dans {jours} jours, seuil {seuil} : {attendu} attendu, {lus.get(hote)!r} "
                f"obtenu (le seuil est inclusif). Graine {graine}.\n  {res.resume()}"
            )
        attendu_code = 1 if any(v != "ok" for v in lus.values()) else 0
        assert res.code == attendu_code, f"Code {res.code}, attendu {attendu_code}. Graine {graine}.\n  {res.resume()}"


def test_les_tests_sont_verts_et_complets() -> None:
    dossier = projet()
    noms = set()
    for fichier in (dossier / "tests").rglob("test_*.py"):
        try:
            noms |= {n.name for n in ast.walk(ast.parse(fichier.read_text(encoding="utf-8")))
                     if isinstance(n, ast.FunctionDef)}
        except SyntaxError:
            continue
    manquants = TESTS_RECUS - noms
    assert not manquants, (
        f"Les tests reçus {sorted(manquants)} ont disparu : un test rouge signale un défaut, "
        "on corrige le code, on ne supprime pas le témoin."
    )
    uv = exiger_outil("uv")
    with copie_temporaire(dossier) as copie:
        res = executer([uv, "run", "--quiet", "--directory", str(copie), "pytest", "-q", "-p", "no:cacheprovider"],
                       timeout=300)
    assert res.returncode == 0, (
        "`uv run pytest` n'est pas vert sur votre version :\n" + (res.stdout + res.stderr).strip()[-1500:]
    )


def test_la_qualite_et_la_ci_passent() -> None:
    dossier = projet()
    with copie_temporaire(dossier) as copie:
        for etape in etapes_livrees():
            commande = etape.get("run")
            if not commande:
                continue
            res = executer(["bash", "-e", "-c", commande], cwd=copie, timeout=600)
            assert res.returncode == 0, (
                f"L'étape de CI « {etape['name']} » échoue sur votre version, rejouée dans une "
                f"copie propre :\n$ {commande.strip()}\n" + (res.stdout + res.stderr).strip()[-1500:]
            )
