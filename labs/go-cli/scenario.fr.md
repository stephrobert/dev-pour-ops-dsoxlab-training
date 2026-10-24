# Donner une interface fiable à `fleetctl`

Implémentez le module Go de départ sous la forme d'une petite CLI Ops. Elle
doit être utile pour l'inspection locale, sans dépendre d'une API active.

Le module nécessite Go 1.27.3 ou supérieur.

## Contrat

- `fleetctl help` (et l'absence d'argument) affiche l'aide et rend 0.
- `fleetctl version` affiche `fleetctl dev` et rend 0.
- `fleetctl config show [--config FICHIER]` lit le JSON (`endpoint`,
  `timeout_seconds`), applique les surcharges d'environnement et affiche du
  JSON indenté canonique.
- La priorité est : valeurs par défaut (`http://127.0.0.1:8080`, 10 secondes),
  fichier, puis `FLEETCTL_ENDPOINT` et `FLEETCTL_TIMEOUT_SECONDS`.
- Le point de terminaison doit être une URL HTTP(S) avec un hôte. Le délai
  doit être un entier de 1 à 120. Les propriétés JSON inconnues, JSON mal
  formé, valeurs invalides et commandes inconnues produisent un message
  lisible sur stderr et un code non nul.
- `go test ./...` passe et `go build -o fleetctl .` produit un exécutable
  fonctionnel.

## Étapes

1. Lisez `main_test.go` ; lancez `go test ./...` pour observer le comportement
   inachevé.
2. Implémentez le chargement, la validation et la priorité de configuration.
3. Implémentez `help`, `version` et `config show`, y compris les erreurs de
   paramètres.
4. Testez différentes combinaisons fichier/environnement, puis construisez
   et lancez le binaire.
5. Lancez `dsoxlab check go-cli`.
