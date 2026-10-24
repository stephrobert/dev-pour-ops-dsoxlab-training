# Normaliser des inventaires de services JSON et YAML

Une équipe Ops reçoit le même inventaire de services en JSON d'un outil et en
YAML d'un autre. Construisez un convertisseur qui produit une représentation
JSON stable, quel que soit le format d'entrée.

| | |
|---|---|
| Cible | votre poste : Go 1.27.3 ou supérieur |
| Durée | environ 45 minutes |
| Réseau | requis une fois pour télécharger le module Go YAML épinglé |
| Leçon jumelée | [Programmation en Go](https://www.stephane-robert.info/docs/developper/programmation/golang/) |

```bash
dsoxlab run data-json-yaml
cd labs/data-json-yaml/challenge/work
go test ./...
go run . inventory.yaml
go run . --output normalise.json inventory.json
go build -o fleet-data .
dsoxlab check data-json-yaml
```

La sortie Go est triée par nom de service et les dates sont au format ISO. Une
entrée invalide doit rendre un code non nul, expliquer le problème et laisser
intact un fichier de sortie déjà présent.
