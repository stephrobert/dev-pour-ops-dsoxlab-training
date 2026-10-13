# Déboguer avec méthode

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Déboguer ». Un ticket est arrivé : certcheck déclare un certificat
illisible alors qu'openssl le lit sans peine. Vous le traitez avec une
**méthode** plutôt qu'au hasard : reproduire, réduire, observer, corriger, et
garder la trace de chaque étape.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), openssl |
| Durée | environ 45 minutes |
| Leçon jumelée | [Déboguer](https://blog.stephane-robert.info/docs/developper/pratiques/deboguer/) |
| Précédent | `tester-une-automatisation` |

```bash
dsoxlab run   deboguer
cd labs/deboguer/challenge/work
less TICKET.md
uv run pytest -v                  # la suite livrée passe, et pourtant
python3 -m pdb certcheck.py       # observer le bogue en direct
dsoxlab check deboguer
```

Le contrôle joue votre suite sur la version boguée d'origine (elle doit
échouer) et sur la référence (elle doit passer), lance `bin/certcheck` sur
des parcs tirés au hasard, vérifie le reste du contrat et lit `DEBUG.md`.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
