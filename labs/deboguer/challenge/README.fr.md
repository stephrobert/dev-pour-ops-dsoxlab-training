# Challenge : le certificat que certcheck ne sait pas lire

5 tâches, 100 points, 25 minutes.

Le ticket est dans `TICKET.md`. Votre suite se lance par `uv run pytest`,
l'outil par `bin/certcheck`, et le journal de débogage s'écrit dans
`DEBUG.md`, à la racine du projet.

### Tâche 1 : un test reproduit le bogue (20 pts)

Votre suite échoue sur la version d'origine de
`src/certcheck/certificats.py`, celle du ticket, et passe sur la version de
référence : au moins un test attrape le bogue, et seulement lui.

### Tâche 2 : le bogue est corrigé (20 pts)

`bin/certcheck` lit les certificats dont le jour d'expiration n'a qu'un
chiffre : statuts, `days_left`, `not_after` et code de sortie justes, sur
des parcs, des dates et des seuils tirés au hasard.

### Tâche 3 : le test reste, et passe après (20 pts)

`uv run pytest` est vert sur votre version corrigée, et la suite compte plus
de tests que celle livrée : le test de reproduction est resté.

### Tâche 4 : aucune régression (20 pts)

Le reste du contrat tient toujours (seuil inclusif, usage incorrect et
certificat absent en 2). Un certificat vraiment illisible reste en `error`,
code 2, et laisse un message qui nomme l'hôte sur la sortie d'erreur.

### Tâche 5 : le journal de débogage (20 pts)

`DEBUG.md` porte trois rubriques rédigées : `## Ce que j'ai vu`,
`## La cause` et `## La correction`. La cause dit ce qui casse la lecture de
la date.
