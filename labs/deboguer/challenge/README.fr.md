# Challenge : le certificat que certcheck ne sait pas lire

5 tâches, 100 points, 45 minutes.

Le ticket est dans `TICKET.md`. Votre suite se lance par `uv run pytest`,
l'outil par `bin/certcheck`, et le journal de débogage s'écrit dans
`DEBUG.md`, à la racine du projet.

### Tâche 1 : un test reproduit le bogue (20 pts)

Votre suite échoue sur la version d'origine de `certcheck.py`, celle du
ticket, et passe sur la version de référence : au moins un test attrape le
bogue, et seulement lui.

### Tâche 2 : le bogue est corrigé (20 pts)

`bin/certcheck` lit les certificats dont le jour d'expiration n'a qu'un
chiffre : statuts, `days_left`, `not_after` et code de sortie justes, sur
des parcs, des dates et des seuils tirés au hasard.

### Tâche 3 : la suite passe sur la version corrigée (20 pts)

`uv run pytest` est vert sur votre version, et la suite compte plus de tests
que celle livrée : le test de reproduction est resté.

### Tâche 4 : aucune régression (20 pts)

Le reste du contrat tient toujours : usage incorrect en 2, seuil inclusif,
inventaire à tabulations, certificat absent ou inventaire absent en 2. Un
certificat vraiment illisible reste en `error`, code 2, et laisse un message
qui nomme l'hôte sur la sortie d'erreur.

### Tâche 5 : le journal de débogage (20 pts)

`DEBUG.md` porte les sections `## Reproduire`, `## Réduire`, `## Observer`
et `## Corriger`, chacune rédigée, et la section Réduire cite la chaîne
minimale qui déclenche le bogue.
