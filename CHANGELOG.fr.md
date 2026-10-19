# Journal des modifications

**Langue :** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Toutes les modifications notables de ce projet sont consignées dans ce fichier.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/).

Ce dépôt est un **catalogue de contenu**, pas une bibliothèque : il ne publie
ni paquet PyPI ni roue. Un tag `vX.Y.Z` publie en revanche une release GitHub —
une archive du catalogue, son empreinte SHA-256, une provenance SLSA niveau 3
et une signature cosign (voir `RELEASING.fr.md`). L'unité qui compte reste le
lab.

## [0.2.0] - 2026-10-17

### Modifié

- **Le validateur lit le contrat, plus l'encadré du terminal.**
  `scripts/valider-labs.py` lisait le score dans ce que `dsoxlab check`
  *affiche*. Cet encadré est de l'interface : il a changé en dsoxlab 0.4.0 et
  la regex a cessé de trouver quoi que ce soit. Il lit désormais
  `check --json`, qui porte un `schema`, et cette lecture vit dans
  `scripts/verdict_check.py`, **identique dans les douze catalogues**.

- **Trois verdicts, pas deux.** Une exécution dont tous les tests collectés ont
  skippé n'a rien mesuré : elle est **SKIP**, ni verte ni rouge, et reste à
  mesurer. La peindre en rouge accuserait le lab de ce qui manque au poste.
  `--check` sort donc en `10` dans ce cas, contre `1` pour un ROUGE, à l'image
  de `dsoxlab doctor --strict` où 9 se répare et 10 se remesure.

- **Le README prend la structure de référence** commune aux douze catalogues :
  quatorze sections, dans les deux langues. Sept d'entre elles décrivent
  dsoxlab et non le sujet, et sont donc identiques partout.

### Exige

- **dsoxlab 0.4.1 ou plus récent**, qui a introduit le champ `status` de
  `check --json`. Sans lui, le validateur refuse de conclure plutôt que de
  deviner.

### En propre

- les dix `doc_url` pointent vers le site public et non la préproduction.

## [0.1.0] - 2026-10-14

Première version du catalogue : dix labs, tous en `runtime: shell`, éprouvés
dans les deux sens.

### Ajouté

- **Le fil rouge, six labs qui construisent un seul outil, `certcheck`**
  (formation Développer pour les Ops). Chaque lab part de la solution de
  référence du précédent, livrée en clair pour cette raison :
  - `lire-du-code` — lire et modifier un petit script Python : le `certcheck`
    hérité ;
  - `script-en-outil` — comprendre un outil Python, puis le modifier :
    `certcheck` et son contrat ;
  - `dependances-reproductibles` — dépendances : `certcheck` s'installe aussi
    ailleurs ;
  - `tester-une-automatisation` — se servir des tests : un test rouge, lu,
    corrigé, et un test de plus ;
  - `deboguer` — déboguer pas à pas : le certificat que `certcheck` ne sait pas
    lire ;
  - `relire-une-automatisation` — relire une pull request : quatre défauts dans
    la n°42 de `certcheck`.
- **La section facultative `approfondir`**, trois labs autonomes qui se jouent
  après le fil rouge :
  - `appeler-une-api` — appeler une API avec `requests` : `certcheck` ouvre son
    ticket ;
  - `livrer-un-outil` — livrer un outil : `certcheck` 1.0.0, versionné et
    installable ;
  - `level-exams-outil` — défi : reprendre un outil d'exploitation.
- **L'épreuve de niveau `level-exams-intervenir`** : un dépôt de cinq commits
  dont un fautif, un journal de CI rouge, une correction limitée, tests,
  qualité et étapes de CI rejoués. Générée par
  `scripts/generer_depot_intervenir.py` depuis `donnees/intervenir/`.
- La table anglaise des README signale les guides qui n'existent qu'en
  français.
- **Les dix labs éprouvés dans les deux sens** par `scripts/valider-labs.py` :
  0 avant le travail, le barème complet après la solution, 0 à nouveau après
  `clean` et `run`, et le poste rendu intact. Verdicts dans
  `validation-labs.json`.

### Corrigé

- `scripts/valider-labs.py` ne photographiait pas le lab mais **le poste
  entier** : son `docker ps -a` sans filtre voyait les conteneurs de tous les
  chantiers de la machine, et deux labs sont passés au rouge pour des
  conteneurs qu'ils n'avaient jamais touchés. La photographie se limite
  désormais à ce que dsoxlab peut créer — le préfixe `dsoxlab-` et les
  `spawns` déclarés par les labs, lus du catalogue pour qu'un futur service
  soit surveillé sans qu'on y repense.
- Les `doc_url` et les liens de guides pointent sur `dev.stephane-robert.info`,
  où les guides de cette formation sont publiés. Les liens vers des pages déjà
  en production sur `www.stephane-robert.info` sont inchangés.
- Dérives documentaires héritées de `github-actions-training`, dont ce dépôt
  est repris : un lab `automatisation-dans-la-ci` qui n'existe pas, un outil
  `security_check.py` qui n'est pas celui du fil rouge, une section
  `automatisation` absente de `meta.yml`, un `.actrc` et un besoin de Docker
  qui n'existent nulle part ici, et un exemple `--lab` nommant un lab inconnu.

[0.1.0]: https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/releases/tag/v0.1.0
