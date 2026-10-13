# Appeler une API avec requests

Lab du fil rouge de **Développer pour les Ops**, jumelé à la leçon « Appeler
une API REST avec Python et requests ». certcheck sait déjà contrôler un
parc ; il doit maintenant **ouvrir un ticket** sur la forge quand des
certificats sont à renouveler. Vous écrivez cet appel avec la bibliothèque
`requests`, pas à pas : déclarer la dépendance, passer le jeton au bon
endroit, borner l'attente, traiter les erreurs, ne pas créer de doublon.

| | |
|---|---|
| Cible | votre poste : Python et uv (`mise install`), openssl |
| Durée | environ 30 minutes |
| Réseau | requis une fois : uv télécharge `requests` depuis PyPI |
| Leçon jumelée | [Appeler une API REST avec Python et requests](https://blog.stephane-robert.info/docs/developper/api-rest/) |
| Précédent | `script-en-outil` |

```bash
dsoxlab run   appeler-une-api
cd labs/appeler-une-api/challenge/work
CERTCHECK_NOW=2026-06-01 bin/certcheck --publish --dry-run; echo "code : $?"
# suivez les étapes du scénario dans src/certcheck/forge.py
python3 forge_factice.py        # dans un second terminal, pour essayer
dsoxlab check appeler-une-api
```

Le contrôle ne lit pas votre code : il lance `bin/certcheck --publish`
contre une forge factice qui répond comme l'API de Forgejo, et regarde les
requêtes qu'elle reçoit.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable. Le verdict est dans `validation-labs.json`.
