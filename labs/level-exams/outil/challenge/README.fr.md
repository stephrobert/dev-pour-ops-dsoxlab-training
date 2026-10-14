# Défi : reprendre un outil d'exploitation

5 tâches, 100 points, 60 minutes. Seuil de réussite : 70 points.

Aucun indice n'est proposé : l'épreuve mesure ce que vous savez déjà faire.
Rien ne lit votre code : chaque contrôle lance vos fichiers comme le ferait
le collègue qui reprendra l'outil après vous, et les vérifications du
contrat sont **cachées**, jouées sur des inventaires, des seuils et des
dates tirés au hasard.

## Ce que vous recevez

- `certcheck.sh`, le script hérité, à lire seulement : plus rien ne le lance ;
- le squelette du projet Python qui le remplace : `pyproject.toml` (la
  commande `certcheck` dans `[project.scripts]`, le `[build-system]`, et
  pytest 9.1.1 dans le groupe de développement `[dependency-groups]`),
  `uv.lock` qui verrouille ces versions, le paquet `src/certcheck/` dont les
  fonctions à écrire lèvent `NotImplementedError`, et `bin/certcheck`, qui
  lance déjà ce paquet par `uv run --project` ;
- `CONTRAT.md`, ce que l'outil doit faire, vu de l'extérieur ;
- `inventaire.txt` et `certs/`, un petit parc pour essayer ;
- `pr/`, la pull request n°57 d'Inès : sa description, son diff, et le
  projet `pr/main/` sur lequel il s'applique ;
- `revue.yaml`, à remplir.

## Ce que vous livrez, à la racine du répertoire de travail

Le squelette fournit la forme du projet ; la notation porte sur ce que vous
en faites. Une ligne du tableau marquée « fourni » reste à garder juste
jusqu'à la livraison, une ligne marquée « à écrire » est entièrement à vous.

| Fichier | Rôle |
|---|---|
| `pyproject.toml` | fourni : la version livrée est à y porter, la commande `certcheck` à garder dans `[project.scripts]` |
| `src/certcheck/` | fourni, à compléter : le paquet Python de l'outil, conforme à `CONTRAT.md` |
| `bin/certcheck` | fourni : le lanceur, qui exécute votre paquet par `uv run --project` |
| `tests/` | à écrire : vos tests pytest, qui lancent l'exécutable désigné par `CERTCHECK_BIN` (défaut : `bin/certcheck`) |
| `uv.lock` | fourni : les dépendances de développement épinglées (`==`), pytest au moins ; `uv run` le tient à jour |
| `CHANGELOG.md` | à écrire : une section `## [X.Y.Z]` pour la version livrée |
| `revue.yaml` | à remplir : votre revue de la PR n°57, dans la forme décrite par son en-tête |

Le répertoire de travail devient un dépôt Git, et la version livrée porte une
étiquette `vX.Y.Z` (annotée ou non).

### Tâche 1 : l'outil respecte le contrat (20 pts)

Interface (`--help`, `--version`, usage incorrect), codes de sortie 0, 1 et
2, sortie JSON juste au jour près et seuil inclusif, seuil réglable par
`CERTCHECK_DAYS` avec priorité de l'option, inventaires aux séparateurs mêlés
(espaces et tabulations), certificats dont le jour d'expiration s'écrit sur
un chiffre, et certificat absent rendu en `error` avec le code 2.

### Tâche 2 : vos tests attrapent le bogue hérité (20 pts)

`uv run pytest tests` est joué trois fois, dans une copie du répertoire de
travail, en changeant seulement `CERTCHECK_BIN` : il passe contre votre
outil, avec au moins trois tests réussis, passe contre l'outil de référence
du formateur, et **échoue** contre une variante qui reproduit le bogue du
script hérité (un certificat absent compté `warning` à 0 jour, code 1).

### Tâche 3 : le projet s'installe (20 pts)

`pyproject.toml` déclare la commande `certcheck`, le code vit dans un paquet
sous `src/`, et les dépendances de développement sont épinglées. Le projet
est installé (`pip install .`) dans un environnement neuf : la commande
`certcheck --version` y affiche la version de `pyproject.toml`, et l'outil
installé passe un contrôle de fumée. Le squelette s'installe déjà : ce sont
`--version` et le contrôle de fumée, qui passent par votre code, qui font la
note, et la version affichée doit suivre celle de `pyproject.toml` quand vous
la changez.

### Tâche 4 : la version est notée et étiquetée (20 pts)

La plus haute étiquette `vX.Y.Z` désigne un commit dont le `CHANGELOG.md`
porte la section `## [X.Y.Z]` et dont le `pyproject.toml` porte la version
`X.Y.Z`.

### Tâche 5 : la revue de la PR n°57 (20 pts)

La PR porte quatre défauts, tous de catégories de la liste fermée de
`revue.yaml`. Au moins trois sont désignés par un commentaire au bon fichier
(chemin depuis `pr/main`), à la bonne catégorie, et à deux lignes près dans
le fichier **après** application du diff ; chaque commentaire et chaque
proposition font au moins 25 caractères ; au plus deux commentaires ne
désignent aucun défaut réel ; `verdict` vaut `demander-des-changements`.

Pour faire noter : `dsoxlab check level-exams-outil`.
