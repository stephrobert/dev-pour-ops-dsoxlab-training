# Challenge : relire la pull request n°42

5 tâches, 100 points, 25 minutes.

Le répertoire de travail contient le projet sur `main`, la description de la
PR (`pr/DESCRIPTION.md`) et son diff (`pr/0042.diff`). Votre revue va dans
`revue.yaml`, dont l'en-tête documente la forme et les quatre catégories. Un
commentaire désigne un défaut s'il porte le bon fichier, la bonne catégorie,
et une ligne à deux lignes au plus de la ligne fautive, comptée dans le
fichier **après** `git apply`.

### Tâche 1 : au moins trois défauts trouvés (20 pts)

Sur les quatre défauts de la PR (erreur avalée, secret affiché, chemin
dangereux, test absent), au moins trois sont désignés par un commentaire.

### Tâche 2 : chaque commentaire propose une correction (20 pts)

Chaque commentaire a un `commentaire` et une `proposition` d'au moins 25
caractères, sa catégorie vient de la liste, et au plus deux commentaires ne
désignent aucun défaut réel.

### Tâche 3 : un verdict (20 pts)

`verdict` vaut `demander-des-changements`.

### Tâche 4 : une configuration ruff versionnée (20 pts)

Le projet porte une configuration ruff : une section `[tool.ruff]` dans
`pyproject.toml`, ou un fichier `ruff.toml`.

### Tâche 5 : ruff check passe sur le code de base (20 pts)

`uv run ruff check .` ne signale plus rien, et l'import inutilisé du code de
base a été retiré du code, pas masqué par la configuration.
