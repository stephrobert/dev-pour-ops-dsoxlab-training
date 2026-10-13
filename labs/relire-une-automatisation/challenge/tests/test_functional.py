"""Relire une automatisation : cinq contrôles, vingt points chacun.

## Ce qui est noté

La revue de `revue.yaml`, confrontée au diff réel de la pull request n°42.
Les lignes attendues ne sont pas écrites en dur : le contrôle applique
`pr/0042.diff` (`git apply`) sur une copie du point de départ intact, puis
cherche dans les fichiers obtenus les marqueurs textuels de chacun des quatre
défauts semés. Un commentaire trouve un défaut s'il désigne le bon fichier, la
bonne catégorie, et une ligne située à deux lignes au plus de la zone fautive
(trois pour un test absent, qui se signale sur la déclaration de la fonction).
Trois défauts sur quatre suffisent : c'est une initiation à la revue.

Les deux derniers contrôles portent sur l'outillage qui voit les défauts
mécaniques avant toute revue : une configuration ruff versionnée, et
`ruff check` qui passe sur le code de base (lancé par uv, ruff 0.17.0 du
groupe dev).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest

from conftest import copie_temporaire, executer, exiger_outil, exiger_workdir, git, lire_yaml, workdir_lab

WORKDIR = workdir_lab(__file__)
LAB_ID = "relire-une-automatisation"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
CLI = "src/certcheck/cli.py"
MAINTENANCE = "src/certcheck/maintenance.py"
TEST_AJOUTE = "tests/test_maintenance.py"

CATEGORIES = {"erreur-avalee", "secret-affiche", "chemin-dangereux", "test-absent"}
VERDICTS = {"approuver", "demander-des-changements"}
LONGUEUR_MINIMALE = 25
FAUX_POSITIFS_TOLERES = 2
DEFAUTS_A_TROUVER = 3


@dataclass(frozen=True)
class Zone:
    """Un défaut semé : où il est, et quelles lignes le désignent."""

    categorie: str
    fichier: str
    debut: int
    fin: int

    def contient(self, fichier: str, ligne: int) -> bool:
        return fichier == self.fichier and self.debut <= ligne <= self.fin


# --- Le diff appliqué : d'où viennent les lignes attendues ----------------------


def _lignes(texte: str, motif: str, fichier: str) -> list[int]:
    trouvees = [n for n, ligne in enumerate(texte.splitlines(), 1) if motif in ligne]
    if not trouvees:
        pytest.fail(
            f"Marqueur « {motif} » introuvable dans {fichier} après application du "
            "diff : le point de départ du lab est abîmé. Relancez `dsoxlab run`.",
            pytrace=False,
        )
    return trouvees


def _zone(categorie: str, fichier: str, fichiers: dict[str, str], *motifs: str, marge: int = 2) -> Zone:
    lignes = [n for motif in motifs for n in _lignes(fichiers[fichier], motif, fichier)]
    return Zone(categorie, fichier, min(lignes) - marge, max(lignes) + marge)


@pytest.fixture(scope="module")
def zones() -> dict[str, list[Zone]]:
    """Catégorie -> zones acceptées, calculées sur le diff réellement appliqué."""
    with copie_temporaire(FIXTURES) as copie:
        res = git("apply", "pr/0042.diff", cwd=copie)
        assert res.returncode == 0, f"pr/0042.diff ne s'applique pas : {res.stderr.strip()}"
        fichiers = {
            nom: (copie / nom).read_text(encoding="utf-8")
            for nom in (CLI, MAINTENANCE, TEST_AJOUTE)
        }
    test_ajoute = len(fichiers[TEST_AJOUTE].splitlines())
    return {
        "secret-affiche": [_zone("secret-affiche", CLI, fichiers, "notification envoyée à {webhook}")],
        "erreur-avalee": [_zone("erreur-avalee", MAINTENANCE, fichiers, "except Exception:")],
        "chemin-dangereux": [_zone("chemin-dangereux", MAINTENANCE, fichiers,
                                   'os.environ.get("CERTCHECK_REPORT_DIR"', "shutil.rmtree(")],
        "test-absent": [
            _zone("test-absent", MAINTENANCE, fichiers, "def notifier(", marge=3),
            _zone("test-absent", CLI, fichiers, "if args.notify:", marge=3),
            Zone("test-absent", TEST_AJOUTE, 1, test_ajoute),
        ],
    }


# --- La revue -------------------------------------------------------------------


@dataclass(frozen=True)
class Commentaire:
    fichier: str
    ligne: int
    categorie: str
    commentaire: str
    proposition: str


def _chemin(valeur: object) -> str:
    chemin = str(valeur or "").strip().replace("\\", "/")
    for prefixe in ("./", "a/", "b/"):
        chemin = chemin.removeprefix(prefixe)
    return chemin


def _ligne(valeur: object) -> int:
    try:
        return int(str(valeur).strip())
    except ValueError:
        return -1


@pytest.fixture(scope="module")
def revue() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    return lire_yaml(WORKDIR / "revue.yaml")


@pytest.fixture(scope="module")
def commentaires(revue: dict) -> list[Commentaire]:
    brut = revue.get("commentaires")
    if not isinstance(brut, list):
        pytest.fail("`commentaires` doit être une liste (voir l'exemple dans revue.yaml).", pytrace=False)
    lus = []
    for element in brut:
        if not isinstance(element, dict):
            pytest.fail(
                "Chaque élément de `commentaires` est un dictionnaire portant fichier, "
                f"ligne, categorie, commentaire et proposition. Lu : {element!r}",
                pytrace=False,
            )
        lus.append(Commentaire(
            fichier=_chemin(element.get("fichier")),
            ligne=_ligne(element.get("ligne")),
            categorie=str(element.get("categorie") or "").strip().lower(),
            commentaire=str(element.get("commentaire") or "").strip(),
            proposition=str(element.get("proposition") or "").strip(),
        ))
    return lus


def _trouve(commentaires: list[Commentaire], zones: list[Zone]) -> bool:
    return any(z.categorie == c.categorie and z.contient(c.fichier, c.ligne)
               for c in commentaires for z in zones)


CONSEILS = {
    "secret-affiche": (
        "secret-affiche : la description dit que l'URL du webhook CONTIENT le jeton. "
        "Cherchez dans cli.py où cette URL est écrite sur une sortie : la sortie "
        "d'erreur d'un cron finit dans un courriel ou un journal."
    ),
    "erreur-avalee": (
        "erreur-avalee : « c'est géré », dit la description si le chat est "
        "indisponible. Regardez comment, dans maintenance.py : que devient un 401 "
        "ou une URL fausse ?"
    ),
    "chemin-dangereux": (
        "chemin-dangereux : que vaut le dossier purgé si CERTCHECK_REPORT_DIR n'est "
        "pas défini dans l'environnement du cron ? Suivez la valeur jusqu'à la "
        "suppression récursive."
    ),
    "test-absent": (
        "test-absent : la PR ajoute un test, et il passe. Quelle nouvelle fonction "
        "n'exerce-t-il pas ? Signalez sa ligne `def`, ou le fichier de tests."
    ),
}


def test_au_moins_trois_defauts_sont_trouves(
        commentaires: list[Commentaire], zones: dict[str, list[Zone]]) -> None:
    trouves = [c for c in CATEGORIES if _trouve(commentaires, zones[c])]
    manques = [CONSEILS[c] for c in sorted(CATEGORIES) if c not in trouves]
    assert len(trouves) >= DEFAUTS_A_TROUVER, (
        f"{len(trouves)} défaut(s) sur 4 désignés par un commentaire (bon fichier, bonne "
        f"catégorie, ligne lue APRÈS application du diff, à deux lignes près) : il en "
        f"faut {DEFAUTS_A_TROUVER}. Pistes :\n  - " + "\n  - ".join(manques)
    )


def test_chaque_commentaire_propose_une_correction(
        commentaires: list[Commentaire], zones: dict[str, list[Zone]]) -> None:
    assert commentaires, "`commentaires` est vide : une revue sans commentaire n'aide pas l'auteur."
    inconnues = sorted({c.categorie for c in commentaires} - CATEGORIES)
    assert not inconnues, (
        f"Catégorie(s) hors de la liste : {inconnues}. Reprenez exactement une valeur "
        "de la liste écrite dans revue.yaml."
    )
    vagues = [f"{c.fichier}:{c.ligne}" for c in commentaires
              if len(c.commentaire) < LONGUEUR_MINIMALE or len(c.proposition) < LONGUEUR_MINIMALE]
    assert not vagues, (
        f"Commentaire(s) trop vague(s) : {vagues}. Chacun porte un `commentaire` (le "
        "problème, et quand il se produit) et une `proposition` (la correction "
        f"demandée), d'au moins {LONGUEUR_MINIMALE} caractères chacun. « À revoir » ne "
        "dit pas à l'auteur quoi faire."
    )
    toutes = [z for liste in zones.values() for z in liste]
    hors_sujet = [f"{c.fichier}:{c.ligne} ({c.categorie})" for c in commentaires
                  if not any(z.categorie == c.categorie and z.contient(c.fichier, c.ligne) for z in toutes)]
    assert len(hors_sujet) <= FAUX_POSITIFS_TOLERES, (
        f"{len(hors_sujet)} commentaire(s) ne désignent aucun défaut du diff : {hors_sujet}. "
        "Vérifiez le chemin du fichier (src/certcheck/...) et le numéro de ligne, lu "
        "dans le fichier APRÈS `git apply`, pas dans le diff."
    )


def test_le_verdict_demande_des_changements(revue: dict) -> None:
    verdict = str(revue.get("verdict") or "").strip().lower()
    assert verdict in VERDICTS, f"`verdict` vaut {verdict!r} : choisissez parmi {sorted(VERDICTS)}."
    assert verdict == "demander-des-changements", (
        "`verdict` : approuver une PR qui affiche un jeton et peut supprimer "
        "récursivement depuis la racine, c'est en devenir co-auteur. Des tests verts "
        "ne suffisent pas : demandez des changements."
    )


def _config_ruff() -> tuple[str, dict]:
    """(fichier, configuration) : ruff.toml, .ruff.toml, ou [tool.ruff] de pyproject.toml."""
    for nom in ("ruff.toml", ".ruff.toml"):
        chemin = WORKDIR / nom
        if chemin.is_file():
            try:
                return nom, tomllib.loads(chemin.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError as exc:
                pytest.fail(f"{nom} n'est pas un TOML valide : {exc}", pytrace=False)
    try:
        projet = tomllib.loads((WORKDIR / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        pytest.fail(f"pyproject.toml est illisible : {exc}", pytrace=False)
    outil = projet.get("tool") or {}
    if "ruff" in outil:
        return "pyproject.toml", outil["ruff"]
    return "", {}


def test_une_configuration_ruff_est_versionnee() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    fichier, _ = _config_ruff()
    assert fichier, (
        "Aucune configuration ruff dans le projet : ni section `[tool.ruff]` dans "
        "pyproject.toml, ni fichier ruff.toml. La configuration du linter se versionne "
        "avec le code : chacun, et la CI, lance alors exactement les mêmes règles. "
        "Une section suffit pour commencer, par exemple `[tool.ruff]` puis "
        "`line-length = 100`."
    )


def test_ruff_check_passe_sur_le_code_de_base() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    uv = exiger_outil("uv")
    fichier, _ = _config_ruff()
    assert fichier, "Écrivez d'abord la configuration ruff (tâche précédente)."
    with copie_temporaire(WORKDIR) as copie:
        res = executer([uv, "run", "--quiet", "--directory", str(copie), "ruff", "check", "."], timeout=300)
        import_inutile = executer([uv, "run", "--quiet", "--directory", str(copie), "ruff", "check",
                                   "--isolated", "--select", "F401", "src"], timeout=300)
    assert res.returncode == 0, (
        "`uv run ruff check .` signale encore des défauts dans le code de base. Lisez "
        "chaque ligne : le code de la règle, le fichier, la ligne. `ruff check --fix` "
        "corrige ceux marqués [*].\n" + (res.stdout + res.stderr).strip()[-1500:]
    )
    assert import_inutile.returncode == 0, (
        "Un import inutilisé (F401) reste dans src/ : la configuration ne doit pas "
        "faire taire une règle pour faire passer ruff, le défaut se corrige dans le "
        "code.\n" + (import_inutile.stdout + import_inutile.stderr).strip()[-800:]
    )
