# Développer pour les Ops : les labs vérifiables

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/dev-pour-ops-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/dev-pour-ops-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/dev-pour-ops-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/dev-pour-ops-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Les labs de la formation
[Développer pour les Ops](https://blog.stephane-robert.info/docs/developper/)
du blog, joués avec [dsoxlab](https://github.com/stephrobert/dsoxlab).

## Ce que c'est

**Dix labs, un outil hérité.** La formation apprend à un Ops à développer comme
un développeur, en Python, et le fil rouge est `certcheck`, un contrôle
d'expiration de certificats TLS que quelqu'un d'autre a écrit avant vous. Vous
lisez son code, le structurez en vrai projet Python (src layout,
`pyproject.toml`, uv) qui respecte un contrat, appelez une API, le testez avec
pytest, déboguez un certificat qu'il ne sait pas lire, relisez une pull request
qui porte quatre défauts, verrouillez les dépendances et livrez une version
installable. L'épreuve de fin reprend un outil d'exploitation de bout en bout.

Le code hérité est le sujet. L'essentiel de ce qu'un Ops écrit est du code que
quelqu'un d'autre relira, et l'essentiel de ce qu'il corrige est du code que
quelqu'un d'autre a écrit. Un lab qui part d'un fichier vide n'enseigne que la
moitié facile.

## Prérequis

- **`mise`** : il installe `uv` et Python aux versions épinglées dans
  [`mise.toml`](./mise.toml), sans curl d'archive ni gestionnaire de paquets
  système.
- **`git`** : un lab relit une pull request, et les labs travaillent dans de
  vrais dépôts.
- **`openssl`**, celui du système : `certcheck` lit de vrais certificats.
- **`dsoxlab`**, le moteur, installé en outil autonome (voir plus bas).
- **Un accès réseau sortant** : quelques labs installent des paquets depuis
  PyPI.

**Aucune VM, aucun `dsoxlab provision`.** Ce catalogue ne déclare aucun bloc
`infra:` : tous ses labs sont `runtime: shell` et tournent sur votre poste,
dans leur propre projet `uv`.

## Installation

`dsoxlab` est publié sur [PyPI](https://pypi.org/project/dsoxlab/).
Installez-le en outil autonome, pour qu'il reste hors de ce dépôt :

```bash
# 1. La CLI dsoxlab (outil externe, hors de ce dépôt)
uv tool install dsoxlab

# 2. Ce catalogue de labs
git clone https://github.com/stephrobert/dev-pour-ops-dsoxlab-training.git
cd dev-pour-ops-dsoxlab-training

# 3. Les outils, aux versions épinglées
mise install

# 4. Vérifier que le contrat est valide
dsoxlab validate-structure
```

### Votre premier lab, en cinq minutes

```bash
export LAB_HOME=$PWD
dsoxlab list-labs                    # les dix labs, dans l'ordre pédagogique
dsoxlab run       lire-du-code       # poser l'état de départ
dsoxlab challenge lire-du-code       # lire la mission
# ... vous travaillez dans challenge/work ...
dsoxlab check     lire-du-code       # lancer les tests, enregistrer le score
```

C'est `run` qui prépare `challenge/work` et copie les fixtures que le lab
déclare. Un `check` joué sur un lab jamais démarré ne mesure rien, et le dit
au lieu d'enregistrer un 0.

### Garder à jour

```bash
uv tool upgrade dsoxlab        # le moteur, publié sur PyPI
git -C <ce dépôt> pull         # le catalogue
```

Le moteur et le catalogue avancent indépendamment : un nouveau `dsoxlab` ne
demande jamais de recloner les labs, et de nouveaux labs ne demandent jamais de
mettre l'outil à jour, tant que la version du contrat correspond. `dsoxlab
doctor` dit ce dont ce dépôt a besoin, et ce dont il n'a pas besoin.

## Comment ça marche

### Le contrat déclaratif, à deux niveaux

Le catalogue est décrit par des données, pas par du code, et c'est ce qui garde
le moteur `dsoxlab` indépendant du domaine :

- **`meta.yml`** à la racine déclare l'identité du dépôt et l'**ordre** des
  sections affichées par `list-labs` ;
- **`lab.yaml`** par lab déclare ses `skills`, son `level`, son `runtime`
  (type, fixtures, services), ses `distros`, son `doc_url` et un bloc
  `validation`. Un `lab.fr.yaml` surcharge `title` et `description` en
  français, et rien d'autre.

`dsoxlab validate-structure` contrôle tout le contrat : `meta.yml` bien formé,
chaque lab référencé présent avec un `lab.yaml` valide, chaque fichier de test
et de fixture déclaré réellement là, et chaque lien relatif d'un README qui
mène quelque part.

### Le cycle de vie d'un lab

```bash
dsoxlab list-labs              # parcourir le catalogue
dsoxlab show      <id>         # métadonnées et état d'un lab
dsoxlab run       <id>         # poser l'état de départ
dsoxlab challenge <id>         # lire la mission, sans pas-à-pas
dsoxlab hint      <id>         # révéler un indice (déduit du score)
dsoxlab check     <id>         # lancer les tests, calculer et enregistrer le score
dsoxlab clean     <id>         # retirer le répertoire de travail
dsoxlab progress               # avancement par section, score moyen
```

### Les runtimes

| Runtime | Ce que le lab demande |
|---|---|
| `shell` | un terminal, `uv`, Python, `git` et l'`openssl` du système. Votre outil tourne dans **son propre** projet `uv`, avec ses dépendances. |

Deux labs travaillent contre une **forge factice locale**, livrée sous forme de
bundle git et non de service vivant : le lab qui appelle une API y ouvre un
ticket, et le lab de relecture y lit une pull request. Aucun compte, aucun
jeton, aucun réseau.

### Le modèle de validation

La validation **prouve ce qu'un appelant observe, elle ne fait pas confiance à
l'apprenant**. Chaque lab porte des tests `pytest` sous `challenge/tests/` qui
lisent la sortie de l'outil, son code de retour, les requêtes reçues par la
forge factice et les fichiers laissés dans le dépôt : jamais ce qu'un fichier
source contient.

Et un lab est prouvé **dans les deux sens** : les tests doivent échouer avant
le travail et passer après. Un test vert avant le travail n'est pas un test,
c'est une hypothèse sur le setup. `scripts/valider-labs.py` joue ce cycle
entier sur chaque lab et écrit son verdict dans
[`validation-labs.json`](./validation-labs.json), qui est versionné : un lab
livré sans verdict ne prouve rien.

Les solutions de référence vivent sous `labs/<lab>/solution/`, **en clair** :
les labs enchaînés les recopient comme point de départ du suivant, donc les
fichiers doivent être lisibles. En lire une, c'est vous gâcher ce lab.

### Score, indices, avancement

`check` enregistre un score (tests réussis sur total, moins le coût des indices
révélés). Les indices sont **en base64** dans `challenge/hints.yaml`, pour qu'on
n'y accède pas en ouvrant le fichier, et leur coût croît avec leur précision.
L'historique vit dans une base SQLite **locale à ce dépôt**.

Une exécution qui n'a rien mesuré n'est ni une réussite ni un échec : si tous
les tests collectés skippent, `check` n'enregistre aucune note et dit pourquoi.
Un 0 accuserait le lab de ce qui manque au poste.

## Catalogue

<!-- LABS:START -->
### Le fil rouge : lire, modifier, tester et faire relire un petit outil

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `lire-du-code` | Lire et modifier un petit script Python : le certcheck hérité | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/lire-du-code/) |
| `script-en-outil` | Comprendre un outil Python, puis le modifier : certcheck et son contrat | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/script-en-outil/) |
| `dependances-reproductibles` | Dépendances : certcheck s'installe aussi ailleurs | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/dependances-reproductibles/) |
| `tester-une-automatisation` | Se servir des tests : un test rouge, lu, corrigé, et un test de plus | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/tester-une-automatisation/) |
| `deboguer` | Déboguer pas à pas : le certificat que certcheck ne sait pas lire | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/deboguer/) |
| `relire-une-automatisation` | Relire une pull request : quatre défauts dans la n°42 de certcheck | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/relire-une-automatisation/) |

### Aller plus loin

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `appeler-une-api` | Appeler une API avec requests : certcheck ouvre son ticket | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/api-rest/) |
| `livrer-un-outil` | Livrer un outil : certcheck 1.0.0, versionné et installable | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) |
| `level-exams-outil` | Défi : reprendre un outil d'exploitation | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/livrer-un-outil/) |

### Épreuve de niveau

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `level-exams-intervenir` | Épreuve : intervenir sur un petit outil d'exploitation | o1 | - | shell | [guide](https://dev.stephane-robert.info/docs/developper/pratiques/epreuve-intervenir/) |

_10 labs, table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contribuer

Lisez [`CONTRIBUTING.fr.md`](./CONTRIBUTING.fr.md). En bref : un lab est prouvé
**dans les deux sens** avant d'être fusionné, `dsoxlab validate-structure` est
vert, et l'énoncé existe en anglais et en français.

Tout ce qui s'affiche est bilingue. Un document traduit d'un seul côté est
signalé par le validateur, et non laissé à la bonne volonté.

## Licence

Voir [`LICENSE`](./LICENSE).
