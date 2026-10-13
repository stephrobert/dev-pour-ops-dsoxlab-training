"""Du script à l'outil : cinq contrôles, vingt points chacun.

## Un projet Python, jugé en boîte noire

L'outil est un projet Python : le paquet `src/certcheck/`, déclaré dans
`pyproject.toml` par `[project.scripts]`, et lancé par `bin/certcheck` à
travers `uv run`. La première tâche vérifie cette structure en l'exécutant :
la commande déclarée par le projet et `bin/certcheck` doivent répondre la
même chose. Ensuite, les contrôles lancent `bin/certcheck`, rien d'autre :
seul compte ce qu'un appelant observe : sortie standard, sortie d'erreur et
code de sortie. C'est exactement la position de cron ou d'un pipeline, qui ne lisent
jamais le code.

## Ce qui est attendu se calcule

Inventaires, seuils et dates du jour sont tirés au hasard (graine affichée en
cas d'échec), et le résultat attendu est recalculé ici depuis les dates
d'expiration connues des certificats. Un outil qui imprimerait un résultat
en dur échoue.
"""

from __future__ import annotations

import ast
import tomllib
from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    attendus,
    code_attendu,
    ecrire_inventaire,
    exiger_executable,
    exiger_outil,
    exiger_workdir,
    lancer,
    lire_json_sortie,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "script-en-outil"
OPTIONS = ("--inventory", "--days", "--format", "--version")


@pytest.fixture(scope="module")
def outil() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return exiger_executable(WORKDIR)


def _scenario(graine: int | None = None) -> tuple[list[str], date, int, int]:
    rnd = tirage(graine)
    graine = rnd.randrange(10**6) if graine is None else graine
    rnd = tirage(graine)
    hotes = rnd.sample(sorted(EXPIRATIONS), rnd.randint(3, 7))
    jour = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900))
    seuil = rnd.choice([7, 15, 30, 45, 90])
    return hotes, jour, seuil, graine


def _exiger_le_paquet(outil: Path, tmp_path: Path) -> None:
    """bin/certcheck lance le paquet Python du projet, déclaré dans pyproject.toml."""
    pyproject = WORKDIR / "pyproject.toml"
    assert pyproject.is_file(), "pyproject.toml est absent : le projet n'est plus un projet Python."
    try:
        scripts = tomllib.loads(pyproject.read_text(encoding="utf-8")).get("project", {}).get("scripts", {})
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(f"pyproject.toml n'est pas un TOML valide : {exc}", pytrace=False)
    cible = str(scripts.get("certcheck", ""))
    module, _, fonction = cible.partition(":")
    assert module and fonction, (
        "pyproject.toml ne déclare pas la commande `certcheck` dans [project.scripts], "
        f"sous la forme module:fonction (lu : {cible!r}). C'est cette déclaration qui "
        "crée la commande dans l'environnement du projet."
    )
    assert (WORKDIR / "src" / "certcheck" / "__init__.py").is_file(), (
        "src/certcheck/__init__.py est absent : le code de l'outil vit dans le paquet "
        "src/certcheck/ (src layout), pas dans un script à la racine."
    )
    fichier = WORKDIR / "src" / Path(*module.split(".")).with_suffix(".py")
    definies = set()
    if fichier.is_file():
        definies = {n.name for n in ast.walk(ast.parse(fichier.read_text(encoding="utf-8")))
                    if isinstance(n, ast.FunctionDef)}
    assert fonction in definies, (
        f"[project.scripts] désigne {cible}, mais {fichier.relative_to(WORKDIR)} ne définit "
        f"pas de fonction {fonction}."
    )
    uv = exiger_outil("uv")
    par_uv = lancer(Path(uv), "run", "--quiet", "--project", str(WORKDIR), "certcheck", "--version",
                    cwd=tmp_path)
    par_bin = lancer(outil, "--version", cwd=tmp_path)
    assert par_uv.code == 0 and par_bin.code == 0 and par_uv.sortie == par_bin.sortie, (
        "bin/certcheck ne lance pas le paquet du projet : `uv run certcheck --version` et "
        "`bin/certcheck --version` doivent sortir en 0 et répondre la même chose. Le "
        "lanceur fourni (`uv run --quiet --project ... certcheck`) suffit ; il échoue tant "
        f"que les fonctions lèvent NotImplementedError.\n  {par_uv.resume()}\n  {par_bin.resume()}"
    )


