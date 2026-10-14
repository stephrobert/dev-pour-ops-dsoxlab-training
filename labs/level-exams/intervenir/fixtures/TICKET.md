# Ticket n°431 : un certificat à 30 jours n'a pas alerté

**Signalé par** : l'astreinte
**Priorité** : haute

## Ce qui se passe

Le rapport de certcheck du 31 octobre n'a signalé aucun des certificats qui
expirent dans exactement 30 jours, le seuil de l'équipe. Le contrat
(`CONTRAT.md`) dit pourtant que le seuil est inclusif. Le rapport du début du
mois les signalait bien : quelque chose a changé depuis.

Par ailleurs, la pipeline de CI est rouge depuis quelques jours sur `main`.
Personne n'a regardé pourquoi. Son dernier journal est dans `ci/run-12.log`.

## Ce qu'on attend

Une correction limitée au défaut, des tests verts, des contrôles de qualité
verts, et une pipeline qui repasse au vert.
