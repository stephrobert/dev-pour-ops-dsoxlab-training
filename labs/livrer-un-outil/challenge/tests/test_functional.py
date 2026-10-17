"""Livrer un outil interne : cinq contrôles, vingt points chacun.

## Ce qui est noté

Ce qu'un utilisateur de l'outil obtient, pas les commandes tapées : la
version affichée, le journal des changements, l'étiquette Git, et surtout
une installation dans un environnement NEUF, d'abord depuis le répertoire de
travail, puis depuis un clone de l'étiquette `v1.0.0`. C'est exactement ce
que fait celui qui installe la 1.0.0 sans avoir vu votre poste. Le lab est
une initiation : rien n'est publié, aucune roue n'est exigée dans `dist/`.

## Pourquoi vérifier que le dépôt est bien celui du lab

Le répertoire de travail vit À L'INTÉRIEUR du dépôt du catalogue. Sans
`git init` dans ce répertoire, toute commande Git y remonterait au dépôt du
catalogue, et lirait ses étiquettes au lieu des vôtres. Chaque contrôle Git
exige donc que la racine du dépôt soit le répertoire de travail lui-même.

## Réseau

L'installation neuve télécharge les dépendances depuis PyPI (uv les garde
ensuite en cache).
"""

from __future__ import annotations

import re
import tomllib
from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    Execution,
    attendus,
    code_attendu,
    copie_temporaire,
    ecrire_inventaire,
    executer,
    exiger_executable,
    exiger_outil,
    exiger_workdir,
    git,
    lancer,
    lire_json_sortie,
    message,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "livrer-un-outil"
VERSION = "1.0.0"
ETIQUETTE = f"v{VERSION}"


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


@pytest.fixture(scope="module")
def uv() -> str:
    return exiger_outil("uv")


def _uv(uv: str, *args: str, cwd: Path, env: dict[str, str] | None = None) -> Execution:
    res = executer([uv, *args], cwd=cwd, env=env)
    return Execution(res.returncode, res.stdout, res.stderr, [uv, *args])


def _version_pyproject(texte: str, ou: str) -> str:
    try:
        return str((tomllib.loads(texte).get("project") or {}).get("version") or "")
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(message(
            en=f"pyproject.toml ({ou}) is not valid TOML: {exc}",
            fr=f"pyproject.toml ({ou}) n'est pas un TOML valide : {exc}",
        ), pytrace=False)


def _exiger_depot(projet: Path) -> None:
    """Le répertoire de travail est la racine de SON dépôt, pas un dossier du catalogue."""
    racine = git("rev-parse", "--show-toplevel", cwd=projet)
    if not (projet / ".git").exists() or Path(racine.stdout.strip()).resolve() != projet.resolve():
        pytest.fail(
            message(
            en="The working directory is not a Git repository: run `git init` "
            "INSIDE this directory, then commit the project. Without it, Git goes up to "
            "the catalogue's repository that contains it, and your commits and tags "
            "would not exist where they are looked for.",
            fr="Le répertoire de travail n'est pas un dépôt Git : lancez `git init` "
            "DANS ce répertoire, puis committez le projet. Sans lui, Git remonte au "
            "dépôt du catalogue qui le contient, et vos commits et étiquettes "
            "n'existeraient pas là où on les cherche.",
        ),
            pytrace=False,
        )


def _exiger_etiquette(projet: Path) -> None:
    _exiger_depot(projet)
    nature = git("cat-file", "-t", ETIQUETTE, cwd=projet)
    if nature.returncode != 0:
        etiquettes = git("tag", "--list", cwd=projet).stdout.split()
        pytest.fail(
            message(
            en=f"The tag {ETIQUETTE} does not exist (tags present: "
            f"{etiquettes or 'none'}). A shipped version is identified by a "
            f"tag: `git tag -a {ETIQUETTE} -m \"certcheck {VERSION}\"`.",
            fr=f"L'étiquette {ETIQUETTE} n'existe pas (étiquettes présentes : "
            f"{etiquettes or 'aucune'}). Une version livrée se repère par une "
            f"étiquette : `git tag -a {ETIQUETTE} -m \"certcheck {VERSION}\"`.",
        ),
            pytrace=False,
        )


