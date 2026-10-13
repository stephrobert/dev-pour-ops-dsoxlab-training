"""Déboguer avec méthode : cinq contrôles, vingt points chacun.

## Ce qui est noté : la méthode, pas seulement la correction

Une correction sans test qui reproduit le bogue ne protège pas du retour du
bogue ; une correction qui casse le reste du contrat en ouvre un autre. Les
cinq contrôles suivent donc la démarche :

1. un test de l'apprenant REPRODUIT le bogue : sa suite échoue sur la version
   boguée d'origine (`fixtures/src/certcheck/certificats.py`) et passe sur
   la référence ;
2. le bogue est corrigé, vu de l'extérieur : `bin/certcheck` lit les
   certificats dont le jour n'a qu'un chiffre, sur des parcs et des dates
   tirés au hasard ;
3. la suite de l'apprenant, enrichie, passe sur sa version corrigée ;
4. aucune régression : le reste du contrat tient toujours, et un certificat
   vraiment illisible laisse désormais une trace sur la sortie d'erreur ;
5. le journal `DEBUG.md` dit, en trois rubriques simples, ce qui a été vu,
   la cause et la correction.

Les contrôles 3 et 4 n'ont de sens que sur une version corrigée : ils
l'exigent d'abord, sans quoi le point de départ les passerait sans travail.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from functools import cache
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    REFERENCE_PAQUET,
    Passage,
    attendus,
    code_attendu,
    ecrire_inventaire,
    exiger_executable,
    exiger_workdir,
    jouer_suite_paquet,
    lancer,
    lire_json_sortie,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "deboguer"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
BOGUE = FIXTURES / "src" / "certcheck" / "certificats.py"
REFERENCE = REFERENCE_PAQUET / "certificats.py"
# Les certificats dont openssl écrit le jour avec deux espaces (« Mar  5 »).
UN_CHIFFRE = sorted(h for h, d in EXPIRATIONS.items() if d.day < 10)
DEUX_CHIFFRES = sorted(h for h, d in EXPIRATIONS.items() if d.day >= 10)
# Les trois rubriques de DEBUG.md, reconnues par un mot de leur titre.
RUBRIQUES = {"vu": "Ce que j'ai vu", "cause": "La cause", "correction": "La correction"}


@cache
def jouer(projet: str, outil: str | None) -> Passage:
    exiger_workdir(WORKDIR, LAB_ID)
    return jouer_suite_paquet(Path(projet), Path(outil) if outil else None)


@pytest.fixture(scope="module")
def outil() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return exiger_executable(WORKDIR)


def _vpn_01_est_lu(outil: Path, dossier: Path) -> None:
    """Le symptôme du ticket a disparu, sinon les contrôles suivants n'ont pas de sens."""
    inventaire = ecrire_inventaire(dossier, ["vpn-01"])
    res = lancer(outil, "--inventory", str(inventaire), "--format", "json",
                 cwd=dossier, env={"CERTCHECK_NOW": "2026-10-13"})
    if res.code != 0:
        pytest.fail(
            "Le bogue du ticket n'est pas encore corrigé : vpn-01, valide jusqu'au "
            "2031-03-05, ne sort pas en ok (code 0). Ce contrôle juge une version "
            f"corrigée ; corrigez d'abord, il suivra.\n  {res.resume()}",
            pytrace=False,
        )


def test_un_test_reproduit_le_bogue() -> None:
    ref = jouer(str(WORKDIR), str(REFERENCE))
    assert ref.code == 0, (
        "Votre suite échoue sur l'outil de RÉFÉRENCE, qui respecte le contrat : un "
        "test attend autre chose que le comportement juste, ou dépend du jour où il "
        "tourne. Une reproduction doit échouer sur le bogue, et seulement sur lui.\n"
        + ref.resume()
    )
    bogue = jouer(str(WORKDIR), str(BOGUE))
    assert bogue.code != 0 and bogue.echoues > 0, (
        "Votre suite passe sur la version d'ORIGINE, celle du ticket : aucun test ne "
        "reproduit le bogue. Écrivez d'abord le test qui échoue, par exemple sur la "
        "date d'expiration de certs/vpn-01.pem (2031-03-05), puis corrigez.\n"
        + bogue.resume()
    )


