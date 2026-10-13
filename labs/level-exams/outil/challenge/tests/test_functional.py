"""Épreuve : reprendre un outil d'exploitation. Cinq contrôles, vingt points chacun.

## Un projet Python, noté en boîte noire

L'apprenant livre certcheck sous la forme d'un projet Python : `pyproject.toml`,
le paquet sous `src/`, une suite pytest sous `tests/`, un CHANGELOG et une
étiquette Git. Rien ici ne lit son code : les contrôles lancent
`bin/certcheck`, sa suite de tests, l'installation de son projet dans un
environnement neuf et son dépôt Git, comme le ferait un collègue qui reprend
l'outil, et ne jugent que ce qui s'observe.

## Ce qui est attendu se calcule

- Inventaires, seuils et dates du jour sont tirés au hasard (graine affichée
  en cas d'échec), et le verdict attendu est recalculé depuis les dates
  connues des certificats (`donnees/certs/certs.json`).
- La suite de tests de l'apprenant est jouée contre trois outils : le sien,
  la référence du catalogue, et une variante de la référence qui reproduit
  l'erreur avalée du script hérité, fabriquée ici par substitution textuelle.
- Les lignes fautives de la pull request n°57 se lisent dans les fichiers
  obtenus en appliquant le diff sur une copie intacte du point de départ.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    REFERENCE,
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
    lire_yaml,
    rendre_executable,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "level-exams-outil"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
OPTIONS = ("--inventory", "--days", "--format", "--version")
# Les certificats dont le jour d'expiration s'écrit sur un chiffre : openssl
# l'affiche avec deux espaces (« Mar  5 12:00:00 2031 GMT »).
JOUR_A_UN_CHIFFRE = sorted(h for h, d in EXPIRATIONS.items() if d.day < 10)
SEMVER = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
TESTS_MINIMUM = 3


@pytest.fixture(scope="module")
def outil() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return exiger_executable(WORKDIR)


def _pyproject(texte: str, ou: str) -> dict:
    try:
        return tomllib.loads(texte)
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(f"pyproject.toml {ou} n'est pas un TOML valide : {exc}", pytrace=False)


# --- Tâche 1 : le contrat -------------------------------------------------------


def _scenario(rnd) -> tuple[list[str], date, int]:
    hotes = rnd.sample(sorted(EXPIRATIONS), rnd.randint(3, 6))
    a_un_chiffre = rnd.choice(JOUR_A_UN_CHIFFRE)
    if a_un_chiffre not in hotes:
        hotes.append(a_un_chiffre)
    seuil = rnd.choice([7, 15, 30, 45, 90])
    # Un hôte expire EXACTEMENT au seuil : le seuil est inclusif.
    limite = rnd.choice(hotes)
    jour = EXPIRATIONS[limite] - timedelta(days=seuil)
    return hotes, jour, seuil


def _inventaire_brut(dossier: Path, hotes: list[str], rnd) -> Path:
    """Un inventaire comme on en reçoit : espaces et tabulations mêlés, commentaires."""
    inventaire = ecrire_inventaire(dossier, hotes)
    lignes = ["# inventaire exporté depuis l'outil de parc", ""]
    for hote in hotes:
        lignes.append(f"{hote}{rnd.choice([' ', chr(9), '   ', ' ' + chr(9) + ' '])}certs/{hote}.pem")
    inventaire.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return inventaire


def test_le_contrat_tient_sur_des_tirages_au_hasard(outil: Path, tmp_path: Path) -> None:
    # L'interface.
    aide = lancer(outil, "--help", cwd=tmp_path)
    absentes = [o for o in OPTIONS if o not in aide.sortie]
    assert aide.code == 0 and not absentes, (
        f"--help doit sortir en 0 et citer chaque option du contrat sur la sortie "
        f"standard ; manquent : {absentes}.\n  {aide.resume()}"
    )
    version = lancer(outil, "--version", cwd=tmp_path)
    assert version.code == 0 and re.fullmatch(r"certcheck \d+\.\d+\.\d+", version.sortie.strip()), (
        f"--version doit afficher exactement « certcheck X.Y.Z » et sortir en 0.\n  {version.resume()}"
    )
    for args in (["--option-inconnue"], ["--days", "abc"], ["--format", "xml"]):
        res = lancer(outil, *args, cwd=tmp_path)
        assert res.code == 2 and not res.sortie.strip() and res.erreurs.strip(), (
            f"`certcheck {' '.join(args)}` est un usage incorrect : code 2, un message sur "
            f"la sortie d'erreur, rien sur la sortie standard.\n  {res.resume()}"
        )

    # Trois parcs tirés au hasard.
    graine = tirage().randrange(10**6)
    rnd = tirage(graine)
    for i in range(3):
        hotes, jour, seuil = _scenario(rnd)
        dossier = tmp_path / f"parc-{i}"
        inventaire = _inventaire_brut(dossier, hotes, rnd)
        attendu = attendus(hotes, jour, seuil)
        contexte = f"graine {graine}, parc {i}, aujourd'hui {jour}, seuil {seuil}"
        res = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil), "--format", "json",
                     cwd=tmp_path, env={"CERTCHECK_NOW": jour.isoformat()})
        donnees = lire_json_sortie(res)
        lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
        for hote, (jours, statut) in attendu.items():
            lu = lus.get(hote, {})
            assert (lu.get("days_left"), lu.get("status"), lu.get("not_after")) == (
                jours, statut, EXPIRATIONS[hote].isoformat()), (
                f"{hote} : lu days_left={lu.get('days_left')} status={lu.get('status')} "
                f"not_after={lu.get('not_after')}, attendu {jours}, {statut}, "
                f"{EXPIRATIONS[hote].isoformat()} ({contexte}). Vérifiez le seuil inclusif, "
                "les séparateurs (espaces ET tabulations) et les jours à un chiffre, "
                "qu'openssl écrit avec deux espaces."
            )
        code = code_attendu([s for _, s in attendu.values()])
        assert res.code == code, f"Code {res.code}, attendu {code} ({contexte}).\n  {res.resume()}"
        texte = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil),
                       cwd=tmp_path, env={"CERTCHECK_NOW": jour.isoformat()})
        for hote, (_, statut) in attendu.items():
            assert any(hote in ligne and statut in ligne for ligne in texte.sortie.splitlines()), (
                f"En --format text, aucune ligne ne porte {hote} et {statut} ({contexte}).\n"
                f"  {texte.resume()}"
            )

    # Le seuil par l'environnement, et l'option qui l'emporte.
    inventaire = ecrire_inventaire(tmp_path / "conf", ["api-01", "web-01"], separateur="\t")
    jour = EXPIRATIONS["api-01"] - timedelta(days=20)
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()
    env = {"CERTCHECK_NOW": jour.isoformat()}
    res = lancer(outil, "--inventory", str(inventaire), "--format", "json", cwd=ailleurs,
                 env={**env, "CERTCHECK_DAYS": "10"})
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"]}
    assert res.code == 0 and statuts == {"api-01": "ok", "web-01": "ok"}, (
        "CERTCHECK_DAYS=10 laisse api-01, à 20 jours, en ok (lancé depuis un autre dossier : "
        f"les chemins des certificats sont relatifs à l'inventaire).\n  {res.resume()}"
    )
    res = lancer(outil, "--inventory", str(inventaire), "--days", "30", cwd=ailleurs,
                 env={**env, "CERTCHECK_DAYS": "10"})
    assert res.code == 1, (
        f"--days 30 l'emporte sur CERTCHECK_DAYS=10 : api-01 passe en warning, code 1.\n  {res.resume()}"
    )
    res = lancer(outil, "--inventory", str(inventaire), cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "dix"})
    assert res.code == 2 and res.erreurs.strip(), (
        f"CERTCHECK_DAYS=dix est une configuration invalide : code 2 et un message.\n  {res.resume()}"
    )

    # Le certificat absent : jamais « 0 jour » comme le script hérité.
    dossier = tmp_path / "troue"
    hotes = rnd.sample(sorted(EXPIRATIONS), 3)
    inventaire = ecrire_inventaire(dossier, hotes, absents=["web-03"])
    res = lancer(outil, "--inventory", str(inventaire), "--format", "json", cwd=dossier,
                 env={"CERTCHECK_NOW": "2026-06-01"})
    lus = {c.get("host"): c for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    absent = lus.get("web-03", {})
    assert res.code == 2 and absent.get("status") == "error" and absent.get("days_left") is None, (
        "Le certificat de web-03 n'existe pas : l'hôte figure en status error, days_left "
        "null, et le code vaut 2, quelles que soient les alertes des autres hôtes. Le "
        "script hérité le comptait « 0 jour » et sortait en 0 : c'est l'erreur avalée à "
        f"corriger (graine {graine}).\n  {res.resume()}"
    )


# --- Tâche 2 : la suite de tests de l'apprenant ---------------------------------


def _lanceur(dossier: Path, nom: str, script: Path) -> Path:
    lanceur = dossier / nom / "bin" / "certcheck"
    lanceur.parent.mkdir(parents=True)
    lanceur.write_text(f'#!/usr/bin/env bash\nexec python3 "{script}" "$@"\n', encoding="utf-8")
    rendre_executable(lanceur)
    return lanceur


def _variante_boguee(dossier: Path) -> Path:
    """La référence, avec l'erreur avalée du script hérité : certificat absent = warning à 0 jour."""
    texte = REFERENCE.read_text(encoding="utf-8")
    bogues = (
        ('"days_left": None, "status": "error"', '"days_left": 0, "status": "warning"'),
        ('log.error("%s : %s", hote, exc)', 'log.debug("%s : %s", hote, exc)'),
    )
    for avant, apres in bogues:
        assert texte.count(avant) == 1, f"Référence modifiée : « {avant} » introuvable, variante impossible."
        texte = texte.replace(avant, apres)
    variante = dossier / "certcheck_bogue.py"
    variante.write_text(texte, encoding="utf-8")
    return variante


