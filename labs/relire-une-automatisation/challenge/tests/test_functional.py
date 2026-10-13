"""Relire une automatisation : cinq contrôles, vingt points chacun.

## Ce qui est noté

La revue de `revue.yaml`, confrontée au diff réel de la pull request n°42.
Les lignes attendues ne sont pas écrites en dur : le contrôle applique
`pr/0042.diff` (`git apply`) sur une copie du point de départ intact, puis
cherche dans les fichiers obtenus les marqueurs textuels de chaque défaut.
Un commentaire trouve un défaut s'il désigne le bon fichier, la bonne
catégorie, et une ligne située à deux lignes au plus de la zone fautive (trois
pour un test absent, qui se signale sur la déclaration de la fonction).

Le dernier contrôle lit `.pre-commit-config.yaml` sans lancer pre-commit :
il vérifie la forme (hooks attendus, dépôts officiels, révisions figées sur
une empreinte de commit), pas le téléchargement des hooks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from conftest import copie_temporaire, exiger_workdir, git, lire_yaml, workdir_lab

WORKDIR = workdir_lab(__file__)
LAB_ID = "relire-une-automatisation"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

CATEGORIES = {
    "erreur-avalee", "secret-expose", "tls-desactive", "effet-de-bord-non-borne",
    "dependance-non-epinglee", "test-absent", "non-idempotent", "injection-de-commande",
}
VERDICTS = {"approuver", "demander-des-changements"}
LONGUEUR_MINIMALE = 25
FAUX_POSITIFS_TOLERES = 2
EMPREINTE = re.compile(r"^[0-9a-f]{40}$")

# Hooks admis pour chaque rôle, et le dépôt officiel qui les publie.
DETECTEURS_DE_SECRETS = {
    "gitleaks": "github.com/gitleaks/gitleaks",
    "detect-secrets": "github.com/yelp/detect-secrets",
    "detect-private-key": "github.com/pre-commit/pre-commit-hooks",
}
LINTERS = {
    "ruff": "github.com/astral-sh/ruff-pre-commit",
    "ruff-check": "github.com/astral-sh/ruff-pre-commit",
}


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
            for nom in ("certcheck.py", "maintenance.py", "pyproject.toml", "tests/test_maintenance.py")
        }
    test_ajoute = len(fichiers["tests/test_maintenance.py"].splitlines())
    return {
        "secret-expose": [_zone("secret-expose", "certcheck.py", fichiers, "notification envoyée à {webhook}")],
        "tls-desactive": [_zone("tls-desactive", "maintenance.py", fichiers,
                                "urllib3.disable_warnings()", "verify=False")],
        "erreur-avalee": [_zone("erreur-avalee", "maintenance.py", fichiers, "except Exception:")],
        "effet-de-bord-non-borne": [_zone("effet-de-bord-non-borne", "maintenance.py", fichiers,
                                          'os.environ.get("CERTCHECK_REPORT_DIR"', "shutil.rmtree(")],
        "dependance-non-epinglee": [_zone("dependance-non-epinglee", "pyproject.toml", fichiers, '"requests>=')],
        "test-absent": [
            _zone("test-absent", "maintenance.py", fichiers, "def notifier(", marge=3),
            _zone("test-absent", "certcheck.py", fichiers, "if args.notify:", marge=3),
            Zone("test-absent", "tests/test_maintenance.py", 1, test_ajoute),
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


def _verifier_trouves(commentaires: list[Commentaire], zones: dict[str, list[Zone]],
                      attendus: dict[str, str]) -> None:
    manques = [conseil for categorie, conseil in attendus.items()
               if not _trouve(commentaires, zones[categorie])]
    assert not manques, (
        f"{len(manques)} défaut(s) de cette tâche ne sont désignés par aucun commentaire "
        "(bon fichier, bonne catégorie, ligne lue APRÈS application du diff) :\n  - "
        + "\n  - ".join(manques)
    )


def test_le_secret_expose_et_le_tls_desactive_sont_signales(
        commentaires: list[Commentaire], zones: dict[str, list[Zone]]) -> None:
    _verifier_trouves(commentaires, zones, {
        "secret-expose": (
            "secret-expose : la description dit que l'URL du webhook CONTIENT le "
            "jeton. Cherchez dans certcheck.py où cette URL est écrite sur une sortie : "
            "la sortie d'erreur d'un cron finit dans un courriel ou un journal."
        ),
        "tls-desactive": (
            "tls-desactive : « c'est contourné », dit la description à propos d'une "
            "erreur de certificat. Cherchez dans maintenance.py comment : un "
            "contournement de ce genre fait accepter n'importe quel serveur."
        ),
    })


def test_l_erreur_avalee_et_l_effet_de_bord_non_borne_sont_signales(
        commentaires: list[Commentaire], zones: dict[str, list[Zone]]) -> None:
    _verifier_trouves(commentaires, zones, {
        "erreur-avalee": (
            "erreur-avalee : « c'est géré », dit la description si le chat est "
            "indisponible. Regardez comment : que devient un 401, un 404 ou une "
            "faute de frappe dans le code de notifier ?"
        ),
        "effet-de-bord-non-borne": (
            "effet-de-bord-non-borne : que vaut le dossier purgé si "
            "CERTCHECK_REPORT_DIR n'est pas défini dans l'environnement du cron ? "
            "Suivez la valeur jusqu'à la suppression récursive."
        ),
    })


def test_la_dependance_non_epinglee_et_le_test_absent_sont_signales(
        commentaires: list[Commentaire], zones: dict[str, list[Zone]]) -> None:
    _verifier_trouves(commentaires, zones, {
        "dependance-non-epinglee": (
            "dependance-non-epinglee : relisez la règle écrite en commentaire dans "
            "pyproject.toml, puis la ligne que le diff y ajoute."
        ),
        "test-absent": (
            "test-absent : la PR ajoute des tests, et ils passent. Lesquelles des "
            "nouvelles fonctions exercent-ils ? Signalez la fonction qu'aucun test "
            "n'appelle (sa ligne `def`), ou le fichier de tests qui l'oublie."
        ),
    })


def test_les_commentaires_sont_actionnables(
        revue: dict, commentaires: list[Commentaire], zones: dict[str, list[Zone]]) -> None:
    assert commentaires, "`commentaires` est vide : une revue sans commentaire n'aide pas l'auteur."
    inconnues = sorted({c.categorie for c in commentaires} - CATEGORIES)
    assert not inconnues, (
        f"Catégorie(s) hors de la liste fermée : {inconnues}. Une catégorie commune "
        "permet de compter les défauts d'une équipe d'une revue à l'autre ; reprenez "
        "exactement une valeur de la liste de revue.yaml."
    )
    vagues = [f"{c.fichier}:{c.ligne}" for c in commentaires
              if len(c.commentaire) < LONGUEUR_MINIMALE or len(c.proposition) < LONGUEUR_MINIMALE]
    assert not vagues, (
        f"Commentaire(s) trop vague(s) : {vagues}. Chacun porte un `commentaire` "
        f"(le problème, et quand il se produit) et une `proposition` (la correction "
        f"demandée), d'au moins {LONGUEUR_MINIMALE} caractères chacun. « À revoir » "
        "ne dit pas à l'auteur quoi faire."
    )
    toutes = [z for liste in zones.values() for z in liste]
    hors_sujet = [f"{c.fichier}:{c.ligne} ({c.categorie})" for c in commentaires
                  if not any(z.categorie == c.categorie and z.contient(c.fichier, c.ligne) for z in toutes)]
    assert len(hors_sujet) <= FAUX_POSITIFS_TOLERES, (
        f"{len(hors_sujet)} commentaire(s) ne désignent aucun défaut réel du diff : "
        f"{hors_sujet}. Au-delà de {FAUX_POSITIFS_TOLERES}, la revue noie l'essentiel. "
        "Vérifiez le numéro de ligne (dans le fichier APRÈS `git apply`, pas dans le "
        "diff), et qu'une catégorie comme non-idempotent ou injection-de-commande se "
        "prouve vraiment par une ligne du diff."
    )
    verdict = str(revue.get("verdict") or "").strip().lower()
    assert verdict in VERDICTS, f"`verdict` vaut {verdict!r} : choisissez parmi {sorted(VERDICTS)}."
    assert verdict == "demander-des-changements", (
        "`verdict` : approuver une PR qui journalise un jeton, coupe TLS et peut "
        "supprimer récursivement depuis la racine, c'est en devenir co-auteur. "
        "Des tests verts ne suffisent pas : demandez des changements."
    )


def _depot_officiel(repo: str) -> str:
    return repo.lower().removeprefix("https://").removeprefix("http://").removesuffix(".git").rstrip("/")


def test_le_pre_commit_detecte_secrets_et_defauts_avant_la_revue() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    chemin = WORKDIR / ".pre-commit-config.yaml"
    assert chemin.is_file(), (
        ".pre-commit-config.yaml est absent de la racine du projet. Les défauts "
        "mécaniques (un jeton commité, un `except Exception: pass`) se refusent "
        "au commit, avant même la revue : c'est le rôle de pre-commit."
    )
    try:
        config = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        pytest.fail(f".pre-commit-config.yaml n'est pas un YAML valide : {exc}", pytrace=False)
    depots = config.get("repos") if isinstance(config, dict) else None
    assert isinstance(depots, list) and depots, ".pre-commit-config.yaml doit porter une liste `repos`."

    secrets, linter, mobiles = [], [], []
    for depot in depots:
        if not isinstance(depot, dict):
            continue
        url = str(depot.get("repo") or "")
        if url in ("local", "meta"):
            continue
        rev = str(depot.get("rev") or "")
        if not EMPREINTE.match(rev):
            mobiles.append(f"{url} (rev: {rev or 'absent'})")
        ids = {str(h.get("id")) for h in depot.get("hooks") or [] if isinstance(h, dict)}
        officiel = _depot_officiel(url)
        secrets += [i for i in ids if DETECTEURS_DE_SECRETS.get(i) == officiel]
        linter += [i for i in ids if LINTERS.get(i) == officiel]

    assert secrets, (
        "Aucun détecteur de secrets : ajoutez le hook gitleaks (dépôt "
        "https://github.com/gitleaks/gitleaks), detect-secrets "
        "(https://github.com/Yelp/detect-secrets) ou detect-private-key "
        "(https://github.com/pre-commit/pre-commit-hooks), depuis son dépôt officiel."
    )
    assert linter, (
        "Aucun linter Python : ajoutez le hook ruff-check du dépôt "
        "https://github.com/astral-sh/ruff-pre-commit. Avec ses règles par "
        "défaut (ruff 0.17.0), il refuse déjà le `except Exception: pass` de la "
        "PR (BLE001, S110) ; la règle S501, à ajouter, refuse `verify=False`."
    )
    assert not mobiles, (
        f"Révision(s) non figée(s) : {mobiles}. Un tag se déplace, une empreinte de "
        "commit de 40 caractères non. `pre-commit autoupdate --freeze` écrit "
        "l'empreinte et garde le tag en commentaire."
    )
