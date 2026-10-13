# Appeler une API sans fragilité

Troisième lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon
« Automatiser par une API REST : authentification, pagination, erreurs et
reprise ». certcheck sait déjà contrôler un parc ; il doit maintenant
**publier** son résultat sur la forge sans fuite de secret, sans doublon et
sans rester bloqué quand la forge va mal.

| | |
|---|---|
| Cible | votre poste : Python (`mise install`) et openssl |
| Durée | environ 45 minutes |
| Leçon jumelée | [Automatiser par une API REST](https://blog.stephane-robert.info/docs/developper/api-rest/) |
| Précédent | `script-en-outil` |

```bash
dsoxlab run   appeler-une-api
cd labs/appeler-une-api/challenge/work
less CONTRAT.md                       # section « Publication sur la forge »
CERTCHECK_NOW=2026-06-01 bin/certcheck --publish --dry-run; echo "code : $?"
# corrigez la partie « Publication sur la forge » de certcheck.py
dsoxlab check appeler-une-api
```

Le point de départ est l'outil du lab précédent, conforme au contrat sauf sa
publication, écrite à la hâte par un collègue. Le contrôle ne lit pas votre
code : il lance `bin/certcheck --publish` contre une forge factice qui répond
comme l'API de Forgejo, et compte les requêtes qu'elle reçoit.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
