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
  livré à la date du ticket, l'étape en échec en relisant `ci/run-12.log`.
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
import shutil
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
    message,
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
        pytest.fail(message(
            en="The repository is not cloned: `git clone depot.bundle certcheck`, then work in certcheck/.",
            fr="Le dépôt n'est pas cloné : `git clone depot.bundle certcheck`, puis travaillez dans certcheck/.",
        ),
                    pytrace=False)
    return chemin


def nettoyer(valeur: object) -> str:
    return str(valeur or "").strip().strip("`").strip().strip("'\"").strip()


@cache
def depot_livre() -> Path:
    """Le dépôt livré, cloné une fois pour toute la session de contrôle."""
    dossier = Path(tempfile.mkdtemp(prefix="intervenir-livre-"))
    res = git("clone", "-q", str(LIVRE / "depot.bundle"), str(dossier / "certcheck"), cwd=dossier)
    assert res.returncode == 0, message(
        en=f"Cannot clone the shipped repository: {res.stderr.strip()[:300]}. "
        "This step belongs to the harness, not to the exam.",
        fr=f"Impossible de cloner le dépôt livré : {res.stderr.strip()[:300]}. "
        "Cette étape appartient au harnais, pas à l'épreuve.",
    )
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
    assert nettoyer(r.get("role")).lower() == "verifier-expiration", message(
        en="`role` does not match the tool's role.",
        fr="`role` ne correspond pas au rôle de l'outil.",
    )
    declaree = tomllib.loads((depot_livre() / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
    assert nettoyer(r.get("commande_declaree")) == declaree["certcheck"], message(
        en="`commande_declaree` does not match the command the project declares.",
        fr="`commande_declaree` ne correspond pas à la commande déclarée par le projet.",
    )
    seuil = 30
    mal_classes = sorted(h for h, s in statuts_livres().items()
                         if s == "ok" and (EXPIRATIONS[h] - JOUR_DU_TICKET).days <= seuil)
    assert nettoyer(r.get("hote_mal_classe")) in mal_classes, message(
        en="`hote_mal_classe` does not name the host misclassified at the ticket's date.",
        fr="`hote_mal_classe` ne désigne pas l'hôte mal classé à la date du ticket.",
    )


def test_la_ci_est_lue_et_le_defaut_localise() -> None:
    r = reponses()
    journal = (LIVRE / "ci" / "run-12.log").read_text(encoding="utf-8")
    echec = re.search(r"== Étape « (.+?) » : échec", journal)
    assert echec, message(
        en="the log as shipped is unreadable",
        fr="journal livré illisible",
    )
    noms = {e["name"] for e in etapes_livrees()}
    assert nettoyer(r.get("etape_en_echec")) == echec.group(1) and echec.group(1) in noms, message(
        en="`etape_en_echec` does not name the failing step as ci.yml names it.",
        fr="`etape_en_echec` ne nomme pas l'étape en échec telle que ci.yml la nomme.",
    )
    commande = nettoyer(r.get("commande_locale"))
    assert "ruff check" in commande, message(
        en="`commande_locale` does not replay that step's failure.",
        fr="`commande_locale` ne rejoue pas l'échec de cette étape.",
    )
    donne = nettoyer(r.get("fichier_du_defaut")).removeprefix("./").removeprefix("certcheck/")
    assert donne == "src/certcheck/certificats.py", message(
        en="`fichier_du_defaut` does not name the file of the ticket's defect.",
        fr="`fichier_du_defaut` ne désigne pas le fichier du défaut du ticket.",
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
            pytest.fail(message(
                en=f"The --format json output is no longer usable. Seed {graine}.\n  {res.resume()}",
                fr=f"La sortie --format json n'est plus exploitable. Graine {graine}.\n  {res.resume()}",
            ),
                        pytrace=False)
        for hote in hotes:
            jours = (EXPIRATIONS[hote] - jour).days
            attendu = "expired" if jours < 0 else "warning" if jours <= seuil else "ok"
            assert lus.get(hote) == attendu, message(
                en=f"{hote} expires in {jours} days, threshold {seuil}: {attendu} expected, {lus.get(hote)!r} "
                f"obtained (the threshold is inclusive). Seed {graine}.\n  {res.resume()}",
                fr=f"{hote} expire dans {jours} jours, seuil {seuil} : {attendu} attendu, {lus.get(hote)!r} "
                f"obtenu (le seuil est inclusif). Graine {graine}.\n  {res.resume()}",
            )
        attendu_code = 1 if any(v != "ok" for v in lus.values()) else 0
        assert res.code == attendu_code, message(
            en=f"Code {res.code}, expected {attendu_code}. Seed {graine}.\n  {res.resume()}",
            fr=f"Code {res.code}, attendu {attendu_code}. Graine {graine}.\n  {res.resume()}",
        )


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
    assert not manquants, message(
        en=f"The shipped tests {sorted(manquants)} have disappeared: a red test signals a defect, "
        "one fixes the code, one does not delete the witness.",
        fr=f"Les tests reçus {sorted(manquants)} ont disparu : un test rouge signale un défaut, "
        "on corrige le code, on ne supprime pas le témoin.",
    )
    uv = exiger_outil("uv")
    with copie_temporaire(dossier) as copie:
        res = executer([uv, "run", "--quiet", "--directory", str(copie), "pytest", "-q", "-p", "no:cacheprovider"],
                       timeout=300)
    assert res.returncode == 0, message(
        en="`uv run pytest` is not green on your version:\n" + (res.stdout + res.stderr).strip()[-1500:],
        fr="`uv run pytest` n'est pas vert sur votre version :\n" + (res.stdout + res.stderr).strip()[-1500:],
    )
    # Les tests TELS QUE REÇUS, rejoués contre votre code : modifier un test pour le
    # faire passer ne corrige rien, et ne fait pas passer ce contrôle.
    with copie_temporaire(dossier) as copie:
        recus = copie / "tests"
        if recus.exists():
            shutil.rmtree(recus)
        shutil.copytree(depot_livre() / "tests", recus)
        res = executer([uv, "run", "--quiet", "--directory", str(copie), "pytest", "-q", "-p", "no:cacheprovider"],
                       timeout=300)
    assert res.returncode == 0, message(
        en="The shipped tests, replayed as they are against your code, do not pass: the defect is "
        "still there.\n" + (res.stdout + res.stderr).strip()[-1500:],
        fr="Les tests reçus, rejoués tels quels contre votre code, ne passent pas : le défaut est "
        "toujours là.\n" + (res.stdout + res.stderr).strip()[-1500:],
    )


def test_la_qualite_et_la_ci_passent() -> None:
    dossier = projet()
    with copie_temporaire(dossier) as copie:
        for etape in etapes_livrees():
            commande = etape.get("run")
            if not commande:
                continue
            res = executer(["bash", "-e", "-c", commande], cwd=copie, timeout=600)
            assert res.returncode == 0, message(
                en=f"The CI step \"{etape['name']}\" fails on your version, replayed in a "
                f"clean copy:\n$ {commande.strip()}\n" + (res.stdout + res.stderr).strip()[-1500:],
                fr=f"L'étape de CI « {etape['name']} » échoue sur votre version, rejouée dans une "
                f"copie propre :\n$ {commande.strip()}\n" + (res.stdout + res.stderr).strip()[-1500:],
            )
