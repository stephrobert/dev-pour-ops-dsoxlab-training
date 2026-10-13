"""Dépendances reproductibles : cinq contrôles, vingt points chacun.

## Ce qui est noté

Ce qu'un collègue obtient en récupérant le projet, pas ce que l'apprenant a
tapé. Les fichiers du projet (`pyproject.toml`, `uv.lock`, `.python-version`,
`requirements.txt`) sont lus, puis le projet est COPIÉ sans son `.venv` et
installé dans cette copie par `uv sync --frozen` : c'est la situation du
collègue, du serveur ou de la CI, qui n'ont jamais vu le poste d'origine.

## Pourquoi `uv`, et pas l'interpréteur des tests

`dsoxlab check` lance pytest dans son propre environnement, qui ne contient
ni `requests` ni `cryptography`. L'outil se lance donc comme son auteur le
lance, par `uv` dans le répertoire du projet, `VIRTUAL_ENV` retiré : une
dépendance oubliée y échoue exactement comme ailleurs.

## Réseau

L'installation télécharge les paquets depuis PyPI (et, au besoin,
l'interpréteur fixé). Ces contrôles demandent donc un accès au réseau, au
moins la première fois : uv garde ensuite tout en cache.
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
    exiger_outil,
    exiger_workdir,
    lire_json_sortie,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "dependances-reproductibles"
DEPENDANCES = ("requests", "cryptography")
OPERATEURS_BORNE_BASSE = (">=", "~=")


@pytest.fixture(scope="module")
def projet() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


@pytest.fixture(scope="module")
def uv() -> str:
    return exiger_outil("uv")


# --- Lecture des fichiers du projet ---------------------------------------------


def _nom_normalise(nom: str) -> str:
    """`Cryptography`, `cryptography` et `crypto_graphy` désignent le même paquet (PEP 503)."""
    return re.sub(r"[-_.]+", "-", nom).lower()


def _exigence(ligne: str) -> tuple[str, str]:
    """`requests>=2.32 ; python_version >= '3.12'` -> ("requests", ">=2.32")."""
    sans_marqueur = ligne.split(";", 1)[0].strip()
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(\[[^\]]*\])?\s*(.*)$", sans_marqueur)
    if not m:
        return "", ""
    return _nom_normalise(m.group(1)), m.group(3).replace(" ", "")


def _pyproject(projet: Path) -> dict:
    chemin = projet / "pyproject.toml"
    if not chemin.is_file():
        pytest.fail("pyproject.toml est absent du projet : c'est lui qui décrit le paquet.", pytrace=False)
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(f"pyproject.toml n'est pas un TOML valide : {exc}", pytrace=False)


def _verrou(projet: Path) -> dict[str, str]:
    """Paquet -> version, tels que `uv.lock` les fige."""
    chemin = projet / "uv.lock"
    if not chemin.is_file():
        pytest.fail(
            "uv.lock est absent. Le verrou est ce qui fige la version EXACTE de chaque "
            "paquet, dépendances de dépendances comprises : `uv lock` le produit depuis "
            "pyproject.toml, et il se versionne avec le code.",
            pytrace=False,
        )
    try:
        donnees = tomllib.loads(chemin.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(f"uv.lock n'est pas lisible ({exc}) : régénérez-le par `uv lock`.", pytrace=False)
    return {_nom_normalise(p.get("name", "")): str(p.get("version", "")) for p in donnees.get("package") or []}


def _version_fixee(projet: Path) -> tuple[str, str]:
    """(version, fichier qui la porte) : `.python-version`, sinon `mise.toml`."""
    fichier = projet / ".python-version"
    if fichier.is_file():
        for brute in fichier.read_text(encoding="utf-8").splitlines():
            ligne = brute.strip()
            if ligne and not ligne.startswith("#"):
                return ligne, ".python-version"
        return "", ".python-version"
    fichier = projet / "mise.toml"
    if fichier.is_file():
        try:
            outils = tomllib.loads(fichier.read_text(encoding="utf-8")).get("tools") or {}
        except tomllib.TOMLDecodeError as exc:
            pytest.fail(f"mise.toml n'est pas un TOML valide : {exc}", pytrace=False)
        valeur = outils.get("python", "")
        if isinstance(valeur, list):
            valeur = valeur[0] if valeur else ""
        if isinstance(valeur, dict):
            valeur = valeur.get("version", "")
        return str(valeur), "mise.toml"
    return "", ""


def _tuple_version(texte: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", texte)[:3])


def _satisfait(version: str, contrainte: str) -> bool:
    """`3.14.7` satisfait-il `>=3.12,<4` ? Les opérateurs courants de requires-python suffisent ici."""
    v = _tuple_version(version)
    for clause in filter(None, (c.strip() for c in contrainte.split(","))):
        m = re.match(r"^(~=|==|!=|>=|<=|>|<)\s*([0-9][0-9.]*)(\.\*)?$", clause)
        if not m:
            continue
        operateur, borne, joker = m.group(1), _tuple_version(m.group(2)), m.group(3)
        tronque = v[: len(borne)]
        if operateur == ">=" and not v >= borne:
            return False
        if operateur == ">" and not v > borne:
            return False
        if operateur == "<=" and not v <= borne:
            return False
        if operateur == "<" and not v < borne:
            return False
        if operateur == "==" and not (tronque == borne if joker or len(borne) < 3 else v == borne):
            return False
        if operateur == "!=" and (tronque == borne if joker else v == borne):
            return False
        if operateur == "~=" and not (v >= borne and v[: len(borne) - 1] == borne[:-1]):
            return False
    return True


def _uv(uv: str, *args: str, cwd: Path, env: dict[str, str] | None = None) -> Execution:
    res = executer([uv, *args], cwd=cwd, env=env)
    return Execution(res.returncode, res.stdout, res.stderr, [uv, *args])


# --- Les contrôles ----------------------------------------------------------------


def test_les_dependances_sont_declarees_dans_pyproject(projet: Path) -> None:
    projet_toml = _pyproject(projet).get("project") or {}
    declarees = {}
    for ligne in projet_toml.get("dependencies") or []:
        nom, specification = _exigence(str(ligne))
        declarees[nom] = specification
    manquantes = [d for d in DEPENDANCES if d not in declarees]
    assert not manquantes, (
        f"[project] dependencies ne déclare pas {manquantes}. Le code importe "
        "`requests` et `cryptography` : un paquet qui ne déclare pas ce qu'il importe "
        "s'installe sans erreur, puis échoue au premier lancement chez quelqu'un "
        "d'autre. `uv add` les ajoute dans pyproject.toml."
    )
    sans_borne = [d for d in DEPENDANCES if not any(op in declarees[d] for op in OPERATEURS_BORNE_BASSE)]
    assert not sans_borne, (
        f"{sans_borne} n'ont pas de borne basse (>= ou ~=) dans pyproject.toml : "
        f"{ {d: declarees[d] or '(aucune)' for d in sans_borne} }. La borne basse dit "
        "quelle version minimale le code exige (une API apparue dans telle version). "
        "La version EXACTE, elle, appartient au verrou, pas à pyproject.toml : un "
        "`==` ici interdirait toute mise à jour de sécurité à qui installe le paquet."
    )
    requires = str(projet_toml.get("requires-python") or "")
    assert ">=" in requires or "~=" in requires, (
        f"requires-python vaut {requires or '(absent)'!r}. Sans lui, uv et pip ne "
        "savent pas sur quelles versions de Python le code tourne, et uv choisit "
        "pour vous (il le signale par un avertissement). Déclarez la plus ancienne "
        "version supportée, par exemple requires-python = \">=3.12\"."
    )


def test_le_verrou_existe_et_suit_pyproject(projet: Path, uv: str) -> None:
    verrouilles = _verrou(projet)
    absents = [d for d in DEPENDANCES if d not in verrouilles]
    assert not absents, (
        f"uv.lock ne fige pas {absents} : il a été produit avant que pyproject.toml "
        "ne les déclare. Un verrou qui ne contient pas les dépendances ne verrouille "
        "rien. Déclarez-les, puis relancez `uv lock`."
    )
    with copie_temporaire(projet) as copie:
        res = _uv(uv, "lock", "--check", cwd=copie)
    assert res.code == 0, (
        "`uv lock --check` refuse le verrou : il ne correspond plus à pyproject.toml "
        "(une dépendance, une borne, requires-python ou la version du projet a "
        "changé depuis le dernier `uv lock`). Un verrou périmé est pire qu'aucun "
        "verrou : il fait croire à une reproductibilité qui n'existe plus. Relancez "
        f"`uv lock` et versionnez le résultat.\n  {res.resume()}"
    )


def test_l_interpreteur_est_fixe(projet: Path) -> None:
    version, fichier = _version_fixee(projet)
    assert fichier, (
        "Aucune version de Python n'est fixée pour le projet : ni .python-version, "
        "ni mise.toml. requires-python dit ce qui est SUPPORTÉ ; le projet doit "
        "aussi dire ce qui est UTILISÉ, sinon chacun lance la version que son "
        "système fournit. `uv python pin 3.14.7` écrit .python-version."
    )
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), (
        f"{fichier} porte {version or '(rien)'!r} : une version précise s'écrit "
        "X.Y.Z (par exemple 3.14.7). « 3 » ou « 3.14 » laissent chaque poste "
        "choisir son correctif, et deux postes peuvent encore diverger."
    )
    requires = str((_pyproject(projet).get("project") or {}).get("requires-python") or "")
    assert requires, (
        f"{fichier} fixe Python {version}, mais pyproject.toml n'a pas de "
        "requires-python : impossible de dire si les deux s'accordent."
    )
    assert _satisfait(version, requires), (
        f"{fichier} fixe Python {version}, que requires-python ({requires}) "
        "exclut : uv refuserait de créer l'environnement. La version fixée doit "
        "appartenir à l'intervalle supporté."
    )


def test_le_projet_s_installe_a_l_identique_ailleurs(projet: Path, uv: str, tmp_path: Path) -> None:
    rnd = tirage()
    graine = rnd.randrange(10**6)
    rnd = tirage(graine)
    hotes = rnd.sample(sorted(EXPIRATIONS), rnd.randint(3, 6))
    jour = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900))
    seuil = rnd.choice([7, 15, 30, 45, 90])
    inventaire = ecrire_inventaire(tmp_path / "parc", hotes)

    with copie_temporaire(projet) as copie:
        installation = _uv(uv, "sync", "--frozen", cwd=copie)
        assert installation.code == 0, (
            "Dans une copie propre du projet (sans .venv, comme chez un collègue ou "
            "en CI), `uv sync --frozen` échoue. --frozen installe EXACTEMENT ce que "
            "dit uv.lock, sans rien résoudre : sans verrou, ou avec un verrou qui "
            "ne contient pas les dépendances, il n'y a rien à reproduire.\n  "
            f"{installation.resume()}"
        )
        version = _uv(uv, "run", "--frozen", "--quiet", "certcheck", "--version", cwd=copie)
        assert version.code == 0 and version.sortie.strip().startswith("certcheck "), (
            "Après `uv sync --frozen`, `uv run certcheck --version` échoue dans la "
            "copie. Une ModuleNotFoundError dit qu'une dépendance importée par le "
            "code n'est ni dans pyproject.toml ni dans le verrou : elle n'existait "
            f"que dans le .venv du poste d'origine.\n  {version.resume()}"
        )
        execution = _uv(uv, "run", "--frozen", "--quiet", "certcheck", "--inventory", str(inventaire),
                        "--days", str(seuil), "--format", "json", cwd=copie,
                        env={"CERTCHECK_NOW": jour.isoformat()})
    donnees = lire_json_sortie(execution)
    lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
    for hote, (jours, statut) in attendus(hotes, jour, seuil).items():
        assert hote in lus and lus[hote].get("days_left") == jours and lus[hote].get("status") == statut, (
            f"Dans la copie installée, {hote} rend {lus.get(hote)}, attendu {jours} jours "
            f"et {statut} (aujourd'hui {jour}, seuil {seuil}, graine {graine}). L'outil "
            "s'installe, mais ne rend pas le résultat du contrat.\n  "
            f"{execution.resume()}"
        )
    attendu = code_attendu([s for _, s in attendus(hotes, jour, seuil).values()])
    assert execution.code == attendu, (
        f"Code {execution.code}, attendu {attendu} (graine {graine}).\n  {execution.resume()}"
    )


def _entrees_requirements(texte: str) -> list[str]:
    """Les exigences d'un requirements.txt, lignes de continuation recollées."""
    recolle = re.sub(r"\\\s*\n", " ", texte)
    entrees = []
    for brute in recolle.splitlines():
        ligne = brute.split(" #", 1)[0].strip()
        if not ligne or ligne.startswith("#"):
            continue
        entrees.append(ligne)
    return entrees


