"""Lire un code hérité : cinq contrôles, vingt points chacun.

## Ce qui est noté

Les réponses de `reponses.yaml`, confrontées à ce que le script fait
réellement. Rien n'est recopié en dur quand on peut le recalculer : le code
de sortie et l'hôte mal signalé viennent d'une exécution du script dans une
copie, et l'empreinte du commit d'une recherche `git log -S` dans le bundle.
Une réponse juste est donc une réponse que la lecture ou l'exécution
prouvent.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from conftest import copie_temporaire, executer, exiger_workdir, git, lire_yaml, workdir_lab

WORKDIR = workdir_lab(__file__)
LAB_ID = "lire-du-code"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

COMMANDES = {"openssl", "cut", "date", "curl", "dirname"}
DEFAUTS_REELS = {"erreur-avalee", "code-de-sortie-muet", "jeton-dans-l-url", "ticket-en-double"}
DEFAUTS_PROPOSES = DEFAUTS_REELS | {"injection-de-commande", "seuil-exclusif", "fichier-temporaire-predictible"}


@pytest.fixture(scope="module")
def reponses() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    return lire_yaml(WORKDIR / "reponses.yaml")


def _liste(valeur: object) -> set[str]:
    if not isinstance(valeur, list):
        return set()
    return {str(v).strip().lower() for v in valeur if str(v).strip()}


def test_les_commandes_externes_sont_toutes_nommees(reponses: dict) -> None:
    donnees = _liste(reponses.get("commandes_externes"))
    manquantes = sorted(COMMANDES - donnees)
    en_trop = sorted(donnees - COMMANDES)
    assert not manquantes and not en_trop, (
        f"commandes_externes : il en manque {len(manquantes)}, et {len(en_trop)} ne sont "
        "pas des commandes externes du script. Cherchez chaque mot en début de "
        "commande, y compris à l'intérieur de $( ) et derrière un pipe, puis "
        "demandez à Bash ce qu'il est : `type -t <mot>` répond builtin, keyword "
        "ou file."
    )


def test_les_effets_de_bord_sont_identifies(reponses: dict) -> None:
    fichier = str(reponses.get("fichier_ecrit") or "").strip()
    variable = str(reponses.get("variable_appel_reseau") or "").strip().lstrip("$")
    assert Path(fichier).name == "certcheck-rapport.txt", (
        "fichier_ecrit : ce n'est pas le fichier que le script écrit. Cherchez "
        "les redirections `>` et `>>`, et la variable qui porte leur cible."
    )
    assert variable == "FORGE_TOKEN", (
        "variable_appel_reseau : ce n'est pas la variable qui déclenche l'appel "
        "à la forge. Suivez le chemin jusqu'à `curl` : quelle condition le "
        "protège ?"
    )


def test_l_execution_sans_risque_est_observee(reponses: dict) -> None:
    # L'exécution de référence, sur le point de départ intact (vos éventuelles
    # retouches du script ne comptent pas) : sans FORGE_TOKEN, aucun appel réseau.
    with copie_temporaire(FIXTURES) as copie:
        res = executer(["bash", "certcheck.sh", "inventaire.txt"], cwd=copie, timeout=60)
    mal_signale = ""
    for ligne in res.stdout.splitlines():
        m = re.match(r"ALERTE\s+(\S+)", ligne)
        if m and not (FIXTURES / "certs" / f"{m.group(1)}.pem").exists():
            mal_signale = m.group(1)
    assert reponses.get("code_de_sortie") == res.returncode, (
        "code_de_sortie : ce n'est pas le code que rend le script sur "
        "l'inventaire fourni. Lancez-le, puis `echo $?` immédiatement après."
    )
    assert str(reponses.get("hote_mal_signale") or "").strip() == mal_signale, (
        "hote_mal_signale : ce n'est pas l'hôte signalé à tort. Comparez les "
        "lignes ALERTE à la liste des fichiers de certs/."
    )


def test_les_defauts_reels_sont_nommes(reponses: dict) -> None:
    donnees = _liste(reponses.get("defauts"))
    inconnus = sorted(donnees - DEFAUTS_PROPOSES)
    assert not inconnus, f"defauts : {inconnus} ne font pas partie de la liste proposée."
    oublies = len(DEFAUTS_REELS - donnees)
    faux = len(donnees - DEFAUTS_REELS)
    assert not oublies and not faux, (
        f"defauts : {oublies} défaut(s) réel(s) oublié(s), {faux} défaut(s) cité(s) "
        "à tort. Chaque défaut se prouve par une ligne du script : relisez ce que "
        "devient l'erreur d'openssl, ce que vaut `exit` en dernière ligne, où "
        "part le jeton, et ce qui se passe si le script tourne deux nuits de suite."
    )


def test_le_commit_de_l_erreur_avalee_est_retrouve(reponses: dict, tmp_path: Path) -> None:
    clone = tmp_path / "historique"
    res = executer(["git", "clone", "-q", str(WORKDIR / "historique.bundle"), str(clone)], timeout=60)
    assert res.returncode == 0, f"historique.bundle illisible : {res.stderr.strip()}"
    trouve = git("log", "-S", "2>/dev/null", "--format=%H", "--reverse", "--", "certcheck.sh", cwd=clone)
    attendu = trouve.stdout.split()[0]
    donne = str(reponses.get("commit_erreur_avalee") or "").strip().lower()
    assert len(donne) >= 7 and attendu.startswith(donne), (
        "commit_erreur_avalee : ce n'est pas le commit qui a introduit "
        "`2>/dev/null`. `git log -S '2>/dev/null' -- certcheck.sh` liste les "
        "commits qui ont ajouté ou retiré cette chaîne ; `git blame` donne celui "
        "qui a écrit la ligne actuelle. Sept caractères au moins."
    )
