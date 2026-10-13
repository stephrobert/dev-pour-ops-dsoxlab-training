# Contrat de l'outil certcheck

Ce document dit ce que **certcheck** doit faire, vu de l'extérieur. Il ne dit
rien du langage : l'outil peut être écrit en Bash, en Python ou en Go. Il est
vérifié en **boîte noire**, en lançant `bin/certcheck` comme le feraient cron
ou un pipeline.

## Entrée : l'inventaire

Un fichier texte, une ligne par hôte : le nom de l'hôte, puis le chemin du
certificat PEM collecté sur cet hôte, séparés par des **espaces ou des
tabulations**. Un chemin relatif se résout depuis le **dossier de
l'inventaire**. Les lignes vides et celles qui commencent par `#` sont
ignorées.

```text
# hôte    certificat collecté
web-01    certs/web-01.pem
vpn-01	certs/vpn-01.pem
```

## Ligne de commande

| Option | Effet |
|---|---|
| `--inventory FICHIER` | l'inventaire à lire |
| `--days N` | le seuil d'alerte, en jours (entier positif) |
| `--format text\|json` | le format de la sortie standard, `text` par défaut |
| `--publish` | ouvre un ticket sur la forge pour les certificats à renouveler |
| `--dry-run` | avec `--publish` : montre le ticket sur la sortie d'erreur, sans rien envoyer |
| `--verbose` | journal détaillé sur la sortie d'erreur |
| `--version` | affiche `certcheck X.Y.Z` et sort en 0 |
| `--help` | l'aide, qui cite chaque option, sur la sortie standard, et sort en 0 |

Une option inconnue ou une valeur invalide (`--days abc`, `--format xml`)
écrit un message sur la **sortie d'erreur** et sort en **2**, sans rien écrire
sur la sortie standard.

## Configuration par l'environnement

| Variable | Rôle | Défaut |
|---|---|---|
| `CERTCHECK_INVENTORY` | l'inventaire, si `--inventory` est absent | `inventaire.txt` |
| `CERTCHECK_DAYS` | le seuil, si `--days` est absent | `30` |
| `CERTCHECK_NOW` | la date du jour, `AAAA-MM-JJ` (pour les tests) | la date du jour, en UTC |
| `FORGE_URL`, `FORGE_TOKEN`, `FORGE_REPO` | la forge, pour `--publish` | aucun |

L'option l'emporte toujours sur la variable, la variable sur le défaut.

## Décision

Pour chaque certificat, `days_left` est le nombre de jours entre la date du
jour et la **date** d'expiration (`notAfter`, en UTC) :

| Statut | Condition |
|---|---|
| `expired` | `days_left < 0` |
| `warning` | `0 <= days_left <= seuil` (le seuil est **inclusif**) |
| `ok` | `days_left > seuil` |
| `error` | certificat absent ou illisible |

## Sorties

- **`--format text`** : une ligne par hôte, qui contient au moins le nom de
  l'hôte et son statut.
- **`--format json`** : un seul document JSON sur la sortie standard, rien
  d'autre :

```json
{
  "threshold_days": 30,
  "certificates": [
    {"host": "web-01", "not_after": "2045-06-15", "days_left": 6819, "status": "ok"},
    {"host": "web-03", "not_after": null, "days_left": null, "status": "error"}
  ]
}
```

- Les **journaux et messages d'erreur** vont sur la **sortie d'erreur**.
- Aucun **secret** (le jeton) n'apparaît jamais ni sur une sortie, ni dans
  une URL.

## Codes de sortie

| Code | Sens |
|---|---|
| 0 | tous les certificats sont `ok` |
| 1 | au moins un certificat `warning` ou `expired`, aucun `error` |
| 2 | usage incorrect, configuration manquante, inventaire ou certificat inexploitable |
| 3 | la publication sur la forge a échoué |

## Publication sur la forge

Avec `--publish` (et sans `--dry-run`) :

- `FORGE_URL`, `FORGE_TOKEN` et `FORGE_REPO` sont **toutes** exigées, sinon
  code 2, avant tout autre travail ;
- le jeton part dans l'en-tête `Authorization: token <jeton>`, **jamais dans
  l'URL** ;
- s'il y a des certificats `warning` ou `expired`, l'outil ouvre **un** ticket
  intitulé exactement `certcheck : certificats à renouveler`
  (`POST /api/v1/repos/{FORGE_REPO}/issues`) ;
- l'opération est **idempotente** : si un ticket ouvert porte déjà ce titre,
  l'outil n'en ouvre pas d'autre. Il le cherche dans **toutes** les pages de
  `GET /api/v1/repos/{FORGE_REPO}/issues?state=open&type=issues` (la forge
  rend 30 tickets par page par défaut, 50 au plus avec `limit`) ;
- chaque requête a un **délai maximal** ; une réponse 429 ou 5xx est
  **reprise** (trois essais au total) avant d'abandonner en code 3.

Avec `--dry-run`, aucune requête n'est envoyée et aucune variable `FORGE_*`
n'est exigée.