def test_l_interface_est_previsible(outil: Path, tmp_path: Path) -> None:
    _exiger_le_paquet(outil, tmp_path)
    aide = lancer(outil, "--help", cwd=tmp_path)
    assert aide.code == 0, f"--help doit sortir en 0.\n  {aide.resume()}"
    absentes = [o for o in OPTIONS if o not in aide.sortie]
    assert not absentes, (
        f"L'aide ne cite pas {absentes} : un outil se découvre par --help, sur la "
        f"sortie standard.\n  {aide.resume()}"
    )
    version = lancer(outil, "--version", cwd=tmp_path)
    assert version.code == 0 and version.sortie.strip().startswith("certcheck "), (
        f"--version doit afficher « certcheck X.Y.Z » et sortir en 0.\n  {version.resume()}"
    )
    for args in (["--option-inconnue"], ["--days", "abc"], ["--format", "xml"]):
        res = lancer(outil, *args, cwd=tmp_path)
        assert res.code == 2 and not res.sortie.strip() and res.erreurs.strip(), (
            f"`certcheck {' '.join(args)}` est un usage incorrect : code 2, un message "
            "sur la sortie d'erreur, rien sur la sortie standard (un appelant qui lit "
            f"la sortie standard ne doit pas y trouver de prose).\n  {res.resume()}"
        )


def test_les_codes_de_sortie_suivent_le_contrat(outil: Path, tmp_path: Path) -> None:
    for i in range(3):
        hotes, jour, seuil, graine = _scenario()
        dossier = tmp_path / f"parc-{i}"
        inventaire = ecrire_inventaire(dossier, hotes)
        attendu = code_attendu([s for _, s in attendus(hotes, jour, seuil).values()])
        res = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil),
                     cwd=dossier, env={"CERTCHECK_NOW": jour.isoformat()})
        assert res.code == attendu, (
            f"Code {res.code}, attendu {attendu} (graine {graine}, aujourd'hui {jour}, "
            f"seuil {seuil}). 0 : tout est valide ; 1 : au moins un certificat à "
            f"renouveler ou expiré.\n  {res.resume()}"
        )
    # Tout est valide : 0.
    dossier = tmp_path / "sain"
    inventaire = ecrire_inventaire(dossier, ["web-01", "mail-01", "dns-01"])
    res = lancer(outil, "--inventory", str(inventaire), cwd=dossier, env={"CERTCHECK_NOW": "2026-06-01"})
    assert res.code == 0, f"Trois certificats valides au-delà du seuil : code 0 attendu.\n  {res.resume()}"
    # Un certificat absent : l'entrée est inexploitable, 2, même s'il y a des alertes.
    dossier = tmp_path / "troue"
    inventaire = ecrire_inventaire(dossier, ["web-02", "web-01"], absents=["web-03"])
    res = lancer(outil, "--inventory", str(inventaire), cwd=dossier, env={"CERTCHECK_NOW": "2026-06-01"})
    assert res.code == 2, (
        "Le certificat de web-03 n'existe pas : l'entrée est inexploitable, code 2, "
        "jamais un « 0 jour » silencieux comme le script hérité, et jamais 1, qui "
        f"ferait croire à une simple alerte.\n  {res.resume()}"
    )
    res = lancer(outil, "--inventory", str(tmp_path / "absent.txt"), cwd=tmp_path)
    assert res.code == 2 and res.erreurs.strip(), (
        f"Un inventaire absent : code 2 et un message sur la sortie d'erreur.\n  {res.resume()}"
    )


def test_la_sortie_json_est_exploitable(outil: Path, tmp_path: Path) -> None:
    hotes, jour, seuil, graine = _scenario()
    # Un certificat qui expire EXACTEMENT au seuil : le seuil est inclusif.
    limite = "proxy-01"
    jour = EXPIRATIONS[limite] - timedelta(days=seuil)
    if limite not in hotes:
        hotes.append(limite)
    inventaire = ecrire_inventaire(tmp_path, hotes)
    res = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil), "--format", "json",
                 cwd=tmp_path, env={"CERTCHECK_NOW": jour.isoformat()})
    donnees = lire_json_sortie(res)
    lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
    for hote, (jours, statut) in attendus(hotes, jour, seuil).items():
        assert hote in lus, f"{hote} manque dans `certificates` (graine {graine}).\n  {res.resume()}"
        assert lus[hote].get("days_left") == jours and lus[hote].get("status") == statut, (
            f"{hote} : days_left={lus[hote].get('days_left')} status={lus[hote].get('status')}, "
            f"attendu {jours} et {statut} (aujourd'hui {jour}, seuil {seuil}, graine {graine}). "
            "Le seuil est inclusif : un certificat qui expire dans exactement N jours "
            "avec --days N est en warning."
        )
        assert lus[hote].get("not_after") == EXPIRATIONS[hote].isoformat(), (
            f"{hote} : not_after doit valoir la date d'expiration en AAAA-MM-JJ."
        )
    texte = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil),
                   cwd=tmp_path, env={"CERTCHECK_NOW": jour.isoformat()})
    for hote, (_, statut) in attendus(hotes, jour, seuil).items():
        assert any(hote in ligne and statut in ligne for ligne in texte.sortie.splitlines()), (
            f"En --format text, aucune ligne ne porte à la fois {hote} et {statut}.\n  {texte.resume()}"
        )


