# Pull request n°42 : purge des anciens rapports et notification du chat

Ouverte par **Malik**, branche `malik/purge-et-webhook` vers `main`.

## Contexte

Le cron nocturne écrit un rapport par nuit dans `CERTCHECK_REPORT_DIR`, et
personne ne les supprime : le disque du serveur d'exploitation a atteint
92 %. L'équipe voudrait aussi voir les alertes dans le chat.

## Ce que fait la PR

- `--purge-days N` : supprime les rapports plus vieux que N jours dans
  `CERTCHECK_REPORT_DIR`.
- `--notify` : poste les certificats à renouveler sur le webhook du chat, lu
  dans `CERTCHECK_WEBHOOK_URL` (l'URL fournie par le chat contient le jeton,
  du genre `https://chat.interne.example/hooks/certcheck?token=...`).
- Nouveau module `src/certcheck/maintenance.py`.

## Remarques

- Si le chat est indisponible, la notification ne doit pas faire échouer le
  contrôle des certificats : c'est géré.

## Liste de contrôle

- [x] Les tests passent (`uv run pytest` : 7 passed)
- [x] Test ajouté
