# Ticket n°412 : certcheck en erreur sur vpn-01

**Signalé par** : l'astreinte réseau
**Priorité** : normale, mais le contrôle quotidien est rouge depuis lundi

## Ce qui se passe

certcheck sort en erreur (code 2) sur vpn-01 alors qu'openssl lit très bien
son certificat. Le pipeline du contrôle quotidien échoue donc tous les jours,
et plus personne ne regarde les vraies alertes.

```console
$ bin/certcheck
web-01	ok	6820 jours	2045-06-15
web-02	expired	-327 jours	2025-11-20
vpn-01	error	certificat illisible
mail-01	ok	4837 jours	2040-01-10
$ echo $?
2

$ openssl x509 -enddate -noout -in certs/vpn-01.pem
notAfter=Mar  5 12:00:00 2031 GMT
```

Le certificat est valide, openssl le lit sans broncher. Rien dans les
journaux, même avec `--verbose`.

## Ce qu'on attend

vpn-01 est lu, son statut est juste, et le code de sortie redevient celui du
contrat (`CONTRAT.md`). Et la prochaine fois qu'un certificat est vraiment
illisible, on aimerait savoir pourquoi.
