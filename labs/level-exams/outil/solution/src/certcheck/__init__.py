"""certcheck : signale les certificats TLS d'un parc qui arrivent à expiration.

Contrat : CONTRAT.md. Codes de sortie :
  0  tous les certificats sont valides au-delà du seuil
  1  au moins un certificat expire dans le seuil, ou a expiré
  2  usage incorrect ou entrée inexploitable (inventaire, certificat illisible)

Le paquet est découpé par responsabilité : certificats.py lit l'inventaire
et décide du statut de chaque certificat, cli.py traduit tout cela en
arguments, sorties et codes de sortie.
"""

__version__ = "1.0.0"
