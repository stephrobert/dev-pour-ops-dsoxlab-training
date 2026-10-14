#!/usr/bin/env python3
"""Fabrique solution/depot.bundle, le dépôt Git livré par la solution de l'épreuve.

Deux commits et une étiquette annotée, à dates et identité fixes : le point de
départ (`fixtures/`), puis la livraison (`fixtures/` recouvert par
`solution/`), étiquetée v1.0.0. `scripts/valider-labs.py` pose ce bundle
par-dessus le répertoire de travail : son arbre doit donc être exactement
celui de `solution/`, ce que le script vérifie en relisant le dépôt.

    python3 scripts/generer_depot_epreuve.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
EPREUVE = RACINE / "labs" / "level-exams" / "outil"
SORTIE = EPREUVE / "solution" / "depot.bundle"
IDENTITE = {"GIT_AUTHOR_NAME": "Equipe exploitation", "GIT_AUTHOR_EMAIL": "exploitation@example.invalid",
            "GIT_COMMITTER_NAME": "Equipe exploitation", "GIT_COMMITTER_EMAIL": "exploitation@example.invalid"}


def git(*args: str, cwd: Path, date: str | None = None) -> str:
    env = {**os.environ, **IDENTITE}
    if date:
        env |= {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    res = subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args],
                         cwd=cwd, capture_output=True, text=True, env=env, check=False)
    if res.returncode != 0:
        sys.exit(f"git {' '.join(args)} : {res.stderr.strip()}")
    return res.stdout


def poser(source: Path, cible: Path) -> list[Path]:
    poses = []
    for fichier in sorted(source.rglob("*")):
        if fichier.is_file() and fichier.name != "depot.bundle" and "__pycache__" not in fichier.parts:
            destination = cible / fichier.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fichier, destination)
            poses.append(fichier.relative_to(source))
    return poses


def main() -> int:
    version = tomllib.loads((EPREUVE / "solution" / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    with tempfile.TemporaryDirectory(prefix="depot-epreuve-") as tmp:
        depot = Path(tmp)
        git("init", "-q", "-b", "main", cwd=depot)
        poser(EPREUVE / "fixtures", depot)
        git("add", "--all", cwd=depot)
        git("commit", "-q", "-m", "Reprise de certcheck : script hérité, contrat et PR n°57 à relire",
            cwd=depot, date="2026-10-12T09:00:00+02:00")
        livres = poser(EPREUVE / "solution", depot)
        git("add", "--all", cwd=depot)
        git("commit", "-q", "-m", f"certcheck {version} : projet Python conforme au contrat, tests et revue de la PR n°57",
            cwd=depot, date="2026-10-13T10:00:00+02:00")
        git("tag", "-a", f"v{version}", "-m", f"certcheck {version}", cwd=depot, date="2026-10-13T10:00:00+02:00")
        # Le script relit ce qu'il a écrit : chaque fichier de solution/ est dans l'arbre étiqueté, octet pour octet.
        for chemin in livres:
            contenu = subprocess.run(["git", "show", f"v{version}:{chemin.as_posix()}"], cwd=depot,
                                     capture_output=True, check=True).stdout
            if contenu != (EPREUVE / "solution" / chemin).read_bytes():
                sys.exit(f"l'étiquette ne porte pas solution/{chemin} à l'identique")
        git("bundle", "create", "-q", str(SORTIE), "main", f"v{version}", cwd=depot)
        print(f"bundle écrit : {SORTIE}")
        print(git("log", "--format=%h %s", "--decorate", cwd=depot), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
