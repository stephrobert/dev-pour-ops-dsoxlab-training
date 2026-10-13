# Journal de débogage : ticket n°412, vpn-01 en erreur

## Ce que j'ai vu

Avec la date fixée, le symptôme revient à chaque fois : vpn-01 est déclaré
illisible et l'outil sort en 2.

```console
$ CERTCHECK_NOW=2026-10-13 bin/certcheck; echo $?
vpn-01	error	certificat illisible
2
```

openssl lit pourtant le certificat sans erreur. Le test
`test_un_jour_a_un_chiffre_se_lit` reproduit le problème : il échouait sur la
version d'origine.

## La cause

openssl écrit `notAfter=Mar  5 12:00:00 2031 GMT`, avec deux espaces avant
un jour à un chiffre. `brut.split(" ")` découpe sur UN espace et produit un
champ vide : six morceaux au lieu de cinq, donc une `ValueError`. Le `except
Exception` d'`analyser` l'avalait sans rien journaliser, d'où le silence de
`--verbose`. Vu sous pdb (`breakpoint()` avant le découpage) : `p
brut.split(" ")` affiche `['Mar', '', '5', '12:00:00', '2031', 'GMT']`.

## La correction

- `brut.split()` sans argument découpe sur toute suite de blancs.
- `except Exception` devient `except (OSError, ValueError) as exc`, avec un
  `log.error` qui nomme l'hôte et la cause.
- Le test de reproduction reste dans la suite.
