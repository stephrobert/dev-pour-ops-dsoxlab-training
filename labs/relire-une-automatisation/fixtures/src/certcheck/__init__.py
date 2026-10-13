"""certcheck : signale les certificats TLS d'un parc qui arrivent à expiration.

Contrat complet : CONTRAT.md. Codes de sortie :
  0  tous les certificats sont valides au-delà du seuil
  1  au moins un certificat expire dans le seuil, ou a expiré
  2  usage incorrect ou entrée inexploitable (inventaire, certificat illisible)
  3  la publication sur la forge a échoué
"""

__version__ = "0.4.0"
