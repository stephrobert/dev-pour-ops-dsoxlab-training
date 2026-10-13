# Épreuve : reprendre un outil d'exploitation

5 tâches, 100 points, 120 minutes. Seuil de réussite : 70 points.

Aucun indice n'est proposé : l'épreuve mesure ce que vous savez déjà faire.
Le langage est libre, Bash, Python ou Go. Rien ne lit votre code : chaque
contrôle lance vos fichiers comme le ferait le collègue qui reprendra
l'outil après vous, et les vérifications du contrat sont **cachées**,
jouées sur des inventaires, des seuils et des dates tirés au hasard.

## Ce que vous recevez

- `certcheck.sh`, le script hérité, et `bin/certcheck`, qui le lance ;
- `CONTRAT.md`, ce que l'outil doit faire, vu de l'extérieur ;
- `inventaire.txt` et `certs/`, un petit parc pour essayer ;
- `pr/`, la pull request n°57 d'Inès : sa description, son diff, et le
  projet `pr/main/` sur lequel il s'applique ;
- `revue.yaml` et `CHOIX.md`, à remplir.

## Ce que vous livrez, à la racine du répertoire de travail

| Fichier | Rôle |
|---|---|
| `bin/certcheck` | le point d'entrée de votre outil, conforme à `CONTRAT.md` |
| `test.sh` | lance VOTRE suite de tests contre l'exécutable désigné par `CERTCHECK_BIN` (défaut : `bin/certcheck`), sort en 0 si tout passe |
| verrou des versions | `uv.lock` (Python), `go.sum` ou `go.mod` avec `toolchain goX.Y.Z` (Go), ou `mise.toml` aux versions exactes X.Y.Z (Bash) |
| `CHANGELOG.md` | une section `## [X.Y.Z]` pour la version livrée |
| `Makefile` | `make install PREFIX=<dossier>` installe `<dossier>/bin/certcheck` |
| `revue.yaml` | votre revue de la PR n°57, dans la forme décrite par son en-tête |
| `CHOIX.md` | la justification du langage retenu |

Le répertoire de travail devient un dépôt Git, et la version livrée porte une
**étiquette annotée** `vX.Y.Z`.

### Tâche 1 : l'outil respecte le contrat (20 pts)

Interface (`--help`, `--version`, usage incorrect), codes de sortie 0, 1 et
2, sortie JSON juste au jour près et seuil inclusif, configuration par
l'environnement avec priorité de l'option, inventaires aux séparateurs mêlés
(espaces et tabulations) et aux fins de ligne CRLF, certificats dont le jour
d'expiration s'écrit sur un chiffre, et certificat absent rendu en `error`
avec le code 2.

### Tâche 2 : la publication est sûre, idempotente et bornée (20 pts)

Avec `--publish` face à une forge factice : le jeton part dans l'en-tête et
jamais dans l'URL ni sur une sortie, une seconde exécution n'ouvre pas de
doublon, le ticket existant est retrouvé en deuxième page, deux réponses 503
sont reprises, et face à une forge qui accepte la connexion sans jamais
répondre, l'outil rend la main seul, en code 3, en moins de 60 secondes.

### Tâche 3 : votre suite de tests attrape le défaut hérité (20 pts)

`./test.sh` est joué trois fois, dans une copie du répertoire de travail, en
changeant seulement `CERTCHECK_BIN` : il passe contre votre outil, passe
contre l'outil de référence du formateur, et **échoue** contre une variante
qui reproduit le défaut du script hérité (un certificat absent compté
`warning` à 0 jour, code 1).

### Tâche 4 : la version se livre depuis son étiquette (20 pts)

La plus haute étiquette annotée `vX.Y.Z` porte un `CHANGELOG.md` avec sa
section `## [X.Y.Z]` et un verrou des versions. Elle est clonée dans un
dossier temporaire, `make install PREFIX=<tmp>` y est lancé, puis le clone est
supprimé : `<tmp>/bin/certcheck --version` affiche `certcheck X.Y.Z` et
l'outil installé passe un contrôle de fumée.

### Tâche 5 : la revue de la PR n°57 (20 pts)

La PR porte cinq défauts, tous de catégories de la liste fermée de
`revue.yaml`. Au moins quatre sont désignés par un commentaire au bon
fichier (chemin depuis `pr/main`), à la bonne catégorie, et à deux lignes
près dans le fichier **après** application du diff ; chaque commentaire et
chaque proposition font au moins 25 caractères ; au plus deux commentaires
ne désignent aucun défaut réel ; `verdict` vaut `demander-des-changements`.

## Ce qui n'est pas noté automatiquement

`CHOIX.md` relève de l'**auto-évaluation** : la grille qu'il contient est
publiée, cotez-vous dessus. Un choix de langage se juge à ses arguments, pas
par un test.

Pour faire noter : `dsoxlab check level-exams-outil`.
