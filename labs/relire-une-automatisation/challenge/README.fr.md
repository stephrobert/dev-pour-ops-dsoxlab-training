# Challenge : relire la pull request n°42

5 tâches, 100 points, 40 minutes.

Le répertoire `challenge/work` contient le projet sur `main`, la description
de la PR (`pr/DESCRIPTION.md`) et son diff (`pr/0042.diff`). Votre revue va
dans `revue.yaml`, dont l'en-tête documente la forme et la liste fermée des
catégories. Un commentaire désigne un défaut s'il porte le bon fichier, la
bonne catégorie, et une ligne à deux lignes au plus de la ligne fautive,
comptée dans le fichier **après** `git apply`.

### Tâche 1 : le secret exposé et le TLS désactivé (20 pts)

Deux commentaires signalent l'URL du webhook, qui porte un jeton, écrite sur
une sortie (`secret-expose`), et la vérification du certificat du chat coupée
(`tls-desactive`).

### Tâche 2 : l'erreur avalée et l'effet de bord non borné (20 pts)

Deux commentaires signalent l'exception attrapée puis ignorée
(`erreur-avalee`) et la suppression récursive dont la cible n'est pas
validée (`effet-de-bord-non-borne`).

### Tâche 3 : la dépendance non épinglée et le test absent (20 pts)

Deux commentaires signalent la dépendance déclarée sans version exacte
(`dependance-non-epinglee`) et la nouvelle fonction qu'aucun test n'exerce
(`test-absent`, sur sa ligne `def` à trois lignes près, ou sur le fichier de
tests).

### Tâche 4 : une revue actionnable (20 pts)

Chaque commentaire a un `commentaire` et une `proposition` d'au moins 25
caractères, toutes les catégories viennent de la liste fermée, au plus deux
commentaires ne désignent aucun défaut réel, et `verdict` vaut
`demander-des-changements`.

### Tâche 5 : les défauts mécaniques refusés au commit (20 pts)

`.pre-commit-config.yaml`, à la racine du projet, déclare un détecteur de
secrets (gitleaks, detect-secrets ou detect-private-key) et le linter ruff,
chacun depuis son dépôt officiel, et chaque `rev` est une empreinte de commit
complète de 40 caractères. Le contrôle lit le fichier, il ne lance pas
pre-commit.
