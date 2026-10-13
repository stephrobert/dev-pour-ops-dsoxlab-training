# Un outil qui a un contrat

## Situation

Vous avez lu `certcheck.sh` : il sort toujours en 0, signale un certificat
absent comme « 0 jour », n'a ni aide ni sortie exploitable par une machine.
L'équipe a écrit ce qu'elle attend de son remplaçant dans `CONTRAT.md`.

Le point d'entrée est imposé : `bin/certcheck`. Il lance aujourd'hui le script
hérité. Vous le faites pointer sur votre outil, écrit dans le langage de votre
choix : Python (celui de la leçon), Go, ou Bash si vous savez le justifier.

## Objectif

`bin/certcheck` respecte le contrat, sauf la publication réelle sur la forge,
qui fait l'objet du lab suivant : aide et version, usage incorrect en code 2,
codes 0, 1 et 2 selon les certificats, sortie JSON, configuration par
`CERTCHECK_INVENTORY`, `CERTCHECK_DAYS` et `CERTCHECK_NOW`, et `--dry-run`
qui n'envoie rien.

## Repères

- `CERTCHECK_NOW=AAAA-MM-JJ` fixe la date du jour : sans elle, impossible de
  tester une alerte avec des certificats à dates fixes.
- Python : `argparse` sort déjà en 2 sur un usage incorrect ; `print(...,
  file=sys.stderr)` écrit sur la sortie d'erreur.
- `openssl x509 -enddate -noout -in <fichier>` donne la date d'expiration ;
  attention aux jours à un chiffre, écrits avec deux espaces.
