# Une publication qui tient la route

## Situation

certcheck respecte son contrat, sauf sur un point : la publication sur la
forge. Un collègue l'a écrite un vendredi, testée une fois sur sa forge de
test, et l'a livrée. Relisez la fonction `requete()` et la fin de
`publier()` dans `certcheck.py` : le jeton est collé à l'URL
(`?access_token=`), `urlopen` est appelé sans délai maximal, la première
erreur 503 fait abandonner, et chaque exécution ouvre un nouveau ticket.

Lancé chaque nuit par cron, cet outil ouvrirait un ticket par nuit, écrirait
le jeton dans les journaux à chaque erreur, et resterait bloqué pour toujours
le jour où la forge ne répond plus.

## Objectif

`bin/certcheck --publish` respecte la section « Publication sur la forge » de
`CONTRAT.md` :

- le jeton part dans l'en-tête `Authorization: token <jeton>`, jamais dans
  une URL ni sur une sortie ;
- avant d'ouvrir, l'outil cherche un ticket ouvert qui porte **exactement**
  le titre `certcheck : certificats à renouveler`, dans **toutes** les pages
  de la liste ;
- une réponse 429 ou 5xx est reprise, trois essais au total, avec une
  attente entre deux, avant d'abandonner en code 3 ;
- chaque requête a un délai maximal : une forge qui ne répond pas fait
  sortir l'outil en code 3, pas l'attendre indéfiniment.

Le reste de l'outil (lecture, décision, sorties, codes) est déjà conforme :
n'y touchez pas.

## Repères

- `urllib.request.Request(url, headers={"Authorization": f"token {jeton}"})`
  place le jeton dans l'en-tête ; `urlopen(demande, timeout=5)` borne
  l'attente de la connexion et de chaque lecture.
- `urllib.error.HTTPError` porte le code HTTP dans `exc.code` ; un délai
  dépassé lève `TimeoutError` (ou `URLError` pendant la connexion).
- La liste des tickets : `GET /api/v1/repos/{dépôt}/issues?state=open&type=issues&limit=50&page=N`.
  La forge rend 30 tickets par page par défaut et 50 au plus ; une page
  incomplète (ou vide) est la dernière. L'en-tête `Link: rel="next"` donne
  aussi la page suivante.
- `--verbose` écrit le journal sur la sortie d'erreur : vérifiez qu'il ne
  contient jamais le jeton.