def _scenario() -> tuple[list[str], date, int, int]:
    rnd = tirage()
    graine = rnd.randrange(10**6)
    rnd = tirage(graine)
    hotes = rnd.sample(sorted(EXPIRATIONS), rnd.randint(3, 6))
    jour = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900))
    return hotes, jour, rnd.choice([7, 15, 30, 45, 90]), graine


# --- Les contrôles ----------------------------------------------------------------


def test_la_version_a_une_seule_source(projet: Path, uv: str) -> None:
    version = _version_pyproject((projet / "pyproject.toml").read_text(encoding="utf-8"), "répertoire de travail")
    assert version == VERSION, message(
        en=f"pyproject.toml carries version {version!r}, expected {VERSION!r}. It is the "
        "ONLY place where the version is written: the wheel, the sdist and `certcheck "
        "--version` take it from there.",
        fr=f"pyproject.toml porte la version {version!r}, attendu {VERSION!r}. C'est la "
        "SEULE place où la version s'écrit : la roue, le sdist et `certcheck "
        "--version` la tirent de là.",
    )
    en_dur = sorted(
        str(f.relative_to(projet)) for f in (projet / "src").rglob("*")
        if f.is_file() and f.suffix in (".py", ".txt", ".toml", ".cfg", ".json")
        and VERSION in f.read_text(encoding="utf-8", errors="ignore")
    )
    assert not en_dur, message(
        en=f"{en_dur} write \"{VERSION}\" by hand. Two places for one version "
        "means two versions the day one of them is forgotten (0.5.0 is an "
        "example). The code reads the version from the installed package's metadata: "
        "`importlib.metadata.version(\"certcheck\")`.",
        fr=f"{en_dur} écrivent « {VERSION} » en dur. Deux endroits pour une version, "
        "c'est deux versions le jour où l'un est oublié (la 0.5.0 en est un "
        "exemple). Le code lit la version dans les métadonnées du paquet installé : "
        "`importlib.metadata.version(\"certcheck\")`.",
    )
    affichee = lancer(exiger_executable(projet), "--version", cwd=projet)
    assert affichee.code == 0 and affichee.sortie.strip() == f"certcheck {VERSION}", message(
        en=f"`bin/certcheck --version` must print exactly \"certcheck {VERSION}\".\n"
        f"  {affichee.resume()}",
        fr=f"`bin/certcheck --version` doit afficher exactement « certcheck {VERSION} ».\n"
        f"  {affichee.resume()}",
    )
    # La preuve par le comportement : changez la version de pyproject.toml dans
    # une copie, et l'outil doit suivre sans qu'on touche au code.
    essai = f"9.{tirage().randint(1, 98)}.{tirage().randint(1, 98)}"
    with copie_temporaire(projet) as copie:
        pyproject = copie / "pyproject.toml"
        pyproject.write_text(re.sub(r'(?m)^version\s*=\s*"[^"]*"', f'version = "{essai}"',
                                    pyproject.read_text(encoding="utf-8"), count=1), encoding="utf-8")
        suivie = _uv(uv, "run", "--quiet", "certcheck", "--version", cwd=copie)
    assert suivie.code == 0 and suivie.sortie.strip() == f"certcheck {essai}", message(
        en=f"In a copy where pyproject.toml moves to {essai}, certcheck --version "
        f"prints {suivie.sortie.strip() or '(nothing)'!r}: the version is not read "
        "from the package's metadata, it comes from somewhere else.\n  "
        f"{suivie.resume()}",
        fr=f"Dans une copie où pyproject.toml passe à {essai}, certcheck --version "
        f"affiche {suivie.sortie.strip() or '(rien)'!r} : la version n'est pas lue "
        "dans les métadonnées du paquet, elle vient d'ailleurs.\n  "
        f"{suivie.resume()}",
    )