def _reussis(sortie: str) -> int:
    trouves = re.findall(r"(\d+) passed", sortie)
    return int(trouves[-1]) if trouves else 0


def test_vos_tests_attrapent_le_defaut_herite(tmp_path: Path) -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    uv = exiger_outil("uv")
    if not any((WORKDIR / "tests").glob("test_*.py")):
        pytest.fail(
            "Aucun fichier tests/test_*.py : vos tests pytest vivent dans le dossier tests/ "
            "du projet. Ils lancent l'exécutable désigné par la variable CERTCHECK_BIN "
            "(bin/certcheck par défaut), jamais une fonction importée.",
            pytrace=False,
        )
    reference = _lanceur(tmp_path, "reference", REFERENCE)
    boguee = _lanceur(tmp_path, "boguee", _variante_boguee(tmp_path))
    with copie_temporaire(WORKDIR) as copie:
        def jouer(binaire: Path):
            return executer([uv, "run", "--quiet", "--with", "pytest", "pytest", "-q", "-p", "no:cacheprovider",
                             "tests"], cwd=copie, env={"CERTCHECK_BIN": str(binaire)}, timeout=600)

        def resume(res) -> str:
            return f"code {res.returncode}\n{(res.stdout + res.stderr).strip()[-1500:]}"

        sien = jouer(copie / "bin" / "certcheck")
        assert sien.returncode == 0 and _reussis(sien.stdout) >= TESTS_MINIMUM, (
            f"`uv run pytest tests` doit passer contre VOTRE outil (CERTCHECK_BIN=bin/certcheck), "
            f"avec au moins {TESTS_MINIMUM} tests réussis ({_reussis(sien.stdout)} lus).\n" + resume(sien)
        )
        ref = jouer(reference)
        assert ref.returncode == 0, (
            "Vos tests échouent contre l'outil de RÉFÉRENCE, qui respecte CONTRAT.md : un test "
            "attend autre chose que le contrat (une version exacte, un format de texte "
            "précis, la date du jour réelle au lieu de CERTCHECK_NOW), ou la suite ignore "
            "CERTCHECK_BIN.\n" + resume(ref)
        )
        bug = jouer(boguee)
    assert bug.returncode != 0, (
        "Vos tests passent contre une variante qui reproduit le défaut du script hérité : un "
        "certificat absent y est compté « warning, 0 jour », code 1, au lieu de error et "
        "code 2. Le défaut qui a motivé la reprise n'est couvert par aucun test, ou la "
        "suite teste toujours bin/certcheck au lieu de CERTCHECK_BIN.\n" + resume(bug)
    )


