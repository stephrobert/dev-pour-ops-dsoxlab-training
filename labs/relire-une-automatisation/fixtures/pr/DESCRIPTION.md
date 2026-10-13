# Pull request n°42 : purge des anciens rapports et notification par webhook

Ouverte par **Malik**, branche `malik/purge-et-webhook` vers `main`.

## Contexte

Le cron nocturne écrit un rapport par nuit dans le dossier des rapports
(`CERTCHECK_REPORT_DIR`), et personne ne les supprime : le disque du serveur
d'exploitation a atteint 92 % la semaine dernière. Par ailleurs, l'équipe
voudrait voir les alertes dans le chat sans aller lire la forge.

## Ce que fait la PR

- Nouvelle option `--purge-days N` : supprime les rapports plus vieux que
  N jours dans `CERTCHECK_REPORT_DIR`.
- Nouvelle option `--notify` : poste le résumé des certificats à renouveler
  sur le webhook du chat, lu dans `CERTCHECK_WEBHOOK_URL` (l'URL fournie par
  le chat contient le jeton, du genre
  `https://chat.interne.example/hooks/certcheck?token=...`).
- Nouveau module `maintenance.py`, pour ne pas alourdir `certcheck.py`.
- Ajout de `requests`, plus simple qu'`urllib` pour le POST JSON.
- Version 0.5.0.

## Comment tester

```bash
export CERTCHECK_REPORT_DIR=/var/lib/certcheck/rapports
export CERTCHECK_WEBHOOK_URL='https://chat.interne.example/hooks/certcheck?token=...'
uv run python certcheck.py --notify --purge-days 30
uv run pytest
```

## Remarques

- Le chat interne répondait par une erreur de certificat depuis le serveur
  d'exploitation : c'est contourné, la notification part bien.
- Si le chat est indisponible, la notification ne doit pas faire échouer le
  contrôle des certificats : c'est géré.

## Liste de contrôle

- [x] Les tests passent (`uv run pytest` : 8 passed)
- [x] Tests ajoutés
- [x] Testé en local
- [x] Pas d'appel au shell
