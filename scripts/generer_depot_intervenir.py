#!/usr/bin/env python3
"""Fabrique le point de départ et la solution de l'épreuve `level-exams-intervenir`.

Le projet juste vit dans `donnees/intervenir/`. Ce script en tire un dépôt Git
de cinq commits, à dates et identités fixes, dont le quatrième introduit le
défaut de l'épreuve (seuil devenu exclusif) et un import inutile que le linter
refuse. Il écrit :

- `fixtures/depot.bundle` : l'historique que l'apprenant clone ;
- `fixtures/ci/run-12.log` : le journal du run de CI sur le dernier commit,
  reconstitué en jouant RÉELLEMENT les étapes `run:` de `ci.yml` sur cet arbre,
  dans l'ordre, jusqu'à la première en échec ;
- `solution/certcheck/` : l'arbre du dernier commit, défaut corrigé.

Il relit ce qu'il a écrit : le bundle se clone, son dernier arbre échoue au
linter et aux tests, et l'arbre de la solution passe toutes les étapes.

    python3 scripts/generer_depot_intervenir.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "donnees" / "intervenir"
EPREUVE = RACINE / "labs" / "level-exams" / "intervenir"
BUNDLE = EPREUVE / "fixtures" / "depot.bundle"
JOURNAL = EPREUVE / "fixtures" / "ci" / "run-12.log"
SOLUTION = EPREUVE / "solution" / "certcheck"
EXCLUS = (".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "uv.lock.bak")

AUTEURS = {
    "julien": ("Julien Marchal", "julien@exploitation.example.invalid"),
    "karim": ("Karim Benali", "karim@exploitation.example.invalid"),
    "ines": ("Ines Ferreira", "ines@exploitation.example.invalid"),
}

JUSTE = "    if jours <= seuil:\n"
FAUX = "    if jours < seuil:\n"
IMPORTS_JUSTES = "import os\nimport subprocess\n"
IMPORTS_FAUX = "import os\nimport subprocess\nimport sys\n"


def git(*args: str, cwd: Path, auteur: str | None = None, date: str | None = None) -> str:
    env = dict(os.environ)
    if auteur:
        nom, mel = AUTEURS[auteur]
        env |= {"GIT_AUTHOR_NAME": nom, "GIT_AUTHOR_EMAIL": mel, "GIT_COMMITTER_NAME": nom, "GIT_COMMITTER_EMAIL": mel}
    if date:
        env |= {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    res = subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
                         cwd=cwd, capture_output=True, text=True, env=env, check=False)
    if res.returncode != 0:
        sys.exit(f"git {' '.join(args)} : {res.stderr.strip()}")
    return res.stdout


def commit(depot: Path, message: str, auteur: str, date: str) -> str:
    git("add", "-A", cwd=depot)
    git("commit", "-q", "-m", message, cwd=depot, auteur=auteur, date=date)
    return git("rev-parse", "HEAD", cwd=depot).strip()


def remplacer(fichier: Path, avant: str, apres: str) -> None:
    texte = fichier.read_text(encoding="utf-8")
    if avant not in texte:
        sys.exit(f"{fichier} : motif introuvable {avant!r}")
    fichier.write_text(texte.replace(avant, apres, 1), encoding="utf-8")


def etapes(depot: Path) -> list[tuple[str, str | None]]:
    doc = yaml.safe_load((depot / ".forgejo" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
    return [(e["name"], e.get("run")) for e in doc["jobs"]["integrer"]["steps"]]


def jouer_ci(depot: Path) -> tuple[list[str], int | None]:
    """Joue les étapes run: dans une copie ; rend les lignes du journal et l'indice de l'étape en échec."""
    lignes: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ci-") as tmp:
        copie = Path(tmp) / "certcheck"
        shutil.copytree(depot, copie, ignore=shutil.ignore_patterns(".git", *EXCLUS))
        env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
        echec = None
        for i, (nom, run) in enumerate(etapes(depot)):
            if echec is not None:
                lignes.append(f"== Étape « {nom} » : non exécutée")
                continue
            if run is None:
                lignes.append(f"== Étape « {nom} » : réussie")
                continue
            res = subprocess.run(["bash", "-e", "-c", run], cwd=copie, capture_output=True, text=True,
                                 env=env, check=False, timeout=600)
            sortie = [f"  {x}" for x in (res.stdout + res.stderr).rstrip().splitlines()]
            if res.returncode == 0:
                lignes.append(f"== Étape « {nom} » : réussie")
            else:
                echec = i
                lignes.append(f"== Étape « {nom} » : échec, code de sortie {res.returncode}")
                lignes.extend(f"  $ {x}" for x in run.strip().splitlines()[:1])
                lignes.extend(sortie[-25:])
    return lignes, echec


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="intervenir-") as tmp:
        depot = Path(tmp) / "certcheck"
        shutil.copytree(SOURCE, depot, ignore=shutil.ignore_patterns(*EXCLUS))
        git("init", "-q", cwd=depot)
        commit(depot, "certcheck 0.5.0 : paquet, contrat, tests et intégration continue",
               "julien", "2026-09-01T09:12:00+02:00")

        (depot / "CHANGELOG.md").write_text(
            "# Journal des changements\n\n## [0.5.0] - 2026-09-01\n\n"
            "- Première version du paquet Python, qui remplace le script Bash.\n", encoding="utf-8")
        commit(depot, "Journal des changements de la 0.5.0", "julien", "2026-09-03T16:40:00+02:00")

        remplacer(depot / "README.md", "Signale les certificats TLS d'un parc qui arrivent à expiration.",
                  "Signale les certificats TLS d'un parc qui arrivent à expiration. cron le\nlance chaque nuit "
                  "sur le parc de production.")
        commit(depot, "README : l'outil tourne chaque nuit", "karim", "2026-09-17T11:05:00+02:00")

        remplacer(depot / "src" / "certcheck" / "certificats.py", JUSTE, FAUX)
        remplacer(depot / "src" / "certcheck" / "certificats.py", IMPORTS_JUSTES, IMPORTS_FAUX)
        fautif = commit(depot, "Décision : simplifier le calcul du statut", "ines", "2026-10-06T18:22:00+02:00")

        remplacer(depot / "README.md", "chaque push sur `main` et à chaque demande de fusion.",
                  "chaque push sur `main` et à chaque demande de fusion. Le journal\ndu dernier run "
                  "est rangé à côté du dépôt, dans `ci/`.")
        tete = commit(depot, "README : où lire le résultat de la CI", "karim", "2026-10-08T10:30:00+02:00")

        BUNDLE.parent.mkdir(parents=True, exist_ok=True)
        # HEAD en plus de main : sans lui, un `git clone` sur un poste sans
        # init.defaultBranch laisse un répertoire vide (remote HEAD absent).
        git("bundle", "create", "-q", str(BUNDLE), "HEAD", "main", cwd=depot)

        lignes, echec = jouer_ci(depot)
        noms = [n for n, _ in etapes(depot)]
        if echec is None or noms[echec] != "Qualité":
            sys.exit(f"le run du dernier commit devait échouer à l'étape Qualité : {lignes}")
        JOURNAL.parent.mkdir(parents=True, exist_ok=True)
        JOURNAL.write_text(
            f"Run n°12 de la pipeline ci, job integrer, déclenché par un push sur main\n"
            f"Commit {tete[:7]} « README : où lire le résultat de la CI »\n\n"
            + "\n".join(lignes) + "\n\nJob failed\n", encoding="utf-8")

        # La solution : le dernier arbre, défaut corrigé (le test qui le prouve existe déjà).
        remplacer(depot / "src" / "certcheck" / "certificats.py", FAUX, JUSTE)
        remplacer(depot / "src" / "certcheck" / "certificats.py", IMPORTS_FAUX, IMPORTS_JUSTES)
        if SOLUTION.exists():
            shutil.rmtree(SOLUTION)
        shutil.copytree(depot, SOLUTION, ignore=shutil.ignore_patterns(".git", *EXCLUS))
        lignes, echec = jouer_ci(SOLUTION)
        if echec is not None:
            sys.exit("la solution devait passer toutes les étapes :\n" + "\n".join(lignes))

    # Relire ce qui a été écrit : le bundle se clone et porte le commit fautif.
    with tempfile.TemporaryDirectory(prefix="relire-") as tmp:
        clone = Path(tmp) / "c"
        git("clone", "-q", str(BUNDLE), str(clone), cwd=Path(tmp))
        trouve = git("log", "--format=%H", "-S", "import sys", "--", "src/certcheck/certificats.py", cwd=clone).split()
        if trouve != [fautif]:
            sys.exit(f"le bundle ne désigne pas le commit fautif {fautif} : {trouve}")
    print(f"bundle : {BUNDLE.relative_to(RACINE)} (commit fautif {fautif[:7]}, tête {tete[:7]})")
    print(f"journal : {JOURNAL.relative_to(RACINE)}")
    print(f"solution : {SOLUTION.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
