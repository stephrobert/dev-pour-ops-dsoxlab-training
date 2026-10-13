# Journal de débogage : ticket n°412, vpn-01 en erreur

## Reproduire

Avec la date du ticket fixée, le symptôme revient à chaque fois :

```console
$ CERTCHECK_NOW=2026-10-13 bin/certcheck; echo $?
vpn-01	error	certificat illisible
2
```

Le test `test_un_jour_a_un_chiffre_se_lit` le reproduit sans lancer l'outil
entier : `date_expiration(certs/vpn-01.pem)` doit rendre 2031-03-05. Il
échoue sur la version d'origine.

## Réduire

Les trois autres certificats passent. openssl lit vpn-01 sans erreur, donc
le problème est dans la lecture de sa sortie. La différence entre vpn-01 et
les autres : son jour d'expiration n'a qu'un chiffre. La chaîne minimale qui
déclenche le bogue, sans certificat ni openssl :

```python
"Mar  5 12:00:00 2031 GMT".split(" ")
```

## Observer

`python3 -m pdb certcheck.py --inventory inventaire.txt`, puis un point
d'arrêt conditionnel sur la ligne du découpage :

```text
(Pdb) b 80, "vpn" in str(certificat)
(Pdb) c
(Pdb) p brut
'Mar  5 12:00:00 2031 GMT'
(Pdb) p brut.split(" ")
['Mar', '', '5', '12:00:00', '2031', 'GMT']
(Pdb) n
ValueError: too many values to unpack (expected 5, got 6)
```

Six champs au lieu de cinq : les deux espaces produisent un champ vide. Le
`except Exception` d'`analyser` avale ensuite l'exception sans rien
journaliser, ce qui explique que `--verbose` ne montre rien.

## Corriger

- `brut.split()` sans argument découpe sur toute suite de blancs : plus de
  champ vide.
- `except Exception` devient `except (OSError, ValueError) as exc`, avec un
  `log.error` qui nomme l'hôte et la cause : un certificat vraiment illisible
  reste en `error`, mais laisse une trace.
- Le test de reproduction reste dans la suite, avec un second sur le statut
  de vpn-01.