def test_une_seule_source_de_verite(projet: Path) -> None:
    declarees = {_exigence(str(d))[0] for d in (_pyproject(projet).get("project") or {}).get("dependencies") or []}
    assert all(d in declarees for d in DEPENDANCES), (
        "pyproject.toml ne déclare pas encore requests et cryptography : tant que "
        "requirements.txt est le seul à les nommer, c'est lui la source de vérité, "
        "et elle n'est pas épinglée. Déclarez-les d'abord dans pyproject.toml."
    )
    requirements = projet / "requirements.txt"
    if not requirements.exists():
        return  # supprimé : pyproject.toml et uv.lock disent tout
    verrouilles = _verrou(projet)
    entrees = [e for e in _entrees_requirements(requirements.read_text(encoding="utf-8"))
               if not e.startswith(("-e", "--", "."))]
    assert entrees, "requirements.txt est vide : supprimez-le plutôt que de garder un fichier qui ne dit rien."
    fautives = []
    for entree in entrees:
        exigence = entree.split("--hash", 1)[0].strip()
        nom, specification = _exigence(exigence)
        m = re.fullmatch(r"==([^\s;,]+)", specification)
        if not m or "--hash=sha256:" not in entree or verrouilles.get(nom) != m.group(1):
            fautives.append(exigence)
    assert not fautives, (
        f"requirements.txt est gardé, mais {len(fautives)} ligne(s) ne viennent pas du "
        f"verrou : {fautives[:4]}. Deux listes de dépendances écrites à la main "
        "divergent tôt ou tard, et personne ne sait laquelle croire. S'il faut un "
        "requirements.txt (un outil qui ne lit que lui), il se GÉNÈRE depuis le "
        "verrou : `uv export --format requirements-txt -o requirements.txt` écrit "
        "chaque version en == avec ses empreintes --hash, identiques à uv.lock. "
        "Sinon, supprimez-le."
    )
    noms = {_exigence(e.split("--hash", 1)[0])[0] for e in entrees}
    assert all(d in noms for d in DEPENDANCES), (
        "requirements.txt ne contient ni requests ni cryptography : il n'a pas été "
        "généré depuis le verrou de ce projet. Régénérez-le par `uv export`."
    )
