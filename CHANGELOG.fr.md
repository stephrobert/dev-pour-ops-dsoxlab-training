# Journal des modifications

**Langue :** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Toutes les modifications notables de ce projet sont consignées dans ce fichier.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/).

Ce dépôt est un **catalogue de contenu**, pas une bibliothèque : il n'est pas
versionné et ne publie aucune release. Les entrées ci-dessous datent les
modifications du catalogue, et l'unité qui compte est le lab.

## [Non publié] - 2026-10-14

### Modifié

- **Recentrage en initiation** (formation Développer pour les Ops, validé le
  2026-10-13) : `lire-du-code` fait lire puis modifier un petit script unique ;
  `script-en-outil` fait se repérer dans le projet Python et combler deux
  écarts au contrat, au lieu de l'écrire ; `tester-une-automatisation` part
  d'une suite rouge à lire et corriger, puis d'un test à ajouter ; `deboguer`
  fournit le test de reproduction en commentaire ; `relire-une-automatisation`
  exige aussi `ruff format --check`.
- **Sections** : le fil rouge garde six labs ; `appeler-une-api`,
  `livrer-un-outil` et l'ancienne épreuve, devenue le défi
  `level-exams-outil`, passent dans la section facultative `approfondir`.

### Ajouté

- **L'épreuve `level-exams-intervenir`** : un dépôt de cinq commits dont un
  fautif, un journal de CI rouge, une correction limitée, tests, qualité et
  étapes de CI rejoués. Générée par `scripts/generer_depot_intervenir.py`
  depuis `donnees/intervenir/`.

### Retiré

- `scripts/generer_historique.sh` et `scripts/generer_historique_paquet.py`,
  qui fabriquaient l'historique du paquet de l'ancien `lire-du-code`.

## [0.1.0] - 2026-10-09

### Ajouté

- **La section `automatisation`**, sept labs qui construisent un seul outil,
  `security_check.py`, pour la piste Automatisation de la formation Python du
  blog (2026-10-02). Chaque lab part de la solution du précédent :
  - `automatisation-lire-un-rapport` lit un export JSON de findings et les
    compte par sévérité, avec le code 2 sur une entrée inexploitable ;
  - `automatisation-interroger-osv` interroge l'API OSV avec un délai
    maximal, vérifié contre une API factice locale qui enregistre chaque
    requête ;
  - `automatisation-rapport-trivy` lit un vrai rapport Trivy 0.74.0 :
    26 occurrences, 22 vulnérabilités distinctes, une cible sans clé
    `Vulnerabilities` ;
  - `automatisation-code-de-sortie` passe sous Click et ajoute `--fail-on` :
    0, 1 ou 2, les codes qu'un pipeline exploite ;
  - `automatisation-tester-son-outil` note la suite pytest de l'apprenant sur
    quatre mutants de l'outil de référence ;
  - `automatisation-dans-la-ci` fait de l'outil une porte dans GitHub
    Actions : les tests d'abord, puis le seuil CRITICAL, joué avec act. Le
    seul lab qui demande Docker ;
  - `automatisation-lire-un-sbom` croise un vrai SBOM CycloneDX (syft
    1.51.1) avec OSV : chaque vulnérabilité connue devient un finding, avec
    la sévérité de son avis GitHub (MODERATE en MEDIUM).
- La table anglaise des README signale les guides qui n'existent qu'en
  français.
- Les labs éprouvés dans les deux sens par `scripts/valider-labs.py` :
  0 avant le travail, 100 après la solution, 0 à nouveau après `clean` et
  `run`. Verdicts dans `validation-labs.json`.

[Non publié]: https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/stephrobert/dev-pour-ops-dsoxlab-training/releases/tag/v0.1.0
