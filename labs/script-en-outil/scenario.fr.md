# Un projet qui a un contrat

## Situation

Le script Bash `certcheck.sh` contrôle encore les certificats sur un vieux
serveur : il sort toujours en 0, signale un certificat absent comme
« 0 jour », n'a ni aide ni sortie exploitable par une machine. L'équipe a
écrit ce qu'elle attend de son remplaçant dans `CONTRAT.md`, et a posé le
squelette du projet Python qui doit le remplacer.

Le squelette est structuré comme un développeur le ferait : le paquet
`src/certcheck/`, découpé en deux modules (`certificats.py` lit
l'inventaire et décide du statut, `cli.py` gère l'interface), un
`pyproject.toml` qui déclare la commande `certcheck` dans
`[project.scripts]`, un `uv.lock`, et le lanceur `bin/certcheck`, qui
l'exécute par `uv run`. Une partie du code est écrite ; les autres fonctions
sont là, avec leur docstring et des exemples, mais lèvent
`NotImplementedError`.

## Objectif

`bin/certcheck` respecte le contrat : aide et version, usage incorrect en
code 2, codes 0, 1 et 2 selon les certificats, sortie JSON, seuil réglable
par `CERTCHECK_DAYS`, et erreurs sur la sortie d'erreur. Le script Bash reste
là comme ancienne implémentation à lire, pas à appeler.

## Repères

- `uv run certcheck --help` lance la commande déclarée par le projet, dans
  son environnement ; `bin/certcheck` fait la même chose depuis n'importe
  quel dossier.
- Tant qu'une fonction lève `NotImplementedError`, la commande affiche une
  trace Python : sa dernière ligne dit quelle fonction écrire.
- `CERTCHECK_NOW=AAAA-MM-JJ` fixe la date du jour : sans elle, impossible de
  tester une alerte avec des certificats à dates fixes.
- `print(..., file=sys.stderr)` écrit sur la sortie d'erreur ; la sortie
  standard ne porte que le résultat.