def test_le_changelog_porte_la_version(projet: Path) -> None:
    chemin = projet / "CHANGELOG.md"
    assert chemin.is_file(), message(
        en="CHANGELOG.md has disappeared: it is what tells users what changes.",
        fr="CHANGELOG.md a disparu : c'est lui qui dit aux utilisateurs ce qui change.",
    )
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    titres = [i for i, ligne in enumerate(lignes) if re.match(r"^##\s", ligne)]
    section = [i for i in titres if re.match(rf"^##\s+\[?{re.escape(VERSION)}\]?(\s|$)", lignes[i])]
    assert section, message(
        en=f"CHANGELOG.md has no `## [{VERSION}]` section. Shipping means saying what "
        f"changes: move the content of [Unreleased] under a heading `## [{VERSION}] - "
        "YYYY-MM-DD`.",
        fr=f"CHANGELOG.md n'a pas de section `## [{VERSION}]`. Livrer, c'est dire ce qui "
        f"change : déplacez le contenu de [Unreleased] sous un titre `## [{VERSION}] - "
        "AAAA-MM-JJ`.",
    )
    debut = section[0]
    suivants = [i for i in titres if i > debut]
    corps = lignes[debut + 1:suivants[0] if suivants else len(lignes)]
    assert any(re.match(r"^\s*[-*]\s+\S", ligne) for ligne in corps), message(
        en=f"The [{VERSION}] section contains no `- …` entry: a user reads it "
        "to decide whether to upgrade.",
        fr=f"La section [{VERSION}] ne contient aucune entrée `- ...` : un utilisateur la "
        "lit pour décider s'il met à jour.",
    )


def test_l_etiquette_designe_la_livraison(projet: Path) -> None:
    _exiger_etiquette(projet)
    pyproject = git("show", f"{ETIQUETTE}:pyproject.toml", cwd=projet)
    version = _version_pyproject(pyproject.stdout, f"à l'étiquette {ETIQUETTE}") if pyproject.returncode == 0 else ""
    assert version == VERSION, message(
        en=f"At the commit tagged {ETIQUETTE}, pyproject.toml carries version {version!r}. "
        "The tag was placed before the commit moving to 1.0.0: it must "
        "name the commit that CONTAINS the shipped version. `git tag -d v1.0.0`, "
        "commit, then place the tag again.",
        fr=f"Au commit étiqueté {ETIQUETTE}, pyproject.toml porte la version {version!r}. "
        "L'étiquette a été posée avant le commit du passage en 1.0.0 : elle doit "
        "désigner le commit qui CONTIENT la version livrée. `git tag -d v1.0.0`, "
        "committez, puis reposez l'étiquette.",
    )


def _installer(uv: str, source: Path, env: Path) -> Path:
    """`pip install <source>` dans un environnement neuf ; rend le chemin de la commande certcheck."""
    creation = _uv(uv, "venv", "--quiet", str(env), cwd=env.parent)
    assert creation.code == 0, message(
        en=f"`uv venv` fails.\n  {creation.resume()}",
        fr=f"`uv venv` échoue.\n  {creation.resume()}",
    )
    installation = _uv(uv, "pip", "install", "--quiet", "--python", str(env / "bin" / "python"),
                       str(source), cwd=env.parent)
    assert installation.code == 0, message(
        en=f"`pip install {source.name}` fails in a fresh environment: the project does not "
        f"build, or its dependencies do not resolve.\n  {installation.resume()}",
        fr=f"`pip install {source.name}` échoue dans un environnement neuf : le projet ne se "
        f"construit pas, ou ses dépendances ne se résolvent pas.\n  {installation.resume()}",
    )
    return env / "bin" / "certcheck"


