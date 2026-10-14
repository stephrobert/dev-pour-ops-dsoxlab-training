# Le certificat que certcheck ne sait pas lire

## Situation

`TICKET.md` : certcheck sort en erreur (code 2) sur vpn-01 alors qu'openssl
lit très bien son certificat. Le contrôle quotidien est rouge tous les
jours, et plus personne ne regarde les vraies alertes. Rien dans les
journaux, même avec `--verbose`.

Le répertoire de travail est le paquet Python de certcheck : son code dans
`src/certcheck/` (la lecture des dates est dans `certificats.py`), son
lanceur `bin/certcheck`, le contrat, quatre certificats et une suite de
tests qui passe. Une suite verte ne prouve que ce qu'elle teste.

## Pourquoi une méthode

Corriger au hasard, c'est modifier une ligne, relancer, recommencer, sans
jamais savoir ce qui a vraiment changé. La méthode tient en trois temps :
**reproduire** le symptôme à volonté, **regarder** le programme au moment
où il se trompe, **corriger** puis garder le test qui le prouve.

## Étapes

### 1. Voir le symptôme

```bash
CERTCHECK_NOW=2026-10-13 bin/certcheck; echo "code : $?"
openssl x509 -enddate -noout -in certs/vpn-01.pem
```

vpn-01 est en `error`, alors qu'openssl affiche sa date d'expiration.

### 2. Reproduire par un test, AVANT de corriger

`tests/test_certcheck.py` contient déjà, en commentaire à la fin, un test qui demande la date de vpn-01. Décommentez-le :

```python
def test_un_jour_a_un_chiffre_se_lit():
    assert certificats.date_expiration(CERTS / "vpn-01.pem") == date(2031, 3, 5)
```

`uv run pytest -k chiffre -v` : il **échoue**, et c'est ce qu'on veut. Il
prouvera la correction, et il empêchera le bogue de revenir.

### 3. Regarder la valeur fautive

Lisez la trace que pytest affiche : elle nomme la ligne qui lève
l'exception. Pour voir la valeur au moment de l'erreur, deux moyens :

- un `print(repr(brut))` provisoire juste avant le découpage, dans
  `date_expiration` (`src/certcheck/certificats.py`), puis relancer le
  test ;
- le débogueur : une ligne `breakpoint()` au même endroit, puis
  `CERTCHECK_NOW=2026-10-13 bin/certcheck`. Le programme s'arrête dans pdb,
  une fois par certificat : `p brut` affiche une variable, `c` continue
  jusqu'au certificat suivant (vpn-01 est le troisième), `n` exécute la
  ligne suivante. Pour finir, `c` jusqu'au bout. Avec Python 3.14, `q`
  demande confirmation puis arrête le programme ; avec une version plus
  ancienne, l'exception qu'il lève peut être avalée par le `except
  Exception` du code, et le programme continue : préférez `c`.

Comparez avec un autre certificat : `openssl x509 -enddate -noout -in
certs/vpn-01.pem | cat -A` rend les espaces visibles.

### 4. Corriger

Deux changements, dans `src/certcheck/certificats.py` :

- le découpage de la date ne doit plus casser sur un jour à un chiffre ;
- le `except Exception` d'`analyser` avale l'erreur sans rien dire :
  n'attrapez que les erreurs attendues (`OSError`, `ValueError`) et écrivez
  un message qui nomme l'hôte avec `log.error(...)`, pour que le prochain
  certificat vraiment illisible laisse une trace.

Retirez le `print` ou le `breakpoint()` provisoire. `uv run pytest -v` doit
être vert, test de reproduction compris.

### 5. Écrire DEBUG.md

À la racine du projet, trois rubriques, quelques lignes chacune :

```markdown
## Ce que j'ai vu
## La cause
## La correction
```

## Preuve

`dsoxlab check deboguer` joue votre suite sur la version d'origine (elle
doit échouer) et sur la référence (elle doit passer), lance `bin/certcheck`
sur des parcs tirés au hasard, vérifie le reste du contrat, et lit
`DEBUG.md`.
