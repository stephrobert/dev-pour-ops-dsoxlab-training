# Le certificat que certcheck ne sait pas lire

## Situation

`TICKET.md` : certcheck sort en erreur (code 2) sur vpn-01 alors qu'openssl
lit très bien son certificat. Le contrôle quotidien est rouge tous les
jours, et plus personne ne regarde les vraies alertes. Rien dans les
journaux, même avec `--verbose`.

Le répertoire de travail est le projet uv de certcheck : `certcheck.py`, son
lanceur `bin/certcheck`, le contrat, quatre certificats et une suite de
tests qui passe. Une suite verte ne prouve que ce qu'elle teste.

## Objectif

Traiter le ticket avec méthode, en quatre temps, et en garder la trace dans
un fichier `DEBUG.md` à la racine du projet, une section `##` par temps.

1. **Reproduire.** Un symptôme qu'on ne sait pas déclencher à volonté ne se
   corrige pas. Écrivez un test qui échoue sur la version actuelle, AVANT de
   toucher au code : il prouvera la correction, et il empêchera le bogue de
   revenir.
2. **Réduire.** Retirez tout ce qui n'est pas nécessaire (l'inventaire, les
   autres hôtes, openssl lui-même) jusqu'à la plus petite entrée qui casse
   encore. Citez cette chaîne exacte, espaces compris, dans la section
   `## Réduire`.
3. **Observer.** Regardez le programme au moment où il se trompe, au lieu de
   deviner. Le bogue s'observe sous le débogueur de Python :
   `python3 -m pdb certcheck.py --inventory inventaire.txt`, puis un point
   d'arrêt (`b date_expiration`, ou `b <ligne>, "vpn" in str(certificat)`
   pour ne s'arrêter que sur vpn-01), `c` pour continuer, `p brut` pour
   afficher une variable, `n` pour avancer d'une ligne. Une ligne
   `breakpoint()` posée dans le code fait la même chose sans option.
4. **Corriger.** La plus petite modification qui fait passer le test de
   reproduction, sans casser le reste du contrat. Demandez-vous aussi
   pourquoi le bogue est resté invisible.

## Repères

- `uv run pytest -v` lance la suite ; `uv run pytest -k vpn` ne lance que
  les tests dont le nom contient « vpn ».
- `openssl x509 -enddate -noout -in certs/vpn-01.pem` montre ce que
  certcheck reçoit. Comparez avec un autre certificat, caractère par
  caractère : `| cat -A` rend les espaces et les fins de ligne visibles.
- Sous pdb, quitter par `q` lève une exception `BdbQuit`. Un `except
  Exception` trop large l'avale aussi, et le programme continue : c'est un
  indice de plus sur ce que ce `except` cache.
- La date du jour se fixe par `CERTCHECK_NOW=AAAA-MM-JJ`, ou se passe aux
  fonctions : un test ne doit pas dépendre du jour où il tourne.

## Preuve

`dsoxlab check deboguer` joue votre suite sur la version d'origine (elle
doit échouer) et sur la référence (elle doit passer), lance `bin/certcheck`
sur des parcs tirés au hasard, rejoue le reste du contrat, et lit
`DEBUG.md`.
