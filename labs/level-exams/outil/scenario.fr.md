# La reprise

## Situation

Julien, qui avait écrit `certcheck.sh`, a quitté l'équipe, et vous reprenez
l'outil. Le script tourne chaque nuit depuis le cron du serveur
d'exploitation. Il sort toujours en 0, et il a compté pendant des semaines un
certificat introuvable comme expirant « dans 0 jour » : personne ne s'en est
aperçu. L'équipe a écrit ce qu'elle attend de l'outil dans `CONTRAT.md`.

Le même jour, Inès vous demande de relire sa pull request n°57 sur la
variante Python que l'équipe maintenait en parallèle : ses tests passent,
elle aimerait la fusionner avant la migration vers la forge interne.

## Objectif

Rendre un outil que n'importe qui dans l'équipe peut reprendre après vous :
conforme au contrat, couvert par une suite de tests qui ne dépend pas de son
implémentation, publié sous une version étiquetée qui s'installe d'une
commande, et accompagné de votre revue de la PR n°57. Le langage est le
vôtre, et vous expliquez pourquoi dans `CHOIX.md`.

Il n'y a ni cours ni indice dans cette épreuve : elle mesure ce que vous
savez déjà faire. La mission est dans `dsoxlab challenge`.
