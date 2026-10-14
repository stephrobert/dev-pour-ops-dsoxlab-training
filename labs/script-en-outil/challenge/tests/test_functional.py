"""Comprendre un outil, puis le modifier : cinq contrôles, vingt points chacun.

## Les trois premiers contrôles lisent `reponses.yaml`

Ils notent ce que l'apprenant a compris du projet AVANT d'y toucher : le
fichier qui déclare la commande, ce qu'il déclare, où vit la décision, quel
fichier cron lance, et les codes de sortie observés. Rien n'est écrit en dur :
la commande déclarée se relit dans le `pyproject.toml` livré, et les codes se
recalculent en lançant le projet livré (`fixtures/`) dans une copie.

## Les deux derniers jugent la modification, en boîte noire

On lance `bin/certcheck` comme cron ou un pipeline, et seul compte ce qu'un
appelant observe : sortie standard, sortie d'erreur et code de sortie.
"""

from __future__ import annotations

import shutil
import tempfile
import tomllib
from datetime import timedelta
from functools import cache
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    ecrire_inventaire,
    exiger_executable,
    exiger_workdir,
    lancer,
    lire_json_sortie,
    lire_yaml,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "script-en-outil"
LIVRE = Path(__file__).resolve().parents[2] / "fixtures"


@pytest.fixture(scope="module")
def outil() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return exiger_executable(WORKDIR)


def reponses() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    return lire_yaml(WORKDIR / "reponses.yaml")


def chemin(valeur: object) -> str:
    return str(valeur or "").strip().strip("`").removeprefix("./").strip()


@cache
def codes_livres() -> dict[str, int]:
    """Les codes de sortie du projet tel qu'il a été livré, mesurés dans une copie."""
    with tempfile.TemporaryDirectory(prefix="lab-outil-") as tmp:
        copie = Path(tmp) / "projet"
        shutil.copytree(LIVRE, copie, ignore=shutil.ignore_patterns(".venv", "__pycache__", "reponses.yaml"))
        outil = copie / "bin" / "certcheck"
        env = {"CERTCHECK_NOW": "2026-06-01"}
        return {
            "code_inventaire_fourni": lancer(outil, cwd=copie, env=env).code,
            "code_usage_incorrect": lancer(outil, "--format", "xml", cwd=copie, env=env).code,
            "code_inventaire_absent": lancer(outil, "--inventory", "absent.txt", cwd=copie, env=env).code,
        }