def test_le_bogue_est_corrige(outil: Path, tmp_path: Path) -> None:
    for i in range(3):
        graine = tirage().randrange(10**6)
        rnd = tirage(graine)
        hotes = rnd.sample(UN_CHIFFRE, rnd.randint(2, 4)) + rnd.sample(DEUX_CHIFFRES, 2)
        rnd.shuffle(hotes)
        jour = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 1800))
        seuil = rnd.choice([15, 30, 90, 365])
        dossier = tmp_path / f"parc-{i}"
        inventaire = ecrire_inventaire(dossier, hotes)
        res = lancer(outil, "--inventory", str(inventaire), "--days", str(seuil), "--format", "json",
                     cwd=dossier, env={"CERTCHECK_NOW": jour.isoformat()})
        donnees = lire_json_sortie(res)
        lus = {c.get("host"): c for c in donnees["certificates"] if isinstance(c, dict)}
        prevus = attendus(hotes, jour, seuil)
        for hote, (jours, statut) in prevus.items():
            obtenu = lus.get(hote, {})
            assert obtenu.get("status") == statut and obtenu.get("days_left") == jours, (
                f"{hote} (expire le {EXPIRATIONS[hote]}) : status={obtenu.get('status')} "
                f"days_left={obtenu.get('days_left')}, attendu {statut} et {jours} "
                f"(aujourd'hui {jour}, seuil {seuil}, graine {graine}). Comparez ce "
                "qu'openssl lit pour cet hôte avec ce que certcheck en fait.\n  " + res.resume()
            )
            assert obtenu.get("not_after") == EXPIRATIONS[hote].isoformat(), (
                f"{hote} : not_after doit valoir {EXPIRATIONS[hote].isoformat()}."
            )
        attendu = code_attendu([s for _, s in prevus.values()])
        assert res.code == attendu, (
            f"Code {res.code}, attendu {attendu} (graine {graine}) : les statuts sont "
            f"justes, le code de sortie doit les suivre.\n  {res.resume()}"
        )


def test_la_suite_passe_sur_la_version_corrigee(outil: Path, tmp_path: Path) -> None:
    _vpn_01_est_lu(outil, tmp_path)
    depart = jouer(str(FIXTURES), None)
    passage = jouer(str(WORKDIR), None)
    assert passage.code == 0, (
        "Votre suite échoue sur VOTRE version corrigée : soit la correction est "
        "incomplète, soit un test attend l'ancien comportement.\n" + passage.resume()
    )
    assert passage.reussis > depart.reussis, (
        f"{passage.reussis} test(s) vert(s), autant que la suite livrée ({depart.reussis}) : "
        "le test qui reproduit le bogue doit rester dans la suite, sinon le bogue "
        "peut revenir sans que personne le voie.\n" + passage.resume()
    )


