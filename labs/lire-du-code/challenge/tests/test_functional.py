"""Lire le code d'une application Python : cinq contrôles, vingt points chacun.

## Ce qui est noté

Les réponses de `reponses.yaml`, confrontées à ce que le paquet certcheck
fait réellement. Rien n'est recopié en dur quand on peut le recalculer :

- le point d'entrée vient de `[project.scripts]` du pyproject.toml, et les
  modules internes de l'arbre syntaxique (module `ast`) du module désigné ;
- le sous-processus, la fonction réseau et la variable qui la déclenche se
  lisent aussi dans l'arbre syntaxique du code ;
- le code de sortie et l'hôte mal classé viennent d'une exécution par
  `uv run` du point de départ intact, dans une copie ;
- l'empreinte du commit vient d'une recherche `git log -S` dans le bundle.

Une réponse juste est donc une réponse que la lecture ou l'exécution prouvent.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest

from conftest import copie_temporaire, executer, exiger_outil, exiger_workdir, git, lire_yaml, workdir_lab

WORKDIR = workdir_lab(__file__)
LAB_ID = "lire-du-code"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
PAQUET = FIXTURES / "src" / "certcheck"
JOUR = "2026-06-01"

# Les noms de la leçon : erreur avalée, secret exposé, appel réseau sans délai,
# action répétée à chaque exécution, injection de commande.
DEFAUTS_REELS = {"erreur-avalee", "secret-expose", "appel-reseau-sans-delai", "action-repetee"}
# Les anciens noms restent acceptés : ils désignent les mêmes défauts.
SYNONYMES = {"jeton-dans-l-url": "secret-expose", "ticket-en-double": "action-repetee"}
DEFAUTS_PROPOSES = DEFAUTS_REELS | {
    "code-de-sortie-muet", "injection-de-commande", "seuil-exclusif",
    "fichier-temporaire-predictible", "dependance-non-epinglee",
}


@pytest.fixture(scope="module")
def reponses() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    return lire_yaml(WORKDIR / "reponses.yaml")


def _texte(valeur: object) -> str:
    return str(valeur or "").strip()


def _module_court(valeur: object) -> str:
    """certcheck.forge, src/certcheck/forge.py ou forge : toujours « forge »."""
    nom = _texte(valeur).lower().removeprefix("src/").removesuffix(".py").replace("/", ".")
    return nom.removeprefix("certcheck.")


def _arbre(module: str) -> ast.Module:
    return ast.parse((PAQUET / f"{module}.py").read_text(encoding="utf-8"))


def _point_d_entree() -> str:
    projet = tomllib.loads((FIXTURES / "pyproject.toml").read_text(encoding="utf-8"))
    return projet["project"]["scripts"]["certcheck"]


def test_le_point_d_entree_et_ses_modules_sont_nommes(reponses: dict) -> None:
    attendu = _point_d_entree()
    donne = _texte(reponses.get("point_d_entree")).replace(" ", "")
    assert donne == attendu, (
        "point_d_entree : ce n'est pas la fonction que lance la commande `certcheck`. "
        "Ouvrez pyproject.toml, table [project.scripts] : la valeur associée à "
        "`certcheck` a la forme module:fonction. Ne devinez pas `main` : le nom se lit."
    )
    module = attendu.partition(":")[0].removeprefix("certcheck.")
    internes = set()
    for noeud in ast.walk(_arbre(module)):
        if isinstance(noeud, ast.ImportFrom) and noeud.module and noeud.module.startswith("certcheck."):
            internes.add(noeud.module.removeprefix("certcheck."))
        elif isinstance(noeud, ast.Import):
            internes |= {a.name.removeprefix("certcheck.") for a in noeud.names if a.name.startswith("certcheck.")}
    lus = {_module_court(v) for v in reponses.get("modules_internes") or [] if _texte(v)}
    manquants, en_trop = sorted(internes - lus), sorted(lus - internes)
    assert not manquants and not en_trop, (
        f"modules_internes : il en manque {len(manquants)}, et {len(en_trop)} ne sont pas "
        f"importés par {module}.py. Lisez TOUT le fichier, pas seulement l'en-tête : un "
        "import peut se trouver dans le corps d'une fonction, et il ne s'exécute qu'en "
        "passant par cette branche. `grep -n import` le montre."
    )


def _sous_processus() -> set[str]:
    programmes = set()
    for fichier in PAQUET.glob("*.py"):
        for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
            if (isinstance(noeud, ast.Call) and isinstance(noeud.func, ast.Attribute)
                    and isinstance(noeud.func.value, ast.Name) and noeud.func.value.id == "subprocess"
                    and noeud.args and isinstance(noeud.args[0], ast.List) and noeud.args[0].elts
                    and isinstance(noeud.args[0].elts[0], ast.Constant)):
                programmes.add(str(noeud.args[0].elts[0].value))
    return programmes


def _fonction_reseau() -> str:
    for fichier in PAQUET.glob("*.py"):
        for fonction in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
            if isinstance(fonction, ast.FunctionDef) and any(
                isinstance(n, ast.Attribute) and n.attr == "urlopen" for n in ast.walk(fonction)
            ):
                return fonction.name
    pytest.fail("Aucune fonction n'appelle urlopen : le point de départ est abîmé.", pytrace=False)


def _variables_qui_declenchent(fonction: str) -> set[str]:
    module = _point_d_entree().partition(":")[0].removeprefix("certcheck.")
    variables = set()
    for noeud in ast.walk(_arbre(module)):
        if isinstance(noeud, ast.If) and any(
            isinstance(n, ast.Name) and n.id == fonction
            for instruction in noeud.body for n in ast.walk(instruction)
        ):
            variables |= {str(c.value) for c in ast.walk(noeud.test)
                          if isinstance(c, ast.Constant) and isinstance(c.value, str)}
    return variables


def test_les_effets_de_bord_sont_identifies(reponses: dict) -> None:
    programmes = _sous_processus()
    donne = Path(_texte(reponses.get("sous_processus"))).name.lower()
    assert programmes and donne in programmes, (
        "sous_processus : ce n'est pas le programme que certcheck lance. Cherchez les "
        "appels au module subprocess : le premier élément de la liste passée à "
        "subprocess.run est le programme exécuté."
    )
    fonction = _fonction_reseau()
    donnee = _texte(reponses.get("fonction_appel_reseau")).removesuffix("()")
    donnee = donnee.replace(":", ".").rsplit(".", 1)[-1]
    assert donnee == fonction, (
        "fonction_appel_reseau : ce n'est pas la fonction qui envoie la requête. Cherchez "
        "qui appelle urllib.request.urlopen (ou requests, httpx...) : c'est là que le "
        "programme sort du poste."
    )
    variable = _texte(reponses.get("variable_appel_reseau")).lstrip("$")
    assert variable in _variables_qui_declenchent(fonction), (
        "variable_appel_reseau : ce n'est pas la variable qui déclenche l'appel. Remontez "
        f"de {fonction} jusqu'à l'endroit où le point d'entrée l'appelle : quelle "
        "condition le protège ?"
    )


def test_l_execution_sans_risque_est_observee(reponses: dict) -> None:
    uv = exiger_outil("uv")
    # L'exécution de référence, sur le point de départ intact (vos éventuelles
    # retouches du code ne comptent pas) : sans FORGE_*, aucun appel réseau.
    with copie_temporaire(FIXTURES) as copie:
        res = executer([uv, "run", "--quiet", "--project", str(copie), "certcheck",
                        "--inventory", "inventaire.txt"], cwd=copie,
                       env={"CERTCHECK_NOW": JOUR}, timeout=300)
    classes = {}
    for ligne in res.stdout.splitlines():
        champs = ligne.split("\t")
        if len(champs) >= 2:
            classes[champs[0]] = champs[1]
    if not classes:
        pytest.fail(f"Le point de départ ne tourne pas (code {res.returncode}) :\n"
                    f"{(res.stdout + res.stderr).strip()[-800:]}", pytrace=False)
    mal_classe = next((h for h, s in classes.items()
                       if s != "error" and not (FIXTURES / "certs" / f"{h}.pem").exists()), "")
    assert reponses.get("code_de_sortie") == res.returncode, (
        "code_de_sortie : ce n'est pas le code que rend certcheck sur l'inventaire fourni, "
        f"au {JOUR}. Lancez `CERTCHECK_NOW={JOUR} uv run certcheck --inventory "
        "inventaire.txt`, puis `echo $?` immédiatement après."
    )
    assert _texte(reponses.get("hote_mal_classe")) == mal_classe, (
        "hote_mal_classe : ce n'est pas l'hôte classé à tort. Comparez chaque ligne de la "
        "sortie à la liste des fichiers de certs/ : lequel est dit valide sans certificat ?"
    )


def test_les_defauts_reels_sont_nommes(reponses: dict) -> None:
    lus = {_texte(v).lower() for v in reponses.get("defauts") or [] if _texte(v)}
    donnees = {SYNONYMES.get(d, d) for d in lus}
    inconnus = sorted(donnees - DEFAUTS_PROPOSES)
    assert not inconnus, f"defauts : {inconnus} ne font pas partie de la liste proposée."
    oublies = len(DEFAUTS_REELS - donnees)
    faux = len(donnees - DEFAUTS_REELS)
    assert not oublies and not faux, (
        f"defauts : {oublies} défaut(s) réel(s) oublié(s), {faux} défaut(s) cité(s) à "
        "tort. Chaque défaut se prouve par une ligne du code : ce que devient une "
        "exception dans analyser, où part le jeton dans forge.py, ce que urlopen attend "
        "si la forge ne répond pas, et ce qui se passe si certcheck tourne deux nuits de "
        "suite. Un défaut qu'aucune ligne ne montre n'en est pas un."
    )


def test_le_commit_de_l_erreur_avalee_est_retrouve(reponses: dict, tmp_path: Path) -> None:
    clone = tmp_path / "historique"
    res = executer(["git", "clone", "-q", str(WORKDIR / "historique.bundle"), str(clone)], timeout=60)
    assert res.returncode == 0, f"historique.bundle illisible : {res.stderr.strip()}"
    trouve = git("log", "-S", "except Exception", "--format=%H", "--reverse", "--",
                 "src/certcheck/certificats.py", cwd=clone)
    attendu = trouve.stdout.split()[0]
    donne = _texte(reponses.get("commit_erreur_avalee")).lower()
    assert len(donne) >= 7 and attendu.startswith(donne), (
        "commit_erreur_avalee : ce n'est pas le commit qui a introduit l'erreur avalée. "
        "`git log -S 'except Exception' -- src/certcheck/certificats.py` liste les "
        "commits qui ont ajouté ou retiré cette chaîne ; `git blame` donne celui qui a "
        "écrit la ligne actuelle. Sept caractères au moins."
    )