def test_l_outil_s_installe_dans_un_environnement_neuf(projet: Path, uv: str, tmp_path: Path) -> None:
    with copie_temporaire(projet) as copie:
        certcheck = _installer(uv, copie, tmp_path / "env")
        version = lancer(certcheck, "--version", cwd=tmp_path)
    assert version.code == 0 and version.sortie.strip() == f"certcheck {VERSION}", message(
        en=f"Installed by `pip install .` in a fresh environment, `certcheck --version` "
        f"must print \"certcheck {VERSION}\". A version hard-coded in the code, "
        "or read from pyproject.toml through a file path, breaks here: an installed "
        f"package carries only its metadata.\n  {version.resume()}",
        fr=f"Installé par `pip install .` dans un environnement neuf, `certcheck --version` "
        f"doit afficher « certcheck {VERSION} ». Une version écrite en dur dans le code, "
        "ou lue dans pyproject.toml par un chemin de fichier, casse ici : un paquet "
        f"installé n'emporte que ses métadonnées.\n  {version.resume()}",
    )


def test_l_etiquette_s_installe_dans_un_environnement_neuf(projet: Path, uv: str, tmp_path: Path) -> None:
    _exiger_etiquette(projet)
    clone = tmp_path / "clone"
    res = git("clone", "-q", "--branch", ETIQUETTE, str(projet), str(clone), cwd=tmp_path)
    assert res.returncode == 0, message(
        en=f"`git clone --branch {ETIQUETTE}` fails:\n{res.stderr.strip()}",
        fr=f"`git clone --branch {ETIQUETTE}` échoue :\n{res.stderr.strip()}",
    )
    certcheck = _installer(uv, clone, tmp_path / "env")
    version = lancer(certcheck, "--version", cwd=tmp_path)
    assert version.code == 0 and version.sortie.strip() == f"certcheck {VERSION}", message(
        en=f"Installed from a clone of the tag {ETIQUETTE}, `certcheck --version` must "
        f"print \"certcheck {VERSION}\". If the tagged commit lacks a file that "
        "your machine has (README.md named by pyproject.toml, an uncommitted "
        f"module), the installation breaks here.\n  {version.resume()}",
        fr=f"Installé depuis un clone de l'étiquette {ETIQUETTE}, `certcheck --version` doit "
        f"afficher « certcheck {VERSION} ». S'il manque au commit étiqueté un fichier que "
        "votre poste possède (README.md cité par pyproject.toml, un module non "
        f"commité), l'installation casse ici.\n  {version.resume()}",
    )
    hotes, jour, seuil, graine = _scenario()
    inventaire = ecrire_inventaire(tmp_path / "parc", hotes)
    execution = lancer(certcheck, "--inventory", str(inventaire), "--days", str(seuil), "--format", "json",
                       cwd=tmp_path / "parc", env={"CERTCHECK_NOW": jour.isoformat()})
    donnees = lire_json_sortie(execution)
    lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
    for hote, (jours, statut) in attendus(hotes, jour, seuil).items():
        assert hote in lus and lus[hote].get("days_left") == jours and lus[hote].get("status") == statut, message(
            en=f"The installed tool returns {lus.get(hote)} for {hote}, expected {jours} days and "
            f"{statut} (today {jour}, threshold {seuil}, seed {graine}).\n  {execution.resume()}",
            fr=f"L'outil installé rend {lus.get(hote)} pour {hote}, attendu {jours} jours et "
            f"{statut} (aujourd'hui {jour}, seuil {seuil}, graine {graine}).\n  {execution.resume()}",
        )
    attendu = code_attendu([s for _, s in attendus(hotes, jour, seuil).values()])
    assert execution.code == attendu, message(
        en=f"Code {execution.code}, expected {attendu} (seed {graine}).\n  {execution.resume()}",
        fr=f"Code {execution.code}, attendu {attendu} (graine {graine}).\n  {execution.resume()}",
    )
