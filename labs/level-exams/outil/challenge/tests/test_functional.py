"""Épreuve : reprendre un outil d'exploitation. Cinq contrôles, vingt points chacun.

## Une épreuve notée sur le contrat, dans n'importe quel langage

L'apprenant livre certcheck en Bash, en Python ou en Go. Rien ici ne lit son
code : les contrôles lancent `bin/certcheck`, sa suite `./test.sh`, son
`Makefile` et son dépôt Git comme le ferait un collègue qui reprend l'outil,
et ne jugent que ce qui s'observe.

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
import shutil
import time
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import (
    EXPIRATIONS,
    REFERENCE,
    TITRE_TICKET,
    Forge,
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
    serveur_muet,
    tirage,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "level-exams-outil"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
OPTIONS = ("--inventory", "--days", "--format", "--publish", "--dry-run", "--verbose", "--version")
# Les certificats dont le jour d'expiration s'écrit sur un chiffre : openssl
# l'affiche avec deux espaces (« Mar  5 12:00:00 2031 GMT »).
JOUR_A_UN_CHIFFRE = sorted(h for h, d in EXPIRATIONS.items() if d.day < 10)
DELAI_MAXIMAL = 60  # secondes, pour rendre la main face à une forge muette
SEMVER = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


@pytest.fixture(scope="module")
def outil() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return exiger_executable(WORKDIR)


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


def _inventaire_brut(dossier: Path, hotes: list[str], rnd, *, crlf: bool) -> Path:
    """Un inventaire comme on en reçoit : espaces et tabulations mêlés, commentaires, CRLF."""
    inventaire = ecrire_inventaire(dossier, hotes)
    lignes = ["# inventaire exporté depuis l'outil de parc", ""]
    for hote in hotes:
        separateur = rnd.choice([" ", "\t", "   ", " \t "])
        lignes.append(f"{hote}{separateur}certs/{hote}.pem")
    fin = "\r\n" if crlf else "\n"
    inventaire.write_bytes((fin.join(lignes) + fin).encode())
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

    # Trois parcs tirés au hasard, dont un aux fins de ligne CRLF.
    graine = tirage().randrange(10**6)
    rnd = tirage(graine)
    for i in range(3):
        hotes, jour, seuil = _scenario(rnd)
        dossier = tmp_path / f"parc-{i}"
        crlf = i == 0
        inventaire = _inventaire_brut(dossier, hotes, rnd, crlf=crlf)
        attendu = attendus(hotes, jour, seuil)
        contexte = (f"graine {graine}, parc {i}, aujourd'hui {jour}, seuil {seuil}, "
                    f"fins de ligne {'CRLF' if crlf else 'LF'}")
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
                "les séparateurs (espaces ET tabulations), le retour chariot d'un fichier "
                "CRLF, et les jours à un chiffre, qu'openssl écrit avec deux espaces."
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

    # La configuration par l'environnement, et l'option qui l'emporte.
    inventaire = ecrire_inventaire(tmp_path / "conf", ["api-01", "web-01"], separateur="\t")
    jour = EXPIRATIONS["api-01"] - timedelta(days=20)
    env = {"CERTCHECK_NOW": jour.isoformat(), "CERTCHECK_INVENTORY": str(inventaire)}
    ailleurs = tmp_path / "ailleurs"
    ailleurs.mkdir()
    res = lancer(outil, "--format", "json", cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "10"})
    statuts = {c.get("host"): c.get("status") for c in lire_json_sortie(res)["certificates"]}
    assert res.code == 0 and statuts == {"api-01": "ok", "web-01": "ok"}, (
        "CERTCHECK_INVENTORY désigne l'inventaire (lancé depuis un autre dossier) et "
        f"CERTCHECK_DAYS=10 laisse api-01, à 20 jours, en ok.\n  {res.resume()}"
    )
    res = lancer(outil, "--format", "json", "--days", "30", cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "10"})
    assert res.code == 1, (
        f"--days 30 l'emporte sur CERTCHECK_DAYS=10 : api-01 passe en warning, code 1.\n  {res.resume()}"
    )
    res = lancer(outil, cwd=ailleurs, env={**env, "CERTCHECK_DAYS": "dix"})
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


# --- Tâche 2 : la publication ---------------------------------------------------


def _publier(outil: Path, dossier: Path, forge: Forge, *, timeout: int = 120):
    inventaire = ecrire_inventaire(dossier, ["web-02", "web-01", "vpn-01"])  # web-02 a expiré
    return lancer(outil, "--inventory", str(inventaire), "--publish", "--verbose", cwd=dossier,
                  env={"CERTCHECK_NOW": "2026-06-01", **forge.env()}, timeout=timeout)


def _remettre(forge: Forge, *, pannes: int = 0) -> None:
    forge.tickets.clear()
    forge.requetes.clear()
    forge.pannes = pannes


def test_la_publication_est_sure_idempotente_et_bornee(outil: Path, tmp_path: Path, forge: Forge) -> None:
    # Un ticket, le jeton dans l'en-tête, nulle part ailleurs.
    forge.ajouter_tickets(3)
    res = _publier(outil, tmp_path / "a", forge)
    creations = forge.creations()
    assert res.code == 1 and len(creations) == 1, (
        f"Un certificat expiré et --publish : un ticket ouvert ({len(creations)} reçu(s)), et "
        f"le code reste celui du contrôle, 1.\n  {res.resume()}"
    )
    assert (creations[0]["corps"] or {}).get("title") == TITRE_TICKET, (
        f"Le ticket s'intitule exactement « {TITRE_TICKET} » : c'est par ce titre que "
        "l'outil le retrouve la nuit suivante."
    )
    fuites = [f"{r['methode']} {r['chemin']}?{r['query']}" for r in forge.requetes
              if forge.jeton in r["chemin"] or forge.jeton in r["query"]]
    assert not fuites, (
        f"Le jeton figure dans l'URL de {fuites} : une URL finit dans les journaux du "
        "serveur et des mandataires. Il part dans l'en-tête Authorization."
    )
    sans_entete = [r["methode"] for r in forge.requetes
                   if r["auth"] not in (f"token {forge.jeton}", f"Bearer {forge.jeton}")]
    assert not sans_entete, (
        f"{len(sans_entete)} requête(s) sans `Authorization: token <jeton>` : la forge les refuse."
    )
    assert forge.jeton not in res.sortie + res.erreurs, (
        "Le jeton apparaît sur une sortie, même avec --verbose : la sortie d'un cron "
        "finit dans un courriel. Aucun secret n'est jamais écrit."
    )
    # Idempotence : la nuit suivante n'ouvre rien de plus.
    res = _publier(outil, tmp_path / "a", forge)
    assert len(forge.creations()) == 1, (
        f"Deuxième passage : {len(forge.creations())} ticket(s) en tout. Le ticket déjà "
        f"ouvert doit être retrouvé, pas doublé.\n  {res.resume()}"
    )

    # Pagination : le ticket existant est en deuxième page.
    _remettre(forge)
    forge.ajouter_tickets(70, cible_en=55)
    res = _publier(outil, tmp_path / "b", forge)
    assert not forge.creations(), (
        "70 tickets ouverts, celui de certcheck en 56e position : il est en deuxième page "
        "(la forge rend 30 tickets par page par défaut, 50 au plus avec limit). Un outil "
        "qui ne lit que la première page en ouvre un doublon chaque nuit.\n  " + res.resume()
    )

    # Reprise : deux 503 avant que la forge réponde.
    _remettre(forge, pannes=2)
    res = _publier(outil, tmp_path / "c", forge)
    assert res.code == 1 and len(forge.creations()) == 1, (
        "La forge rend 503 deux fois, puis répond : une erreur passagère se reprend (trois "
        f"essais au total), et le ticket s'ouvre. {len(forge.creations())} ticket(s) reçu(s).\n"
        f"  {res.resume()}"
    )

    # Délai maximal : une forge qui accepte la connexion et ne répond jamais.
    with serveur_muet() as url:
        muette = Forge(url=url)
        debut = time.monotonic()
        res = _publier(outil, tmp_path / "d", muette, timeout=DELAI_MAXIMAL + 30)
        duree = time.monotonic() - debut
    assert res.code == 3 and duree < DELAI_MAXIMAL, (
        f"Face à une forge qui ne répond jamais, l'outil a rendu la main en {duree:.0f} s "
        f"avec le code {res.code}. Attendu : moins de {DELAI_MAXIMAL} s et le code 3 "
        "(publication échouée). Chaque requête porte un délai maximal, et les essais "
        f"sont comptés.\n  {res.resume()}"
    )


# --- Tâche 3 : la suite de tests de l'apprenant ---------------------------------


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


def test_la_suite_de_l_apprenant_attrape_l_erreur_avalee(tmp_path: Path) -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    suite = WORKDIR / "test.sh"
    if not suite.is_file():
        pytest.fail(
            "test.sh est absent de la racine du dépôt. Il lance VOTRE suite de tests contre "
            "l'exécutable désigné par CERTCHECK_BIN (bin/certcheck par défaut), et sort en 0 "
            "si tout passe.",
            pytrace=False,
        )
    if not suite.stat().st_mode & 0o100:
        pytest.fail("test.sh n'est pas exécutable : `chmod +x test.sh`.", pytrace=False)

    reference = _lanceur(tmp_path, "reference", REFERENCE)
    boguee = _lanceur(tmp_path, "boguee", _variante_boguee(tmp_path))
    with copie_temporaire(WORKDIR) as copie:
        def jouer(binaire: Path):
            return executer(["./test.sh"], cwd=copie, env={"CERTCHECK_BIN": str(binaire)}, timeout=300)

        def resume(res) -> str:
            return f"code {res.returncode}\n{(res.stdout + res.stderr).strip()[-1500:]}"

        sien = jouer(copie / "bin" / "certcheck")
        assert sien.returncode == 0, (
            "./test.sh échoue contre VOTRE outil (CERTCHECK_BIN=bin/certcheck) : une suite "
            "livrée passe sur l'outil livré.\n" + resume(sien)
        )
        ref = jouer(reference)
        assert ref.returncode == 0, (
            "./test.sh échoue contre l'outil de RÉFÉRENCE, qui respecte CONTRAT.md : un test "
            "attend autre chose que le contrat (une version exacte, un format de texte "
            "précis, la date du jour réelle au lieu de CERTCHECK_NOW), ou la suite ignore "
            "CERTCHECK_BIN.\n" + resume(ref)
        )
        bug = jouer(boguee)
    assert bug.returncode != 0, (
        "./test.sh passe contre une variante qui reproduit le défaut du script hérité : un "
        "certificat absent y est compté « warning, 0 jour », code 1, au lieu de error et "
        "code 2. Le défaut qui a motivé la reprise n'est couvert par aucun test, ou la "
        "suite teste toujours bin/certcheck au lieu de CERTCHECK_BIN.\n" + resume(bug)
    )


# --- Tâche 4 : la livraison -----------------------------------------------------


def _etiquette_annotee() -> tuple[str, str]:
    if not (WORKDIR / ".git").exists():
        pytest.fail(
            "Le répertoire de travail n'est pas un dépôt Git : `git init`, des commits, puis "
            "une étiquette annotée `git tag -a vX.Y.Z -m ...`.",
            pytrace=False,
        )
    res = git("for-each-ref", "--format=%(objecttype) %(refname:strip=2)", "refs/tags", cwd=WORKDIR)
    annotees, legeres = [], []
    for ligne in res.stdout.splitlines():
        genre, _, nom = ligne.partition(" ")
        if SEMVER.match(nom):
            (annotees if genre == "tag" else legeres).append(nom)
    if not annotees:
        detail = f" Étiquette(s) légère(s) trouvée(s) : {legeres}." if legeres else ""
        pytest.fail(
            "Aucune étiquette annotée de la forme vX.Y.Z. Une étiquette légère n'est qu'un "
            "pointeur : elle n'a ni auteur, ni date, ni message, et `git describe` l'ignore. "
            f"`git tag -a v1.0.0 -m \"certcheck 1.0.0\"`.{detail}",
            pytrace=False,
        )
    nom = max(annotees, key=lambda n: tuple(int(x) for x in SEMVER.match(n).groups()))
    return nom, nom[1:]


def _verrou_present(fichiers: set[str], lire) -> bool:
    if "uv.lock" in fichiers or "go.sum" in fichiers:
        return True
    if "go.mod" in fichiers and re.search(r"^toolchain go\d+\.\d+\.\d+\s*$", lire("go.mod"), re.MULTILINE):
        return True
    if "mise.toml" in fichiers:
        outils = re.search(r"^\[tools\](.*?)(?=^\[|\Z)", lire("mise.toml"), re.MULTILINE | re.DOTALL)
        valeurs = re.findall(r'^\s*[\w.:/-]+\s*=\s*"([^"]*)"', outils.group(1), re.MULTILINE) if outils else []
        return bool(valeurs) and all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in valeurs)
    return False


def test_la_version_se_livre_depuis_son_etiquette(tmp_path: Path) -> None:
    exiger_workdir(WORKDIR, LAB_ID)
    exiger_outil("make")
    etiquette, version = _etiquette_annotee()

    fichiers = set(git("ls-tree", "-r", "--name-only", etiquette, cwd=WORKDIR).stdout.split())

    def lire(nom: str) -> str:
        return git("show", f"{etiquette}:{nom}", cwd=WORKDIR).stdout

    assert "CHANGELOG.md" in fichiers and re.search(
        rf"^## \[{re.escape(version)}\]", lire("CHANGELOG.md"), re.MULTILINE), (
        f"Le CHANGELOG.md de l'étiquette {etiquette} doit porter une section `## [{version}]` : "
        "c'est ce que lit celui qui se demande ce qui a changé avant de mettre à jour."
    )
    assert _verrou_present(fichiers, lire), (
        f"L'étiquette {etiquette} ne porte aucun verrou des versions : uv.lock (Python), "
        "go.sum ou un go.mod avec `toolchain goX.Y.Z` (Go), ou un mise.toml dont chaque "
        "outil est à une version exacte X.Y.Z (Bash). Sans lui, la même étiquette ne "
        "reconstruit pas le même outil dans six mois."
    )

    clone, prefixe = tmp_path / "clone", tmp_path / "prefixe"
    res = git("clone", "--quiet", "--branch", etiquette, str(WORKDIR), str(clone), cwd=tmp_path)
    assert res.returncode == 0, f"`git clone --branch {etiquette}` a échoué : {res.stderr.strip()}"
    assert (clone / "Makefile").is_file(), f"Le clone de {etiquette} n'a pas de Makefile à sa racine."
    res = executer(["make", "install", f"PREFIX={prefixe}"], cwd=clone, timeout=300)
    installe = prefixe / "bin" / "certcheck"
    assert res.returncode == 0 and installe.is_file(), (
        f"`make install PREFIX={prefixe}`, depuis un clone de {etiquette}, doit installer "
        f"{installe}. Code {res.returncode}.\n{(res.stdout + res.stderr).strip()[-1200:]}"
    )
    shutil.rmtree(clone)  # l'outil installé ne dépend pas du clone qui l'a construit
    assert installe.exists(), (
        f"{installe} ne mène plus à rien une fois le clone supprimé : c'est un lien vers le "
        "clone, pas une installation. `make install` copie dans PREFIX tout ce dont l'outil "
        "a besoin pour tourner."
    )

    res = lancer(installe, "--version", cwd=tmp_path)
    assert res.sortie.strip() == f"certcheck {version}" and res.code == 0, (
        f"L'outil installé depuis {etiquette} doit afficher « certcheck {version} » : la "
        "version annoncée et l'étiquette disent la même chose. (Le clone a été supprimé "
        f"après l'installation.)\n  {res.resume()}"
    )
    rnd = tirage()
    hotes = rnd.sample(sorted(EXPIRATIONS), 4)
    jour, seuil = date(2026, 6, 1) + timedelta(days=rnd.randint(0, 900)), 30
    inventaire = ecrire_inventaire(tmp_path / "fumee", hotes)
    res = lancer(installe, "--inventory", str(inventaire), "--format", "json", cwd=tmp_path,
                 env={"CERTCHECK_NOW": jour.isoformat()})
    lus = {c.get("host"): (c.get("days_left"), c.get("status"))
           for c in lire_json_sortie(res)["certificates"] if isinstance(c, dict)}
    attendu = attendus(hotes, jour, seuil)
    assert lus == attendu and res.code == code_attendu([s for _, s in attendu.values()]), (
        f"Contrôle de fumée de l'outil installé (aujourd'hui {jour}, seuil {seuil}) : lu {lus}, "
        f"attendu {attendu}.\n  {res.resume()}"
    )


# --- Tâche 5 : la revue de la pull request n°57 ---------------------------------

CATEGORIES = {
    "erreur-avalee", "secret-expose", "tls-desactive", "effet-de-bord-non-borne",
    "dependance-non-epinglee", "test-absent", "non-idempotent", "injection-de-commande",
}
LONGUEUR_MINIMALE = 25
FAUX_POSITIFS_TOLERES = 2
DEFAUTS_A_TROUVER = 4


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
        "secret-expose": [
            _zone("secret-expose", "certcheck.py", code, 'log.debug("%s %s, en-têtes : %s", methode, url, entetes)'),
            _zone("secret-expose", "certcheck.py", code, "logging.DEBUG if args.verbose"),
        ],
        "tls-desactive": [
            _zone("tls-desactive", "certcheck.py", code, "ssl._create_unverified_context()"),
            _zone("tls-desactive", "certcheck.py", code, "context=CONTEXTE_TLS"),
        ],
        "non-idempotent": [_zone("non-idempotent", "certcheck.py", code,
                                 "def ticket_ouvert(", "for ticket in tickets if isinstance(tickets, list)")],
    }


def _chemin(valeur: object) -> str:
    chemin = str(valeur or "").strip().replace("\\", "/")
    for prefixe in ("./", "a/", "b/", "pr/main/"):
        chemin = chemin.removeprefix(prefixe)
    return chemin


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
            str(element.get("categorie") or "").strip().lower(),
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
        f"{len(trouves)} défaut(s) sur 5 désignés ({trouves}) ; il en faut au moins "
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
