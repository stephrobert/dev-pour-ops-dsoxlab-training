# Déboguer pas à pas

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon « Déboguer
un programme Python pas à pas, avec pdb ». Un ticket est arrivé : certcheck
déclare un certificat illisible alors qu'openssl le lit sans peine. Vous le
traitez dans l'ordre plutôt qu'au hasard : **reproduire** par un test,
**regarder** la valeur fautive, **corriger**, et garder une trace courte de ce
que vous avez appris.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), openssl |
| Durée | environ 25 minutes |
| Leçon jumelée | [Déboguer un programme Python pas à pas, avec pdb](https://dev.stephane-robert.info/docs/developper/pratiques/deboguer/) |
| Précédent | `tester-une-automatisation` |

```bash
dsoxlab run   deboguer
cd labs/deboguer/challenge/work
less TICKET.md
uv run pytest -v                  # la suite livrée passe, et pourtant
# suivez les étapes du scénario
dsoxlab check deboguer
```

Le contrôle joue votre suite sur la version boguée d'origine (elle doit
échouer) et sur la référence (elle doit passer), lance `bin/certcheck` sur
des parcs tirés au hasard, vérifie le reste du contrat et lit `DEBUG.md`.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
