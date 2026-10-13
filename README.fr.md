# Développer pour les Ops : les labs vérifiables

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/dev-pour-ops-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/dev-pour-ops-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/dev-pour-ops-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/dev-pour-ops-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Les labs de la formation
[Développer pour les Ops](https://blog.stephane-robert.info/docs/developper/)
du blog, joués avec [dsoxlab](https://github.com/stephrobert/dsoxlab). La
formation apprend à un Ops à développer comme un développeur, en Python. Un
seul fil rouge, `certcheck`, un contrôle d'expiration de certificats TLS :
vous lisez le code d'un paquet Python hérité, structurez un projet Python
(src layout, `pyproject.toml`, uv) qui respecte un contrat, appelez une API,
testez avec pytest, déboguez, relisez un changement, verrouillez les
dépendances et livrez une version installable. L'épreuve de fin reprend un
outil d'exploitation de bout en bout.

Chaque lab a un point de départ, une vérification qui juge ce qu'un appelant
observe (sorties, codes de sortie, requêtes reçues par une forge factice,
fichiers du dépôt), une solution de référence, et a été éprouvé dans les deux
sens : 0 avant le travail, 100 après. Le verdict de chaque lab est dans
`validation-labs.json`.

```bash
mise install                                     # uv et Python
export LAB_HOME=$PWD
dsoxlab list-labs
dsoxlab run   lire-du-code
dsoxlab check lire-du-code
```

Aucune VM : l'outil tourne sur votre poste, dans son propre projet uv, avec
openssl et Git du système. Quelques labs téléchargent des paquets depuis PyPI.

<!-- LABS:START -->
### Le fil rouge : du code hérité à l'outil livré

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `lire-du-code` | Lire le code d'une application Python : le paquet certcheck hérité | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/lire-du-code/) |
| `script-en-outil` | Structurer un projet Python en outil : certcheck respecte son contrat | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/script-en-outil/) |
| `appeler-une-api` | Appeler une API sans fragilité : certcheck publie son ticket | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/api-rest/) |
| `tester-une-automatisation` | Premiers tests : pytest attrape deux vrais bogues | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) |
| `deboguer` | Déboguer pas à pas : le certificat que certcheck ne sait pas lire | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/deboguer/) |
| `relire-une-automatisation` | Relire une automatisation : la pull request n°42 de certcheck | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/relire-une-automatisation/) |
| `dependances-reproductibles` | Dépendances reproductibles : certcheck s'installe à l'identique ailleurs | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/dependances-reproductibles/) |
| `livrer-un-outil` | Livrer un outil interne : certcheck 1.0.0, étiqueté et installable | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) |

### Épreuve de niveau

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `level-exams-outil` | Épreuve : reprendre un outil d'exploitation | o1 | - | shell | [guide](https://blog.stephane-robert.info/docs/developper/parcours/) |

_9 labs, table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->
