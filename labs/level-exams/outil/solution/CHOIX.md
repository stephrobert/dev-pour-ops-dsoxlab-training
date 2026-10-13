# Choix du langage de certcheck

Ce fichier n'est pas noté par `dsoxlab check` : il relève de
l'auto-évaluation, sur la grille ci-dessous.

## Le langage retenu

Python 3.12 ou plus récent, bibliothèque standard seule, plus `openssl` du
système. La suite de tests utilise pytest 9.1.1, verrouillé dans `uv.lock`.

## Pourquoi lui, pour cet outil

Le contrat exige un appel HTTP avec délai maximal et reprise, un JSON sur la
sortie standard et un calcul de dates exact. En Bash, chacun de ces points
passe par un outil externe (`curl`, `jq`, `date`) dont les options varient
d'une distribution à l'autre, et l'erreur avalée du script hérité est
justement née d'une substitution de commande qui échouait en silence. Python
fournit `urllib`, `json` et `datetime` sans aucune dépendance, et l'équipe
d'exploitation lit déjà du Python. Go aurait donné un binaire unique, mais
personne dans l'équipe ne le maintient aujourd'hui.

## Ce que ce choix coûte

Le serveur d'exploitation doit avoir Python 3.12 ou plus récent : c'est le
cas de la distribution en place, mais une machine plus ancienne exigerait une
installation par uv. Les tests demandent uv pour installer pytest.

## Ce qui ferait changer d'avis

Une diffusion sur des machines sans Python, ou un besoin de concurrence pour
interroger des centaines de forges : Go deviendrait alors le meilleur choix.

## Grille d'auto-évaluation

| Critère | Note |
|---|---|
| Le choix part des besoins de l'outil, pas d'une préférence | 2 |
| Au moins un besoin du contrat est comparé dans deux langages | 2 |
| Le coût du choix est nommé (dépendance, installation, compétences de l'équipe) | 2 |
| Le choix tient compte de qui maintiendra l'outil | 2 |
| Ce qui ferait changer d'avis est écrit | 2 |
