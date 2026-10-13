"""Du script à l'outil : cinq contrôles, vingt points chacun.

## Une boîte noire, dans n'importe quel langage

Les contrôles lancent `bin/certcheck`, rien d'autre. L'outil peut être écrit
en Python, en Go ou en Bash : seul compte ce qu'un appelant observe, sorties,
code de sortie et requêtes réseau. C'est exactement la position de cron ou
d'un pipeline, qui ne lisent jamais le code.

## Ce qui est attendu se calcule

Inventaires, seuils et dates du jour sont tirés au hasard (graine affichée en
cas d'échec), et le résultat attendu est recalculé ici depuis les dates
d'expiration connues des certificats. Un outil qui imprimerait un résultat
en dur échoue.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    Forge,
    attendus,
    code_attendu,
    ecrire_inventaire,
    exiger_executable,
    exiger_workdir,
    lancer,
    lire_json_sortie,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "script-en-outil"
OPTIONS = ("--inventory", "--days", "--format", "--publish", "--dry-run", "--verbose", "--version")


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


def test_l_interface_est_previsible(outil: Path, tmp_path: Path) -> None:
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


def test_la_configuration_vient_de_l_environnement(outil: Path, tmp_path: Path) -> None:
    # Séparateurs mêlés et commentaires, comme dans un vrai inventaire.
    inventaire = ecrire_inventaire(tmp_path / "parc", ["api-01", "web-01"], separateur="\t")
    jour = EXPIRATIONS["api-01"] - timedelta(days=20)  # api-01 expire dans 20 jours
    env = {"CERTCHECK_NOW": jour.isoformat(), "CERTCHECK_INVENTORY": str(inventaire)}
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()
    res = lancer(outil, "--format", "json", cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "10"})
    donnees = lire_json_sortie(res)
    statuts = {c.get("host"): c.get("status") for c in donnees["certificates"] if isinstance(c, dict)}
    assert statuts == {"api-01": "ok", "web-01": "ok"} and res.code == 0, (
        "CERTCHECK_INVENTORY doit désigner l'inventaire (lancé depuis un autre dossier, "
        "chemins des certificats relatifs à l'inventaire, tabulation comme séparateur), "
        f"et CERTCHECK_DAYS=10 doit laisser api-01 (20 jours) en ok.\n  {res.resume()}"
    )
    res = lancer(outil, "--format", "json", "--days", "30", cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "10"})
    donnees = lire_json_sortie(res)
    statuts = {c.get("host"): c.get("status") for c in donnees["certificates"] if isinstance(c, dict)}
    assert statuts.get("api-01") == "warning" and res.code == 1, (
        "--days 30 doit l'emporter sur CERTCHECK_DAYS=10 : api-01, à 20 jours, passe en "
        f"warning et le code vaut 1. L'option gagne toujours sur la variable.\n  {res.resume()}"
    )
    res = lancer(outil, "--format", "json", cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "dix"})
    assert res.code == 2 and res.erreurs.strip(), (
        f"CERTCHECK_DAYS=dix est une configuration invalide : code 2 et un message.\n  {res.resume()}"
    )


def test_le_mode_simulation_n_envoie_rien(outil: Path, tmp_path: Path, forge: Forge) -> None:
    inventaire = ecrire_inventaire(tmp_path, ["web-02", "web-01"])  # web-02 a expiré
    env = {"CERTCHECK_NOW": "2026-06-01"}
    res = lancer(outil, "--inventory", str(inventaire), "--publish", "--dry-run",
                 cwd=tmp_path, env={**env, **forge.env()})
    assert not forge.requetes, (
        f"--dry-run a envoyé {len(forge.requetes)} requête(s) à la forge : une simulation "
        f"ne touche à rien.\n  {res.resume()}"
    )
    assert res.code == 1 and "web-02" in res.erreurs, (
        "En simulation, le ticket qui serait ouvert s'affiche sur la sortie d'erreur "
        f"(il cite web-02), et le code reste celui du contrôle, 1.\n  {res.resume()}"
    )
    sans_jeton = {k: v for k, v in forge.env().items() if k != "FORGE_TOKEN"}
    res = lancer(outil, "--inventory", str(inventaire), "--publish", cwd=tmp_path, env={**env, **sans_jeton})
    assert res.code == 2 and not forge.requetes and "FORGE_TOKEN" in res.erreurs, (
        "--publish sans FORGE_TOKEN : la configuration est incomplète, code 2, un message "
        f"qui nomme la variable manquante, et aucune requête.\n  {res.resume()}"
    )