# --- Tâche 3 : le projet s'installe ---------------------------------------------


def _dependances_epinglees(projet: dict) -> bool:
    """uv.lock, un requirements*.txt tout en ==, ou des dépendances de dev toutes en ==."""
    if (WORKDIR / "uv.lock").is_file():
        return True
    for fichier in WORKDIR.glob("requirements*.txt"):
        lignes = [ligne.split("#")[0].strip() for ligne in fichier.read_text(encoding="utf-8").splitlines()]
        lignes = [ligne for ligne in lignes if ligne and not ligne.startswith("-")]
        if lignes and all("==" in ligne for ligne in lignes):
            return True
    groupes = list((projet.get("dependency-groups") or {}).values())
    groupes += list(((projet.get("project") or {}).get("optional-dependencies") or {}).values())
    specs = [s for g in groupes for s in g if isinstance(s, str)]
    return bool(specs) and all("==" in s for s in specs)


def test_le_projet_s_installe_dans_un_environnement_neuf(tmp_path: Path) -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    uv = exiger_outil("uv")
    if not (WORKDIR / "pyproject.toml").is_file():
        pytest.fail("pyproject.toml est absent : le projet Python n'existe pas encore.", pytrace=False)
    projet = _pyproject((WORKDIR / "pyproject.toml").read_text(encoding="utf-8"), "du répertoire de travail")
    version = str((projet.get("project") or {}).get("version", ""))
    scripts = (projet.get("project") or {}).get("scripts") or {}
    assert "certcheck" in scripts, (
        "pyproject.toml ne déclare pas la commande `certcheck` dans [project.scripts] "
        "(forme `certcheck = \"certcheck.cli:main\"`) : une fois installé, le paquet ne "
        "créerait aucune commande."
    )
    assert any(WORKDIR.glob("src/*/__init__.py")), (
        "Aucun paquet sous src/ (src/<paquet>/__init__.py) : le code de l'outil vit dans un "
        "paquet, en src layout."
    )
    assert _dependances_epinglees(projet), (
        "Les dépendances de développement (pytest au moins) ne sont pas épinglées : un "
        "uv.lock, un requirements-dev.txt dont chaque ligne porte ==, ou un groupe "
        "[dependency-groups] dont chaque entrée porte ==. Sans cela, la même suite ne tourne "
        "pas avec les mêmes versions dans six mois."
    )
    env = tmp_path / "env"
    python = env / "bin" / "python"
    creation = executer([uv, "venv", "--quiet", str(env)], cwd=tmp_path)
    assert creation.returncode == 0, f"`uv venv` échoue : {creation.stderr.strip()}"
    with copie_temporaire(WORKDIR) as copie:
        installation = executer([uv, "pip", "install", "--quiet", "--python", str(python), str(copie)],
                                cwd=tmp_path, timeout=600)
    assert installation.returncode == 0, (
        "Le projet ne s'installe pas dans un environnement neuf (`pip install .`, ici "
        "`uv pip install`) : pyproject.toml incomplet, [build-system] absent, ou fichier "
        f"cité introuvable.\n{(installation.stdout + installation.stderr).strip()[-1200:]}"
    )
    certcheck = env / "bin" / "certcheck"
    res = lancer(certcheck, "--version", cwd=tmp_path)
    assert res.code == 0 and res.sortie.strip() == f"certcheck {version}", (
        f"Installé, `certcheck --version` doit afficher « certcheck {version} », la version "
        "de pyproject.toml : la version annoncée et la version installée disent la même "
        f"chose.\n  {res.resume()}"
    )
    rnd = tirage()
    hotes = rnd.sample(sorted(EXPIRATIONS), 4)
    jour, seuil = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900)), 30
    inventaire = ecrire_inventaire(tmp_path / "fumee", hotes)
    res = lancer(certcheck, "--inventory", str(inventaire), "--format", "json", cwd=tmp_path,
                 env={"CERTCHECK_NOW": jour.isoformat()})
    lus = {c.get("host"): (c.get("days_left"), c.get("status"))
           for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    attendu = attendus(hotes, jour, seuil)
    assert lus == attendu and res.code == code_attendu([s for _, s in attendu.values()]), (
        f"Contrôle de fumée de l'outil installé (aujourd'hui {jour}, seuil {seuil}) : lu {lus}, "
        f"attendu {attendu}.\n  {res.resume()}"
    )


# --- Tâche 4 : la version est étiquetée ------------------------------------------


def test_la_version_est_notee_et_etiquetee() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    if not (WORKDIR / ".git").exists():
        pytest.fail(
            "Le répertoire de travail n'est pas un dépôt Git : `git init`, des commits, puis "
            "une étiquette `git tag -a vX.Y.Z -m ...`.",
            pytrace=False,
        )
    noms = git("tag", "--list", cwd=WORKDIR).stdout.split()
    versions = [n for n in noms if SEMVER.match(n)]
    assert versions, (
        f"Aucune étiquette de la forme vX.Y.Z (lues : {noms or 'aucune'}). Une version livrée "
        "se repère par son étiquette : `git tag -a v1.0.0 -m \"certcheck 1.0.0\"`."
    )
    etiquette = max(versions, key=lambda n: tuple(int(x) for x in SEMVER.match(n).groups()))
    version = etiquette[1:]

    def lire(nom: str) -> str:
        res = git("show", f"{etiquette}:{nom}", cwd=WORKDIR)
        return res.stdout if res.returncode == 0 else ""

    changelog = lire("CHANGELOG.md")
    assert re.search(rf"^## \[{re.escape(version)}\]", changelog, re.MULTILINE), (
        f"Le CHANGELOG.md du commit étiqueté {etiquette} doit porter une section "
        f"`## [{version}]` : c'est ce que lit celui qui se demande ce qui a changé."
    )
    pyproject = lire("pyproject.toml")
    lue = str((_pyproject(pyproject, f"de {etiquette}").get("project") or {}).get("version", "")) if pyproject else ""
    assert lue == version, (
        f"Au commit étiqueté {etiquette}, pyproject.toml porte la version {lue!r}. L'étiquette "
        "désigne le commit qui CONTIENT la version livrée : passez la version, committez, "
        "puis étiquetez."
    )


# --- Tâche 5 : la revue de la pull request n°57 ---------------------------------

# La liste fermée de revue.yaml, aux noms du lab relire-une-automatisation.
CATEGORIES = {
    "erreur-avalee", "secret-affiche", "chemin-dangereux", "tls-desactive",
    "injection-de-commande", "dependance-non-epinglee", "test-absent",
}
# Les anciens noms restent acceptés : une revue juste ne perd pas de points
# pour un synonyme.
SYNONYMES = {"secret-expose": "secret-affiche"}
LONGUEUR_MINIMALE = 25
FAUX_POSITIFS_TOLERES = 2
DEFAUTS_A_TROUVER = 3


@dataclass(frozen=True)
class Zone:
    categorie: str
    fichier: str
    debut: int
    fin: int

    def contient(self, fichier: str, ligne: int) -> bool:
        return fichier == self.fichier and self.debut <= ligne <= self.fin


def _zone(categorie: str, fichier: str, texte: str, *motifs: str, marge: int = 2) -> Zone:
    lignes = []
    for motif in motifs:
        trouvees = [n for n, ligne in enumerate(texte.splitlines(), 1) if motif in ligne]
        if not trouvees:
            pytest.fail(f"Marqueur « {motif} » introuvable dans {fichier} après le diff : "
                        "le point de départ est abîmé.", pytrace=False)
        lignes += trouvees
    return Zone(categorie, fichier, min(lignes) - marge, max(lignes) + marge)


@pytest.fixture(scope="module")
def defauts() -> dict[str, list[Zone]]:
    """Catégorie -> zones acceptées, calculées sur le diff réellement appliqué."""
    with copie_temporaire(FIXTURES / "pr") as copie:
        res = git("apply", "../0057.diff", cwd=copie / "main")
        assert res.returncode == 0, f"pr/0057.diff ne s'applique pas : {res.stderr.strip()}"
        code = (copie / "main" / "certcheck.py").read_text(encoding="utf-8")
        tests = (copie / "main" / "tests" / "test_certcheck.py").read_text(encoding="utf-8")
    return {
        "injection-de-commande": [_zone("injection-de-commande", "certcheck.py", code,
                                        'f"openssl x509 -enddate -noout -in {certificat}"', "shell=True")],
        "erreur-avalee": [
            _zone("erreur-avalee", "certcheck.py", code, 'log.debug("%s ignoré : %s", hote, exc)'),
            _zone("erreur-avalee", "tests/test_certcheck.py", tests, "def test_un_hote_decommissionne_est_ignore"),
        ],
        "secret-affiche": [
            _zone("secret-affiche", "certcheck.py", code, 'log.debug("%s %s, en-têtes : %s", methode, url, entetes)'),
            _zone("secret-affiche", "certcheck.py", code, "logging.DEBUG if args.verbose"),
        ],
        "tls-desactive": [
            _zone("tls-desactive", "certcheck.py", code, "ssl._create_unverified_context()"),
            _zone("tls-desactive", "certcheck.py", code, "context=CONTEXTE_TLS"),
        ],
    }


def _chemin(valeur: object) -> str:
    chemin = str(valeur or "").strip().replace("\\", "/")
    for prefixe in ("./", "a/", "b/", "pr/main/"):
        chemin = chemin.removeprefix(prefixe)
    return chemin


def _categorie(valeur: object) -> str:
    categorie = str(valeur or "").strip().lower()
    return SYNONYMES.get(categorie, categorie)


def _ligne(valeur: object) -> int:
    try:
        return int(str(valeur).strip())
    except ValueError:
        return -1


def test_la_revue_de_la_pr_57_trouve_les_defauts(defauts: dict[str, list[Zone]]) -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    revue = lire_yaml(WORKDIR / "revue.yaml")
    brut = revue.get("commentaires")
    assert isinstance(brut, list) and brut, (
        "`commentaires` est vide ou n'est pas une liste : une revue sans commentaire n'aide "
        "pas l'auteur."
    )
    commentaires = []
    for element in brut:
        assert isinstance(element, dict), (
            f"Chaque commentaire est un dictionnaire (fichier, ligne, categorie, commentaire, "
            f"proposition). Lu : {element!r}"
        )
        commentaires.append((
            _chemin(element.get("fichier")), _ligne(element.get("ligne")),
            _categorie(element.get("categorie")),
            str(element.get("commentaire") or "").strip(), str(element.get("proposition") or "").strip(),
        ))
    inconnues = sorted({c[2] for c in commentaires} - CATEGORIES)
    assert not inconnues, f"Catégorie(s) hors de la liste fermée de revue.yaml : {inconnues}."
    vagues = [f"{f}:{n}" for f, n, _, texte, proposition in commentaires
              if len(texte) < LONGUEUR_MINIMALE or len(proposition) < LONGUEUR_MINIMALE]
    assert not vagues, (
        f"Commentaire(s) trop vague(s) : {vagues}. Un `commentaire` et une `proposition` "
        f"d'au moins {LONGUEUR_MINIMALE} caractères chacun : le problème, puis la correction."
    )

    def designe(zones: list[Zone]) -> bool:
        return any(z.categorie == c and z.contient(f, n) for f, n, c, _, _ in commentaires for z in zones)

    trouves = sorted(cat for cat, zones in defauts.items() if designe(zones))
    assert len(trouves) >= DEFAUTS_A_TROUVER, (
        f"{len(trouves)} défaut(s) sur 4 désignés ({trouves}) ; il en faut au moins "
        f"{DEFAUTS_A_TROUVER}. Un défaut est trouvé quand un commentaire porte le bon fichier "
        "(chemin depuis pr/main), la bonne catégorie, et une ligne à deux lignes près, "
        "comptée dans le fichier APRÈS application du diff. Confrontez chaque affirmation "
        "de pr/DESCRIPTION.md au code."
    )
    toutes = [z for zones in defauts.values() for z in zones]
    hors_sujet = [f"{f}:{n} ({c})" for f, n, c, _, _ in commentaires
                  if not any(z.categorie == c and z.contient(f, n) for z in toutes)]
    assert len(hors_sujet) <= FAUX_POSITIFS_TOLERES, (
        f"{len(hors_sujet)} commentaire(s) ne désignent aucun défaut réel : {hors_sujet}. "
        f"Au-delà de {FAUX_POSITIFS_TOLERES}, la revue noie l'essentiel."
    )
    verdict = str(revue.get("verdict") or "").strip().lower()
    assert verdict == "demander-des-changements", (
        f"`verdict` vaut {verdict!r}. Une PR qui exécute un chemin d'inventaire dans un shell, "
        "coupe la vérification TLS et journalise le jeton ne se fusionne pas : "
        "`demander-des-changements`."
    )