def test_la_commande_est_declaree_par_le_projet() -> None:
    r = reponses()
    assert chemin(r.get("fichier_declaration")) == "pyproject.toml", (
        f"`fichier_declaration` vaut {r.get('fichier_declaration')!r}. Une commande "
        "installée par un projet Python se déclare dans un fichier de configuration du "
        "projet, sous une table [project.scripts]."
    )
    declaree = tomllib.loads((LIVRE / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]["certcheck"]
    assert chemin(r.get("commande_declaree")) == declaree, (
        f"`commande_declaree` vaut {r.get('commande_declaree')!r} : recopiez la valeur de "
        "`certcheck = ...` dans [project.scripts], sous la forme module:fonction."
    )


def test_ou_est_quoi() -> None:
    r = reponses()
    module = chemin(r.get("module_decision"))
    assert module == "src/certcheck/certificats.py", (
        f"`module_decision` vaut {module!r}. Le code vit sous src/certcheck/ ; "
        "`grep -n \"def statut\" -r src` dit dans quel fichier."
    )
    assert chemin(r.get("lanceur")) == "bin/certcheck", (
        f"`lanceur` vaut {r.get('lanceur')!r}. CONTRAT.md dit quel fichier cron et les "
        "pipelines appellent : c'est un petit script shell exécutable."
    )


def test_les_codes_de_sortie_observes() -> None:
    r = reponses()
    for cle, attendu in codes_livres().items():
        assert r.get(cle) == attendu, (
            f"`{cle}` vaut {r.get(cle)!r}. Lancez la commande indiquée dans reponses.yaml "
            "sur le projet reçu, puis `echo $?` aussitôt. CONTRAT.md dit ce que chaque "
            "code signifie."
        )


def test_le_seuil_vient_de_l_environnement(outil: Path, tmp_path: Path) -> None:
    # Tabulation comme séparateur, et un lancement depuis un autre dossier :
    # les chemins des certificats se résolvent depuis celui de l'inventaire.
    inventaire = ecrire_inventaire(tmp_path / "parc", ["api-01", "web-01"], separateur="\t")
    jour = EXPIRATIONS["api-01"] - timedelta(days=20)  # api-01 expire dans 20 jours
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()

    def jouer(*args: str, days: str):
        return lancer(outil, "--inventory", str(inventaire), "--format", "json", *args, cwd=ailleurs,
                      env={"CERTCHECK_NOW": jour.isoformat(), "CERTCHECK_DAYS": days})

    res = jouer(days="10")
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    assert statuts == {"api-01": "ok", "web-01": "ok"} and res.code == 0, (
        "CERTCHECK_DAYS=10 doit laisser api-01, à 20 jours, en ok, et le code à 0 "
        "(inventaire séparé par une tabulation, lancé depuis un autre dossier : les "
        f"chemins des certificats sont relatifs à l'inventaire).\n  {res.resume()}"
    )
    res = jouer(days="45")
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    assert statuts.get("api-01") == "warning" and res.code == 1, (
        "CERTCHECK_DAYS=45 doit faire passer api-01, à 20 jours, en warning, code 1 : "
        f"la variable est-elle lue ?\n  {res.resume()}"
    )
    res = jouer("--days", "10", days="45")
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    assert statuts.get("api-01") == "ok" and res.code == 0, (
        "--days 10 doit l'emporter sur CERTCHECK_DAYS=45 : api-01 reste ok, code 0. "
        f"L'option gagne toujours sur la variable.\n  {res.resume()}"
    )
    res = jouer(days="dix")
    assert res.code == 2 and res.erreurs.strip() and not res.sortie.strip(), (
        "CERTCHECK_DAYS=dix est une configuration invalide : code 2, un message sur la "
        f"sortie d'erreur, rien sur la sortie standard.\n  {res.resume()}"
    )


def test_les_erreurs_vont_sur_la_sortie_d_erreur(outil: Path, tmp_path: Path) -> None:
    inventaire = ecrire_inventaire(tmp_path, ["web-01", "vpn-01"], absents=["web-03"])
    res = lancer(outil, "--inventory", str(inventaire), "--format", "json", cwd=tmp_path,
                 env={"CERTCHECK_NOW": "2026-06-01"})
    donnees = lire_json_sortie(res)  # échoue si un message pollue la sortie standard
    lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
    absent = lus.get("web-03", {})
    assert absent.get("status") == "error" and absent.get("days_left") is None, (
        "Le certificat de web-03 n'existe pas : il figure dans le JSON en status error, "
        f"days_left null. Il ne disparaît pas, et il ne passe pas pour valide.\n  {res.resume()}"
    )
    assert "web-03" in res.erreurs, (
        "Le problème de web-03 doit être signalé sur la SORTIE D'ERREUR, en le nommant : "
        "la sortie standard ne porte que le document JSON, qu'un programme va lire. "
        f"`log.error(...)` ou `print(..., file=sys.stderr)`.\n  {res.resume()}"
    )
    res = lancer(outil, "--inventory", str(tmp_path / "absent.txt"), cwd=tmp_path)
    assert res.code == 2 and res.erreurs.strip() and not res.sortie.strip(), (
        "Un inventaire absent : code 2, un message sur la sortie d'erreur, et RIEN sur la "
        "sortie standard (pas de trace Python non plus : l'erreur est attrapée et "
        f"expliquée).\n  {res.resume()}"
    )
    assert "Traceback" not in res.erreurs, (
        "Un inventaire absent produit une trace Python : attrapez l'erreur (ErreurUsage) "
        f"et écrivez un message d'une ligne qui nomme le fichier.\n  {res.resume()}"
    )