def test_aucune_regression(outil: Path, tmp_path: Path) -> None:
    _vpn_01_est_lu(outil, tmp_path / "symptome")
    aide = lancer(outil, "--help", cwd=tmp_path)
    assert aide.code == 0 and "--days" in aide.sortie, f"--help doit toujours sortir en 0.\n  {aide.resume()}"
    res = lancer(outil, "--days", "abc", cwd=tmp_path)
    assert res.code == 2 and not res.sortie.strip(), (
        f"`--days abc` reste un usage incorrect : code 2, rien sur la sortie standard.\n  {res.resume()}"
    )
    # Le seuil reste inclusif, sur un certificat à un chiffre : proxy-01 expire le 2027-02-03.
    dossier = tmp_path / "frontiere"
    inventaire = ecrire_inventaire(dossier, ["proxy-01", "web-01"], separateur="\t")
    jour = EXPIRATIONS["proxy-01"] - timedelta(days=30)
    res = lancer(outil, "--inventory", str(inventaire), "--days", "30", "--format", "json",
                 cwd=dossier, env={"CERTCHECK_NOW": jour.isoformat()})
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"]}
    assert statuts == {"proxy-01": "warning", "web-01": "ok"} and res.code == 1, (
        "proxy-01 expire dans exactement 30 jours avec --days 30 : warning, code 1 "
        f"(seuil inclusif, inventaire séparé par des tabulations).\n  {res.resume()}"
    )
    # Un certificat VRAIMENT illisible reste une erreur, et laisse désormais une trace.
    dossier = tmp_path / "illisible"
    inventaire = ecrire_inventaire(dossier, ["web-01"])
    (dossier / "certs" / "casse.pem").write_text("-----BEGIN CERTIFICATE-----\ntronqué\n", encoding="utf-8")
    with inventaire.open("a", encoding="utf-8") as f:
        f.write("casse-01 certs/casse.pem\n")
    res = lancer(outil, "--inventory", str(inventaire), "--format", "json",
                 cwd=dossier, env={"CERTCHECK_NOW": "2026-10-13"})
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"]}
    assert statuts.get("casse-01") == "error" and res.code == 2, (
        "Un certificat tronqué doit rester en error, code 2. Corriger le découpage ne "
        "doit pas rendre l'outil complaisant : élargir encore le `except`, ou le "
        f"supprimer, change ce verdict.\n  {res.resume()}"
    )
    assert "casse-01" in res.erreurs, (
        "Un certificat illisible ne laisse aucune trace sur la sortie d'erreur : c'est "
        "exactement ce qui a rendu le ticket difficile. Le contrat veut les messages "
        "d'erreur sur la sortie d'erreur ; journalisez l'hôte et la cause dans le "
        f"`except`, et attrapez seulement les exceptions attendues.\n  {res.resume()}"
    )
    # Un certificat absent et un inventaire absent : toujours 2.
    dossier = tmp_path / "troue"
    inventaire = ecrire_inventaire(dossier, ["web-02"], absents=["web-03"])
    res = lancer(outil, "--inventory", str(inventaire), cwd=dossier, env={"CERTCHECK_NOW": "2026-10-13"})
    assert res.code == 2, f"Un certificat absent rend toujours 2.\n  {res.resume()}"
    res = lancer(outil, "--inventory", str(tmp_path / "absent.txt"), cwd=tmp_path)
    assert res.code == 2 and res.erreurs.strip(), (
        f"Un inventaire absent rend toujours 2, avec un message.\n  {res.resume()}"
    )


def _rubriques(texte: str) -> dict[str, str]:
    """Clé de RUBRIQUES -> contenu de la section `## …` dont le titre la contient."""
    sections: dict[str, str] = {}
    courant = None
    for ligne in texte.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", ligne)
        if m:
            titre = m.group(1).lower().replace("\u2019", "'")
            courant = next((cle for cle in RUBRIQUES if re.search(rf"\b{cle}\b", titre)), None)
            if courant is not None:
                sections.setdefault(courant, "")
        elif courant is not None:
            sections[courant] += ligne + "\n"
    return sections


# La cause se dit avec des mots (« deux espaces ») ou se montre (« Mar  5 »).
CAUSE = re.compile(r"espace|split|\S {2,}\d", re.IGNORECASE)


def test_le_journal_de_debogage_dit_ce_qui_s_est_passe() -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    journal = WORKDIR / "DEBUG.md"
    assert journal.is_file(), (
        "DEBUG.md est absent du répertoire de travail. Un débogage se raconte en "
        "quelques lignes : ce que vous avez vu, la cause, la correction. Le "
        "prochain qui tombe sur un symptôme voisin gagnera une heure."
    )
    sections = _rubriques(journal.read_text(encoding="utf-8"))
    manquantes = [titre for cle, titre in RUBRIQUES.items() if cle not in sections]
    assert not manquantes, (
        f"DEBUG.md n'a pas de rubrique `## {manquantes[0]}`. Il en faut trois : "
        "## Ce que j'ai vu, ## La cause, ## La correction."
    )
    vides = [RUBRIQUES[cle] for cle in RUBRIQUES if len(re.sub(r"\s", "", sections[cle])) < 20]
    assert not vides, (
        f"La rubrique `## {vides[0]}` de DEBUG.md est vide ou presque : une phrase "
        "au moins, qui dit ce que vous avez fait ou constaté."
    )
    assert CAUSE.search(sections["cause"]), (
        "La rubrique « La cause » ne dit pas ce qui casse la lecture de la date. "
        "Comparez ce qu'openssl écrit pour vpn-01 et pour web-01 : quelle "
        "différence de caractères, et que fait `split(\" \")` de cette différence ?"
    )
