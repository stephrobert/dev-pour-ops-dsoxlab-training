"""Lire et modifier un petit script : cinq contrôles, vingt points chacun.

## Ce que ce lab note

Les trois premiers contrôles lisent `reponses.yaml` : ce que l'apprenant a
compris du script AVANT d'y toucher. Les réponses attendues ne sont pas
écrites ici : elles se recalculent en lisant et en exécutant le script tel
qu'il a été livré (`fixtures/certcheck.py`), si bien qu'un changement du point
de départ ne laisse pas un corrigé périmé.

Les deux derniers contrôles jugent la modification demandée, en boîte noire :
on lance `python3 certcheck.py` du répertoire de travail sur des inventaires et
des dates tirés au hasard, et on lit le verdict affiché et le code de sortie.
Le code n'est jamais lu.
"""

from __future__ import annotations

import ast
import random
import shutil
import tempfile
from datetime import date, timedelta
from functools import cache
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    ecrire_inventaire,
    executer,
    exiger_workdir,
    lire_yaml,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "lire-du-code"
ORIGINAL = Path(__file__).resolve().parents[2] / "fixtures" / "certcheck.py"
JOUR_DE_LECTURE = "2026-10-31"
ROLES = {"verifier-expiration", "renouveler-certificats", "deployer-certificats", "sauvegarder-certificats"}


def reponses() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    return lire_yaml(WORKDIR / "reponses.yaml")


def python() -> str:
    chemin = shutil.which("python3")
    if not chemin:
        pytest.fail("python3 est introuvable sur le PATH.", pytrace=False)
    return chemin


def jouer(script: Path, dossier: Path, *args: str, jour: str) -> tuple[int, dict[str, str], str]:
    """Le code de sortie, le verdict par hôte, et la sortie brute du script."""
    res = executer([python(), str(script), *args], cwd=dossier, env={"CERTCHECK_NOW": jour}, timeout=60)
    verdicts = {}
    for ligne in res.stdout.splitlines():
        champs = ligne.split("\t")
        if len(champs) >= 2:
            verdicts[champs[0].strip()] = champs[1].strip()
    return res.returncode, verdicts, f"code {res.returncode}\n{res.stdout}{res.stderr}"


@cache
def lecture_originale() -> tuple[int, dict[str, str]]:
    """Ce que le script livré affiche au jour de lecture, sur l'inventaire livré."""
    with tempfile.TemporaryDirectory(prefix="lab-lire-") as tmp:
        dossier = Path(tmp)
        shutil.copytree(ORIGINAL.parent / "certs", dossier / "certs")
        shutil.copy(ORIGINAL.parent / "inventaire.txt", dossier / "inventaire.txt")
        code, verdicts, _ = jouer(ORIGINAL, dossier, jour=JOUR_DE_LECTURE)
    return code, verdicts


def nettoyer(valeur: object) -> str:
    return str(valeur or "").strip().strip("`").strip()


def test_le_role_du_script() -> None:
    r = reponses()
    role = nettoyer(r.get("role")).lower()
    assert role in ROLES, f"`role` vaut {role!r} : choisissez une valeur de la liste de reponses.yaml."
    assert role == "verifier-expiration", (
        f"`role` vaut {role!r}. Relisez la docstring en tête de certcheck.py et ce que "
        "main() affiche : le script ne crée, ne copie ni n'archive aucun certificat."
    )
    externe = nettoyer(r.get("programme_externe")).lower()
    assert externe == "openssl", (
        f"`programme_externe` vaut {externe!r}. Cherchez l'appel à subprocess.run : le "
        "premier élément de la liste est le programme lancé."
    )


def test_les_entrees_du_script() -> None:
    r = reponses()
    option = nettoyer(r.get("option_seuil"))
    assert option == "--days", (
        f"`option_seuil` vaut {option!r}. Les options sont déclarées par "
        "parser.add_argument dans main() ; `python3 certcheck.py --help` les liste."
    )
    variable = nettoyer(r.get("variable_date"))
    assert variable == "CERTCHECK_NOW", (
        f"`variable_date` vaut {variable!r}. Lisez la fonction aujourd_hui() : elle lit "
        "une variable par os.environ.get."
    )
    arbre = ast.parse(ORIGINAL.read_text(encoding="utf-8"))
    fonctions = {n.name for n in ast.walk(arbre) if isinstance(n, ast.FunctionDef)}
    fonction = nettoyer(r.get("fonction_verdict")).removesuffix("()")
    assert fonction in fonctions, (
        f"`fonction_verdict` vaut {fonction!r}, qui n'est pas une fonction du script "
        f"(elles sont : {', '.join(sorted(fonctions))})."
    )
    assert fonction == "statut", (
        f"`fonction_verdict` vaut {fonction!r}. Suivez main() : la valeur affichée en "
        "deuxième colonne vient d'un appel de fonction, c'est elle qui décide."
    )


