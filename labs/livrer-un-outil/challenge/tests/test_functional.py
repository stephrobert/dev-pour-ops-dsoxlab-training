"""Livrer un outil interne : cinq contrôles, vingt points chacun.

## Ce qui est noté

Ce qu'un utilisateur de l'outil obtient, pas les commandes tapées : la
version affichée, le journal des changements, l'étiquette Git, les
artefacts de `dist/`, et surtout une installation VIERGE depuis
l'étiquette. Le dépôt est cloné à `v1.0.0` dans un dossier temporaire, la
roue y est construite puis installée dans un environnement neuf, et
certcheck y tourne sur un inventaire tiré au hasard. C'est exactement ce que
fait celui qui installe la 1.0.0 sans jamais avoir vu votre poste.

## Pourquoi vérifier que le dépôt est bien celui du lab

Le répertoire de travail vit À L'INTÉRIEUR du dépôt du catalogue. Sans
`git init` dans ce répertoire, toute commande Git y remonterait au dépôt du
catalogue, et lirait ses étiquettes au lieu des vôtres. Chaque contrôle Git
exige donc que la racine du dépôt soit le répertoire de travail lui-même.

## Réseau

uv construit avec le backend `uv_build` qu'il embarque (rien à télécharger
quand la contrainte de `[build-system]` accepte sa version), mais
l'installation vierge télécharge les dépendances depuis PyPI : ces contrôles
demandent un accès au réseau, au moins la première fois.
"""

from __future__ import annotations

import re
import tomllib
import zipfile
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
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "livrer-un-outil"
VERSION = "1.0.0"
ETIQUETTE = f"v{VERSION}"
ROUE = f"certcheck-{VERSION}-py3-none-any.whl"
SDIST = f"certcheck-{VERSION}.tar.gz"
RUBRIQUES = ("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security",
             "Ajouté", "Modifié", "Obsolète", "Supprimé", "Corrigé", "Sécurité")


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
        pytest.fail(f"pyproject.toml ({ou}) n'est pas un TOML valide : {exc}", pytrace=False)


def _exiger_depot(projet: Path) -> None:
    """Le répertoire de travail est la racine de SON dépôt, pas un dossier du catalogue."""
    racine = git("rev-parse", "--show-toplevel", cwd=projet)
    if not (projet / ".git").exists() or Path(racine.stdout.strip()).resolve() != projet.resolve():
        pytest.fail(
            "Le répertoire de travail n'est pas un dépôt Git : lancez `git init` "
            "DANS ce répertoire, puis committez le projet. Sans lui, Git remonte au "
            "dépôt du catalogue qui le contient, et vos commits et étiquettes "
            "n'existeraient pas là où on les cherche.",
            pytrace=False,
        )


