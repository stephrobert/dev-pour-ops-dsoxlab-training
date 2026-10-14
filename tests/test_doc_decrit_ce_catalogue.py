"""Méta-test du dépôt : la doc doit décrire CE catalogue, pas celui d'où il vient.

Ce dépôt est repris de `github-actions-training`, et la reprise a laissé des
noms qui n'existent pas ici. Le 2026-10-14, `CONTRIBUTING.fr.md` affirmait
encore, en trois lignes :

    Seul le dernier lab, `automatisation-dans-la-ci`, demande Docker : act y
    joue le workflow dans l'image du runner épinglée par digest dans `.actrc`.

    Les labs de la section `automatisation` construisent **un seul outil**,
    `security_check.py`, version après version.

Quatre affirmations, quatre fausses : ce lab n'existe pas, cette section n'est
pas dans `meta.yml`, cet outil n'est pas celui du fil rouge (c'est `certcheck`),
et ni `.actrc` ni Docker n'existent nulle part dans le dépôt.

CE QUE CELA COÛTE, ET POURQUOI UN TEST

Une doc fausse n'est pas un défaut de style : elle fait prendre des décisions
fausses avec assurance. Sur ce dépôt précisément, l'audit de conformité qui
précédait la première publication a conclu qu'il fallait chiffrer les dix
solutions, comme les catalogues Linux, Terraform et Ansible le font — alors
que le même `CONTRIBUTING.fr.md` explique trois paragraphes plus bas que ce
catalogue les livre en clair **à dessein**, chaque solution étant le point de
départ du lab suivant. Le chiffrement aurait cassé le fil rouge. C'est le texte
faux qui a orienté la lecture, et seule une vérification au disque l'a arrêtée.

Un test est ce qui empêche la dérive de revenir, parce qu'il relit le disque à
chaque fois et que personne ne relit `CONTRIBUTING.md` à chaque fois.

CE QUI EST CONTRÔLÉ, ET CE QUI NE PEUT PAS L'ÊTRE

On ne contrôle que le mécaniquement vérifiable : les identifiants de labs et de
sections cités entre accents graves existent-ils ? Le reste du texte est du
jugement.

`CHANGELOG.md` et `CHANGELOG.fr.md` sont HORS périmètre, et ce n'est pas une
commodité : un journal parle du passé par nature, et l'entrée qui corrige une
dérive doit pouvoir nommer le nom qu'elle retire. Un contrôle qui le lui
interdirait rendrait le journal illisible, et c'est le genre de contrôle qu'on
apprend à contourner — donc à ignorer.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
LABS = REPO / "labs"

#: Les documents qui décrivent le catalogue au présent. Le CHANGELOG en est
#: absent (voir la docstring), et tout ce qui est généré ou copié dans un
#: répertoire de travail aussi : on ne contrôle que ce qui est écrit à la main.
DOCUMENTS = (
    "README.md",
    "README.fr.md",
    "CONTRIBUTING.md",
    "CONTRIBUTING.fr.md",
)

#: Un identifiant de lab de ce catalogue : minuscules et tirets, au moins deux
#: tirets. Le seuil n'est pas esthétique — il sépare les identifiants
#: (`lire-du-code`, `appeler-une-api`) des options et noms de fichiers qu'une
#: doc technique cite à longueur de ligne (`--fail-on`, `ruff-format`,
#: `pre-commit`), qui n'en portent qu'un. Mesuré sur ce dépôt : sans ce seuil,
#: le contrôle crie sur une trentaine de termes parfaitement légitimes, et un
#: contrôle qui crie à tort est un contrôle qu'on désactive.
MOTIF_IDENTIFIANT = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+){2,})`")

#: Les termes qui passent le motif sans être des identifiants de labs. Chacun
#: est présent dans la doc du dépôt, vérifié à la main : ce sont des commandes,
#: des chemins et des noms d'outils, pas des labs.
HORS_SUJET = frozenset({
    "dev-pour-ops-dsoxlab-training",
    "linux-dsoxlab-training",
    "terraform-dsoxlab-training",
    "ansible-dsoxlab-training",
    "devsecops-dsoxlab-training",
    "github-actions-training",
    "ruff-format-check",
    "validate-structure",
    "persist-credentials",
    "known-first-party",
    "estimated-time",
    "vault-password-file",
    "exam-passing-score",
    "snapshot-required",
    "lab-type",
    "doc-url",
})


def identifiants_des_labs() -> set[str]:
    """Les identifiants réellement déclarés, lus des `lab.yaml`.

    On lit l'`id` ET le chemin depuis `labs/`, parce que les deux sont cités :
    `meta.yml` range `level-exams/outil` par son chemin, et la CLI l'appelle
    `level-exams-outil` par son `id`.
    """
    connus: set[str] = set()
    for fichier in sorted(LABS.rglob("lab.yaml")):
        definition = yaml.safe_load(fichier.read_text(encoding="utf-8")) or {}
        if definition.get("id"):
            connus.add(str(definition["id"]))
        relatif = fichier.parent.relative_to(LABS)
        connus.add(str(relatif))
        connus.add(str(relatif).replace("/", "-"))
    return connus


def sections_declarees() -> set[str]:
    meta = yaml.safe_load((REPO / "meta.yml").read_text(encoding="utf-8")) or {}
    return {str(s["id"]) for s in (meta.get("sections") or []) if s.get("id")}


@pytest.mark.parametrize("nom", DOCUMENTS)
def test_aucun_lab_inexistant_n_est_cite(nom: str) -> None:
    """Un identifiant de lab cité dans la doc doit exister sur le disque."""
    document = REPO / nom
    if not document.is_file():
        pytest.skip(f"{nom} absent")

    connus = identifiants_des_labs() | sections_declarees() | HORS_SUJET
    fautifs: list[str] = []
    for numero, ligne in enumerate(document.read_text(encoding="utf-8").splitlines(), 1):
        for trouve in MOTIF_IDENTIFIANT.findall(ligne):
            if trouve not in connus:
                fautifs.append(f"{nom}:{numero} « {trouve} »")

    assert not fautifs, (
        "la doc cite des identifiants qui n'existent pas dans ce catalogue :\n  "
        + "\n  ".join(fautifs)
        + "\n\nSoit le nom est faux (dérive héritée d'un autre catalogue), soit "
        "c'est un terme légitime à ajouter à HORS_SUJET après vérification."
    )


@pytest.mark.parametrize("nom", DOCUMENTS)
def test_aucune_section_inexistante_n_est_citee(nom: str) -> None:
    """« section `X` » doit nommer une section de `meta.yml`.

    C'est la phrase qui désigne le sujet du catalogue — « les labs de la
    section `automatisation` construisent… ». La laisser fausse, c'est décrire
    un autre dépôt.

    Les sections d'un fichier de configuration portent le même mot et sont
    exclues : `scenario.fr.md` de `dependances-reproductibles` parle à juste
    titre de « une section `dependencies` » dans `pyproject.toml`.
    """
    document = REPO / nom
    if not document.is_file():
        pytest.skip(f"{nom} absent")

    sections = sections_declarees()
    fautives: list[str] = []
    for numero, ligne in enumerate(document.read_text(encoding="utf-8").splitlines(), 1):
        if "pyproject" in ligne or "toml" in ligne.lower():
            continue
        for trouve in re.findall(r"section `([a-z0-9-]+)`", ligne):
            if trouve not in sections:
                fautives.append(f"{nom}:{numero} « section `{trouve}` »")

    assert not fautives, (
        "la doc cite des sections absentes de meta.yml "
        f"({', '.join(sorted(sections))}) :\n  " + "\n  ".join(fautives)
    )


def test_l_outil_du_fil_rouge_est_celui_que_le_depot_livre() -> None:
    """Le nom de l'outil construit par le fil rouge doit être le vrai.

    `CONTRIBUTING` annonçait `security_check.py`, nom de l'outil du catalogue
    GitHub Actions d'où ce dépôt est repris. Le fil rouge d'ici livre
    `certcheck`, et c'est le paquet qu'on trouve sous `src/` dans les solutions.

    Le contrôle lit donc le disque plutôt qu'une constante : le jour où le fil
    rouge changera d'outil, il suivra tout seul.
    """
    paquets = {
        chemin.name
        for chemin in REPO.rglob("src/*")
        if chemin.is_dir() and (chemin / "__init__.py").is_file()
    }
    assert paquets, "aucun paquet Python sous un src/ : le fil rouge ne livre rien ?"

    for nom in ("CONTRIBUTING.md", "CONTRIBUTING.fr.md"):
        document = REPO / nom
        if not document.is_file():
            continue
        texte = document.read_text(encoding="utf-8")
        assert any(f"`{paquet}`" in texte for paquet in paquets), (
            f"{nom} ne nomme aucun des paquets réellement livrés "
            f"({', '.join(sorted(paquets))}) : il décrit probablement encore "
            "l'outil du catalogue d'origine."
        )
