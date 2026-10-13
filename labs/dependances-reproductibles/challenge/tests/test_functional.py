"""Dépendances reproductibles : cinq contrôles, vingt points chacun.

## Ce qui est noté

Ce qu'un collègue obtient en récupérant le projet, pas ce que l'apprenant a
tapé. Les fichiers du projet (`pyproject.toml`, `requirements.txt`,
`uv.lock`, `.python-version`) sont lus, puis le projet est COPIÉ sans son
`.venv` et installé dans un environnement neuf, uniquement depuis ces
fichiers :

- s'il y a un `uv.lock` : `uv sync --frozen`, comme un collègue qui utilise
  uv ;
- sinon : un environnement virtuel neuf, `pip install -r requirements.txt`
  s'il existe, puis `pip install .` (joué par `uv pip`, plus rapide, même
  résultat).

Une bibliothèque installée « à la main » sur le poste de l'apprenant
n'existe pas dans cet environnement : si l'outil y fonctionne, c'est que
tout ce qu'il importe est déclaré.

## Pourquoi `requests` ne s'importe qu'à la publication

`cryptography` est importée au démarrage : sans elle, même `--version`
échoue. `requests` ne l'est que par `--publish` : le dernier contrôle publie
donc vraiment un ticket, sur une forge factice, pour prouver qu'elle aussi
est déclarée.

## Réseau

L'installation télécharge les paquets depuis PyPI (et, au besoin,
l'interpréteur fixé) ; uv garde ensuite tout en cache.
"""

from __future__ import annotations

import re
import shutil
import tomllib
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    TITRE_TICKET,
    Execution,
    Forge,
    attendus,
    code_attendu,
    copie_temporaire,
    ecrire_inventaire,
    executer,
    exiger_outil,
    exiger_workdir,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "dependances-reproductibles"
DEPENDANCES = ("requests", "cryptography")
VERSION = "0.5.0"


def _nom(nom: str) -> str:
    """`Cryptography`, `cryptography` et `crypto_graphy` désignent le même paquet."""
    return re.sub(r"[-_.]+", "-", nom).lower()


def _exigence(ligne: str) -> tuple[str, str]:
    """`requests==2.34.2 ; python_version >= '3.12'` -> ("requests", "==2.34.2")."""
    sans_marqueur = ligne.split(";", 1)[0].split("--hash", 1)[0].strip()
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(\[[^\]]*\])?\s*(.*)$", sans_marqueur)
    if not m:
        return "", ""
    return _nom(m.group(1)), m.group(3).replace(" ", "").replace("\\", "")