def _exiger_etiquette(projet: Path) -> None:
    _exiger_depot(projet)
    nature = git("cat-file", "-t", ETIQUETTE, cwd=projet)
    if nature.returncode != 0:
        etiquettes = git("tag", "--list", cwd=projet).stdout.split()
        pytest.fail(
            f"L'étiquette {ETIQUETTE} n'existe pas (étiquettes présentes : "
            f"{etiquettes or 'aucune'}). Une version livrée se repère par une "
            f"étiquette : `git tag -a {ETIQUETTE} -m \"certcheck {VERSION}\"`.",
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
    assert version == VERSION, (
        f"pyproject.toml porte la version {version!r}, attendu {VERSION!r}. C'est la "
        "SEULE place où la version s'écrit : la roue, le sdist et `certcheck "
        "--version` la tirent de là."
    )
    en_dur = sorted(
        str(f.relative_to(projet)) for f in (projet / "src").rglob("*")
        if f.is_file() and f.suffix in (".py", ".txt", ".toml", ".cfg", ".json")
        and VERSION in f.read_text(encoding="utf-8", errors="ignore")
    )
    assert not en_dur, (
        f"{en_dur} écrivent « {VERSION} » en dur. Deux endroits pour une version, "
        "c'est deux versions le jour où l'un est oublié (la 0.5.0 en est un "
        "exemple). Le code lit la version dans les métadonnées du paquet installé : "
        "`importlib.metadata.version(\"certcheck\")`."
    )
    affichee = lancer(exiger_executable(projet), "--version", cwd=projet)
    assert affichee.code == 0 and affichee.sortie.strip() == f"certcheck {VERSION}", (
        f"`bin/certcheck --version` doit afficher exactement « certcheck {VERSION} ».\n"
        f"  {affichee.resume()}"
    )
    # La preuve par le comportement : changez la version de pyproject.toml dans
    # une copie, et l'outil doit suivre sans qu'on touche au code.
    essai = f"9.{tirage().randint(1, 98)}.{tirage().randint(1, 98)}"
    with copie_temporaire(projet) as copie:
        pyproject = copie / "pyproject.toml"
        pyproject.write_text(re.sub(r'(?m)^version\s*=\s*"[^"]*"', f'version = "{essai}"',
                                    pyproject.read_text(encoding="utf-8"), count=1), encoding="utf-8")
        suivie = _uv(uv, "run", "--quiet", "certcheck", "--version", cwd=copie)
    assert suivie.code == 0 and suivie.sortie.strip() == f"certcheck {essai}", (
        f"Dans une copie où pyproject.toml passe à {essai}, certcheck --version "
        f"affiche {suivie.sortie.strip() or '(rien)'!r} : la version n'est pas lue "
        "dans les métadonnées du paquet, elle vient d'ailleurs.\n  "
        f"{suivie.resume()}"
    )


def test_le_changelog_porte_la_version(projet: Path) -> None:
    chemin = projet / "CHANGELOG.md"
    assert chemin.is_file(), "CHANGELOG.md a disparu : c'est lui qui dit aux utilisateurs ce qui change."
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    titres = [(i, m) for i, ligne in enumerate(lignes)
              if (m := re.match(r"^##\s+\[([^\]]+)\](?:\s+-\s+(\S+))?\s*$", ligne))]
    versions = [m.group(1) for _, m in titres]
    assert VERSION in versions, (
        f"CHANGELOG.md n'a pas de section `## [{VERSION}] - AAAA-MM-JJ` (sections "
        f"trouvées : {versions}). Au format Keep a Changelog, livrer, c'est déplacer "
        f"le contenu de [Unreleased] sous un titre daté [{VERSION}]."
    )
    rang = versions.index(VERSION)
    debut, titre = titres[rang]
    jour = titre.group(2) or ""
    try:
        date.fromisoformat(jour)
    except ValueError:
        pytest.fail(
            f"La section [{VERSION}] porte la date {jour or '(aucune)'!r} : le format est "
            f"`## [{VERSION}] - AAAA-MM-JJ`, la date de la livraison.",
            pytrace=False,
        )
    fin = titres[rang + 1][0] if rang + 1 < len(titres) else len(lignes)
    corps = lignes[debut + 1:fin]
    rubriques = [ligne for ligne in corps if re.match(rf"^###\s+({'|'.join(RUBRIQUES)})\s*$", ligne)]
    entrees = [ligne for ligne in corps if re.match(r"^\s*[-*]\s+\S", ligne)]
    assert rubriques and entrees, (
        f"La section [{VERSION}] est vide ou sans rubrique : il faut au moins une "
        "rubrique `### Ajouté` / `### Modifié` / `### Corrigé` (ou Added, Changed, "
        "Fixed) et une entrée `- ...`. Un utilisateur lit cette section pour décider "
        "s'il met à jour."
    )
    au_dessus = [v for v in versions[:rang] if v.lower() != "unreleased"]
    assert not au_dessus, (
        f"{au_dessus} apparaissent au-dessus de [{VERSION}]. Le journal se lit du plus "
        f"récent au plus ancien : [Unreleased] en tête, puis [{VERSION}], puis les "
        "versions précédentes."
    )


def test_l_etiquette_annotee_designe_la_livraison(projet: Path, uv: str) -> None:
    _exiger_etiquette(projet)
    nature = git("cat-file", "-t", ETIQUETTE, cwd=projet).stdout.strip()
    assert nature == "tag", (
        f"{ETIQUETTE} est une étiquette LÉGÈRE (elle désigne directement un {nature}). "
        "Une étiquette annotée porte un auteur, une date et un message, et c'est "
        "elle que `git describe` et les forges traitent comme une version : "
        f"`git tag -d {ETIQUETTE}` puis `git tag -a {ETIQUETTE} -m \"certcheck {VERSION}\"`."
    )
    pyproject = git("show", f"{ETIQUETTE}:pyproject.toml", cwd=projet)
    version = _version_pyproject(pyproject.stdout, f"à l'étiquette {ETIQUETTE}") if pyproject.returncode == 0 else ""
    assert version == VERSION, (
        f"Au commit étiqueté {ETIQUETTE}, pyproject.toml porte la version {version!r}. "
        "L'étiquette a été posée avant le commit du passage en 1.0.0 : elle doit "
        "désigner le commit qui CONTIENT la version livrée."
    )
    etat = git("status", "--porcelain", cwd=projet)
    assert not etat.stdout.strip(), (
        "L'arbre de travail n'est pas propre : des fichiers modifiés ou non suivis "
        f"ne sont pas dans le commit étiqueté.\n{etat.stdout.strip()[:600]}\n"
        "Ce qui est livré doit être exactement ce qui est étiqueté : committez (ou "
        "ignorez dans .gitignore ce qui se régénère, comme .venv/ et dist/), puis "
        "replacez l'étiquette sur ce commit."
    )
    with copie_temporaire(projet, avec_git=True) as copie:
        git("checkout", "-q", "--force", ETIQUETTE, cwd=copie)
        verrou = _uv(uv, "lock", "--check", cwd=copie)
    assert verrou.code == 0, (
        f"Au commit étiqueté, uv.lock ne correspond pas à pyproject.toml. Le verrou "
        "enregistre aussi la version du projet : passer pyproject.toml en "
        f"{VERSION} sans relancer `uv lock` livre un verrou périmé.\n  {verrou.resume()}"
    )


def test_dist_contient_la_roue_et_le_sdist(projet: Path) -> None:
    dist = projet / "dist"
    presents = sorted(f.name for f in dist.iterdir()) if dist.is_dir() else []
    manquants = [n for n in (ROUE, SDIST) if n not in presents]
    assert not manquants, (
        f"dist/ ne contient pas {manquants} (présents : {presents or 'rien'}). "
        "`uv build` construit la roue (ce qui s'installe) et le sdist (les sources), "
        "à partir de la version de pyproject.toml."
    )
    try:
        with zipfile.ZipFile(dist / ROUE) as roue:
            metadonnees = roue.read(f"certcheck-{VERSION}.dist-info/METADATA").decode()
            points = roue.read(f"certcheck-{VERSION}.dist-info/entry_points.txt").decode()
    except (zipfile.BadZipFile, KeyError) as exc:
        pytest.fail(f"{ROUE} n'est pas une roue lisible ({exc}) : reconstruisez-la par `uv build`.",
                    pytrace=False)
    requis = {re.split(r"[\s<>=!~;\[]", ligne.split(":", 1)[1].strip())[0].lower()
              for ligne in metadonnees.splitlines() if ligne.startswith("Requires-Dist:")}
    assert re.search(rf"(?m)^Version:\s*{re.escape(VERSION)}$", metadonnees) and {"requests", "cryptography"} <= requis, (
        f"Les métadonnées de la roue doivent porter Version: {VERSION} et déclarer "
        f"requests et cryptography (Requires-Dist trouvés : {sorted(requis)}). Sans "
        "elles, la roue s'installe sans ses dépendances."
    )
    assert re.search(r"(?m)^certcheck\s*=\s*certcheck\.cli:main\s*$", points), (
        "La roue ne déclare pas le point d'entrée `certcheck = certcheck.cli:main` : "
        "une fois installée, aucune commande `certcheck` n'existerait."
    )


def test_l_etiquette_s_installe_dans_un_environnement_vierge(projet: Path, uv: str, tmp_path: Path) -> None:
    _exiger_etiquette(projet)
    clone = tmp_path / "clone"
    res = git("clone", "-q", "--branch", ETIQUETTE, str(projet), str(clone), cwd=tmp_path)
    assert res.returncode == 0, f"`git clone --branch {ETIQUETTE}` échoue :\n{res.stderr.strip()}"
    construction = _uv(uv, "build", "--quiet", cwd=clone)
    roues = sorted((clone / "dist").glob("certcheck-*.whl"))
    assert construction.code == 0 and roues, (
        "Le dépôt cloné à l'étiquette ne se construit pas : il manque au commit "
        "étiqueté un fichier que votre poste possède (README.md cité par "
        "pyproject.toml, un module non commité...).\n  "
        f"{construction.resume()}"
    )
    assert roues[0].name == ROUE, (
        f"Construite depuis l'étiquette {ETIQUETTE}, la roue s'appelle {roues[0].name}, "
        f"attendu {ROUE} : le commit étiqueté ne porte pas la version {VERSION}."
    )
    env = tmp_path / "env"
    creation = _uv(uv, "venv", "--quiet", str(env), cwd=clone)
    assert creation.code == 0, f"`uv venv` échoue dans le clone.\n  {creation.resume()}"
    installation = _uv(uv, "pip", "install", "--quiet", "--python", str(env / "bin" / "python"),
                       str(roues[0]), cwd=tmp_path)
    assert installation.code == 0, (
        "La roue ne s'installe pas dans un environnement neuf : ses dépendances "
        f"déclarées ne se résolvent pas.\n  {installation.resume()}"
    )
    certcheck = env / "bin" / "certcheck"
    version = lancer(certcheck, "--version", cwd=tmp_path)
    assert version.code == 0 and version.sortie.strip() == f"certcheck {VERSION}", (
        f"Installé depuis la roue de l'étiquette, `certcheck --version` doit afficher "
        f"« certcheck {VERSION} ». Une version lue dans pyproject.toml par un chemin "
        "de fichier casse ici : une roue installée n'emporte pas pyproject.toml, "
        f"seulement ses métadonnées.\n  {version.resume()}"
    )
    hotes, jour, seuil, graine = _scenario()
    inventaire = ecrire_inventaire(tmp_path / "parc", hotes)
    execution = lancer(certcheck, "--inventory", str(inventaire), "--days", str(seuil), "--format", "json",
                       cwd=tmp_path / "parc", env={"CERTCHECK_NOW": jour.isoformat()})
    donnees = lire_json_sortie(execution)
    lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
    for hote, (jours, statut) in attendus(hotes, jour, seuil).items():
        assert hote in lus and lus[hote].get("days_left") == jours and lus[hote].get("status") == statut, (
            f"L'outil installé rend {lus.get(hote)} pour {hote}, attendu {jours} jours et "
            f"{statut} (aujourd'hui {jour}, seuil {seuil}, graine {graine}).\n  {execution.resume()}"
        )
    attendu = code_attendu([s for _, s in attendus(hotes, jour, seuil).values()])
    assert execution.code == attendu, f"Code {execution.code}, attendu {attendu} (graine {graine}).\n  {execution.resume()}"