def test_ce_que_montre_l_execution() -> None:
    r = reponses()
    code, verdicts = lecture_originale()
    assert r.get("code_de_sortie") == code, (
        f"`code_de_sortie` vaut {r.get('code_de_sortie')!r}. Lancez le script reçu, puis "
        "`echo \"code : $?\"` aussitôt : $? est le code de la dernière commande."
    )
    alertes = {h for h, v in verdicts.items() if v == "warning"}
    donnees = r.get("hotes_en_alerte") or []
    donnees = {nettoyer(h) for h in donnees} if isinstance(donnees, list) else set()
    assert donnees == alertes, (
        f"`hotes_en_alerte` vaut {sorted(donnees)} : relisez la deuxième colonne de la "
        "sortie et listez tous les hôtes marqués warning, et seulement eux."
    )
    jour = date.fromisoformat(JOUR_DE_LECTURE)
    au_seuil = sorted(h for h in verdicts if (EXPIRATIONS[h] - jour).days == 30)
    assert nettoyer(r.get("hote_au_seuil")) in au_seuil, (
        f"`hote_au_seuil` vaut {r.get('hote_au_seuil')!r}. La troisième colonne donne le "
        "nombre de jours restants : cherchez la ligne à 30 jours, et regardez son verdict."
    )


def _parc_au_hasard(rng: random.Random) -> tuple[str, int, timedelta]:
    hote = rng.choice(sorted(EXPIRATIONS))
    seuil = rng.randint(7, 60)
    return hote, seuil, timedelta(days=seuil)


def test_le_seuil_est_inclusif() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    script = WORKDIR / "certcheck.py"
    graine = random.SystemRandom().randrange(10**6)
    rng = tirage(graine)
    for _ in range(3):
        hote, seuil, ecart = _parc_au_hasard(rng)
        with tempfile.TemporaryDirectory(prefix="lab-lire-") as tmp:
            dossier = Path(tmp)
            ecrire_inventaire(dossier, [hote])
            pile = (EXPIRATIONS[hote] - ecart).isoformat()
            code, verdicts, brut = jouer(script, dossier, "--days", str(seuil), jour=pile)
            assert verdicts.get(hote) == "warning", (
                f"Le certificat de {hote} expire dans exactement {seuil} jours, avec un seuil "
                f"de {seuil} : il doit passer en warning (le seuil est inclusif). Graine {graine}.\n{brut}"
            )
            assert code == 1, f"Un certificat en warning doit donner le code 1. Graine {graine}.\n{brut}"
            veille = (EXPIRATIONS[hote] - ecart - timedelta(days=1)).isoformat()
            code, verdicts, brut = jouer(script, dossier, "--days", str(seuil), jour=veille)
            assert verdicts.get(hote) == "ok", (
                f"À {seuil + 1} jours de l'expiration, avec un seuil de {seuil}, {hote} doit "
                f"rester ok : seul le cas d'égalité change. Graine {graine}.\n{brut}"
            )
            assert code == 0, f"Un parc entièrement ok doit sortir en 0. Graine {graine}.\n{brut}"


def test_un_certificat_expire_est_signale() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    script = WORKDIR / "certcheck.py"
    graine = random.SystemRandom().randrange(10**6)
    rng = tirage(graine)
    hote = rng.choice(sorted(EXPIRATIONS))
    apres = (EXPIRATIONS[hote] + timedelta(days=rng.randint(1, 400))).isoformat()
    with tempfile.TemporaryDirectory(prefix="lab-lire-") as tmp:
        dossier = Path(tmp)
        ecrire_inventaire(dossier, [hote])
        code, verdicts, brut = jouer(script, dossier, jour=apres)
    assert verdicts.get(hote) == "expired", (
        f"Au {apres}, le certificat de {hote} a déjà expiré : le verdict doit être "
        f"`expired`, pas {verdicts.get(hote)!r}. Ajoutez ce cas dans la fonction qui "
        f"décide, avant les autres. Graine {graine}.\n{brut}"
    )
    assert code == 1, f"Un certificat expiré demande une action : code 1. Graine {graine}.\n{brut}"
