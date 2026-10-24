# Construire une CLI Go simple et prévisible

L'équipe plateforme a besoin d'une commande locale `fleetctl` qui affiche son
point de terminaison de déploiement et son délai d'attente sans exiger qu'un
service soit en ligne. Implémentez les sous-commandes, la priorité prévisible
de configuration et les tests avant de produire un binaire autonome.

| | |
|---|---|
| Cible | votre poste : Go 1.27.3 ou supérieur |
| Durée | environ 60 minutes |
| Réseau | non requis par le lab ; Go peut télécharger la toolchain déclarée si nécessaire |
| Leçon jumelée | [Programmation en Go](https://www.stephane-robert.info/docs/developper/programmation/golang/) |

```bash
dsoxlab run go-cli
cd labs/go-cli/challenge/work
go test ./...
go run . help
go run . config show --config fleetctl.json
go build -o fleetctl .
dsoxlab check go-cli
```

La priorité est : valeurs par défaut, fichier JSON, puis variables
d'environnement. Le contrôle vérifie la sortie réelle, les codes de sortie,
les configurations invalides, les tests et l'exécutable construit.