def test_le_seuil_vient_de_l_environnement(outil: Path, tmp_path: Path) -> None:
    # Tabulation comme séparateur, et un lancement depuis un autre dossier :
    # les chemins des certificats se résolvent depuis celui de l'inventaire.
    inventaire = ecrire_inventaire(tmp_path / "parc", ["api-01", "web-01"], separateur="\t")
    jour = EXPIRATIONS["api-01"] - timedelta(days=20)  # api-01 expire dans 20 jours
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()

    def jouer(*args: str, days: str):
        return lancer(outil, "--inventory", str(inventaire), "--format", "json", *args, cwd=ailleurs,
                      env={"CERTCHECK_NOW": jour.isoformat(), "CERTCHECK_DAYS": days})

    res = jouer(days="10")
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    assert statuts == {"api-01": "ok", "web-01": "ok"} and res.code == 0, (
        "CERTCHECK_DAYS=10 doit laisser api-01, à 20 jours, en ok, et le code à 0 "
        "(inventaire séparé par une tabulation, lancé depuis un autre dossier : les "
        f"chemins des certificats sont relatifs à l'inventaire).\n  {res.resume()}"
    )
    res = jouer(days="45")
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    assert statuts.get("api-01") == "warning" and res.code == 1, (
        "CERTCHECK_DAYS=45 doit faire passer api-01, à 20 jours, en warning, code 1 : "
        f"la variable est-elle lue ?\n  {res.resume()}"
    )
    res = jouer("--days", "10", days="45")
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    assert statuts.get("api-01") == "ok" and res.code == 0, (
        "--days 10 doit l'emporter sur CERTCHECK_DAYS=45 : api-01 reste ok, code 0. "
        f"L'option gagne toujours sur la variable.\n  {res.resume()}"
    )
    res = jouer(days="dix")
    assert res.code == 2 and res.erreurs.strip() and not res.sortie.strip(), (
        "CERTCHECK_DAYS=dix est une configuration invalide : code 2, un message sur la "
        f"sortie d'erreur, rien sur la sortie standard.\n  {res.resume()}"
    )


def test_les_erreurs_vont_sur_la_sortie_d_erreur(outil: Path, tmp_path: Path) -> None:
    inventaire = ecrire_inventaire(tmp_path, ["web-01", "vpn-01"], absents=["web-03"])
    res = lancer(outil, "--inventory", str(inventaire), "--format", "json", cwd=tmp_path,
                 env={"CERTCHECK_NOW": "2026-06-01"})
    donnees = lire_json_sortie(res)  # échoue si un message pollue la sortie standard
    lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
    absent = lus.get("web-03", {})
    assert absent.get("status") == "error" and absent.get("days_left") is None, (
        "Le certificat de web-03 n'existe pas : il figure dans le JSON en status error, "
        f"days_left null. Il ne disparaît pas, et il ne passe pas pour valide.\n  {res.resume()}"
    )
    assert "web-03" in res.erreurs, (
        "Le problème de web-03 doit être signalé sur la SORTIE D'ERREUR, en le nommant : "
        "la sortie standard ne porte que le document JSON, qu'un programme va lire. "
        f"`log.error(...)` ou `print(..., file=sys.stderr)`.\n  {res.resume()}"
    )
    res = lancer(outil, "--inventory", str(tmp_path / "absent.txt"), cwd=tmp_path)
    assert res.code == 2 and res.erreurs.strip() and not res.sortie.strip(), (
        "Un inventaire absent : code 2, un message sur la sortie d'erreur, et RIEN sur la "
        "sortie standard (pas de trace Python non plus : l'erreur est attrapée et "
        f"expliquée).\n  {res.resume()}"
    )
    assert "Traceback" not in res.erreurs, (
        "Un inventaire absent produit une trace Python : attrapez l'erreur (ErreurUsage) "
        f"et écrivez un message d'une ligne qui nomme le fichier.\n  {res.resume()}"
    )