def _pyproject() -> dict:
    exiger_workdir(WORKDIR, LAB_ID)
    try:
        return tomllib.loads((WORKDIR / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        pytest.fail(f"pyproject.toml est illisible : {exc}", pytrace=False)


def _requirements() -> dict[str, str]:
    chemin = WORKDIR / "requirements.txt"
    if not chemin.is_file():
        return {}
    texte = re.sub(r"\\\s*\n", " ", chemin.read_text(encoding="utf-8"))
    sortie = {}
    for brute in texte.splitlines():
        ligne = brute.split(" #", 1)[0].strip()
        if ligne and not ligne.startswith(("#", "-")):
            nom, spec = _exigence(ligne)
            sortie[nom] = spec
    return sortie


def _declarees() -> dict[str, list[str]]:
    """Paquet -> spécifications trouvées (pyproject.toml et requirements.txt)."""
    sortie: dict[str, list[str]] = {}
    for ligne in (_pyproject().get("project") or {}).get("dependencies") or []:
        nom, spec = _exigence(str(ligne))
        sortie.setdefault(nom, []).append(spec)
    for nom, spec in _requirements().items():
        sortie.setdefault(nom, []).append(spec)
    return sortie


def _verrou() -> dict[str, str]:
    chemin = WORKDIR / "uv.lock"
    if not chemin.is_file():
        return {}
    try:
        donnees = tomllib.loads(chemin.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return {}
    return {_nom(p.get("name", "")): str(p.get("version", "")) for p in donnees.get("package") or []}


# --- L'installation neuve, partagée par les deux derniers contrôles -----------------


@pytest.fixture(scope="module")
def installation(tmp_path_factory: pytest.TempPathFactory) -> Callable[..., Execution]:
    """Installe une copie du projet dans un environnement neuf ; rend un lanceur de certcheck."""
    exiger_workdir(WORKDIR, LAB_ID)
    uv = exiger_outil("uv")
    base = tmp_path_factory.mktemp("installation")
    copie = base / "projet"
    with copie_temporaire(WORKDIR) as source:
        shutil.copytree(source, copie)
    etapes: list[str] = []

    def etape(*args: str, cwd: Path) -> None:
        res = executer([uv, *args], cwd=cwd)
        etapes.append(f"$ uv {' '.join(args)}  (code {res.returncode})\n{(res.stdout + res.stderr).strip()[-800:]}")
        if res.returncode != 0:
            pytest.fail(
                "L'installation dans un environnement neuf échoue, à partir des seuls "
                "fichiers du projet :\n" + "\n".join(etapes),
                pytrace=False,
            )

    if (copie / "uv.lock").is_file():
        etape("sync", "--frozen", "--quiet", cwd=copie)
        commande = [uv, "run", "--frozen", "--quiet", "--project", str(copie), "certcheck"]
    else:
        env = base / "env"
        etape("venv", "--quiet", str(env), cwd=base)
        python = str(env / "bin" / "python")
        if (copie / "requirements.txt").is_file():
            etape("pip", "install", "--quiet", "--python", python, "-r", str(copie / "requirements.txt"), cwd=base)
        etape("pip", "install", "--quiet", "--python", python, str(copie), cwd=base)
        commande = [str(env / "bin" / "certcheck")]

    def certcheck(*args: str, cwd: Path, env: dict[str, str] | None = None) -> Execution:
        res = executer([*commande, *args], cwd=cwd, env=env, timeout=120)
        return Execution(res.returncode, res.stdout, res.stderr, [*commande, *args])

    return certcheck


# --- Les contrôles ----------------------------------------------------------------


def test_les_dependances_sont_declarees() -> None:
    declarees = _declarees()
    manquantes = [d for d in DEPENDANCES if d not in declarees]
    assert not manquantes, (
        f"{manquantes} ne sont déclarées ni dans pyproject.toml ([project] dependencies), "
        "ni dans requirements.txt. Le code les importe : installées « à la main » chez "
        "vous, elles n'existent pas chez un collègue. `uv add requests cryptography` "
        "les écrit dans pyproject.toml."
    )


def test_les_versions_sont_epinglees() -> None:
    declarees = _declarees()
    verrou = _verrou()
    if all(d in verrou for d in DEPENDANCES):
        return  # uv.lock fige la version exacte de chaque paquet, transitifs compris
    non_epinglees = [d for d in DEPENDANCES
                     if not any(re.fullmatch(r"==[0-9][^,]*", s) for s in declarees.get(d, []))]
    assert not non_epinglees, (
        f"{non_epinglees} n'ont pas de version exacte : "
        f"{ {d: declarees.get(d) or '(non déclarée)' for d in non_epinglees} }. Sans "
        "version, chaque installation prend la dernière parue, et deux postes divergent. "
        "Épinglez-les (`requests==2.34.2`), ou laissez uv écrire un verrou : `uv lock` "
        "produit uv.lock, qui fige chaque version."
    )


def test_la_version_de_python_est_notee() -> None:
    requires = str((_pyproject().get("project") or {}).get("requires-python") or "")
    fichier = WORKDIR / ".python-version"
    fixee = fichier.read_text(encoding="utf-8").strip() if fichier.is_file() else ""
    assert requires or re.match(r"^\d+\.\d+", fixee), (
        "Rien ne dit avec quelle version de Python le projet tourne : ni "
        "`requires-python` dans pyproject.toml (par exemple \">=3.12\"), ni fichier "
        ".python-version (`uv python pin 3.14`). Un collègue sous Python 3.9 "
        "découvrirait l'incompatibilité au premier lancement."
    )


def test_le_projet_s_installe_dans_un_environnement_neuf(installation: Callable[..., Execution],
                                                          tmp_path: Path) -> None:
    res = installation("--version", cwd=tmp_path)
    assert res.code == 0 and res.sortie.strip() == f"certcheck {VERSION}", (
        "Installé dans un environnement neuf depuis les seuls fichiers du projet, "
        "`certcheck --version` échoue. Une ModuleNotFoundError nomme la bibliothèque "
        "importée par le code mais déclarée nulle part.\n  " + res.resume()
    )


def test_rien_n_est_installe_a_la_main(installation: Callable[..., Execution], tmp_path: Path,
                                       forge: Forge) -> None:
    graine = tirage().randrange(10**6)
    rnd = tirage(graine)
    while True:
        hotes = rnd.sample(sorted(EXPIRATIONS), rnd.randint(3, 5))
        jour = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900))
        seuil = rnd.choice([15, 30, 45, 90])
        calcul = attendus(hotes, jour, seuil)
        if any(s in ("warning", "expired") for _, s in calcul.values()):
            break
    inventaire = ecrire_inventaire(tmp_path / "parc", hotes)
    res = installation("--inventory", str(inventaire), "--days", str(seuil), "--publish",
                       cwd=tmp_path / "parc", env={"CERTCHECK_NOW": jour.isoformat(), **forge.env()})
    attendu = code_attendu([s for _, s in calcul.values()])
    tickets = [t for t in forge.tickets if t.get("title") == TITRE_TICKET]
    assert res.code == attendu and len(tickets) == 1, (
        "Dans l'environnement neuf, certcheck n'a pas analysé le parc puis publié son "
        f"ticket (code {res.code}, attendu {attendu} ; {len(tickets)} ticket(s), graine "
        f"{graine}). La publication importe requests : si elle manque, c'est qu'elle "
        "n'était installée qu'à la main sur votre poste.\n  " + res.resume()
    )
