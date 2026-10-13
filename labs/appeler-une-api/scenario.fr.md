# certcheck ouvre son ticket

## Situation

certcheck contrôle le parc chaque nuit. L'équipe veut qu'il ouvre aussi un
ticket sur la forge quand des certificats sont à renouveler, au lieu
d'attendre que quelqu'un lise sa sortie. Dans `src/certcheck/forge.py`, le
module qui parle à la forge, la fonction `publier()` est prête ; il manque
les deux fonctions qui parlent à l'API, `requete()` et `ticket_existe()`,
marquées « À ÉCRIRE ».

La forge se configure par trois variables : `FORGE_URL` (l'adresse),
`FORGE_TOKEN` (le jeton, un secret) et `FORGE_REPO` (le dépôt,
`exploitation/certificats`).

## Pourquoi ces règles

Cet appel tournera chaque nuit, sans personne devant l'écran :

- un jeton collé à l'URL finit dans les journaux du serveur et des proxys :
  il voyage dans un **en-tête** ;
- une forge qui ne répond plus ne doit pas bloquer l'outil pour toujours :
  chaque requête a un **délai maximal** ;
- une erreur (jeton refusé, forge en panne) doit donner un **code de sortie
  3** et un message lisible, pas une trace Python ;
- l'outil tourne chaque nuit : s'il ne vérifie pas qu'un ticket est déjà
  ouvert, il en ouvre un **par nuit**.

## Étapes

### 1. Déclarer requests dans le projet

`requests` n'est pas dans la bibliothèque standard. Déclarez-le, à une
version exacte, comme le demande la règle écrite dans `pyproject.toml` :

```bash
uv add requests==2.34.2
```

uv écrit la dépendance dans `pyproject.toml`, fige l'ensemble dans
`uv.lock`, et l'installe dans `.venv`. Ajoutez `import requests` en haut de
`src/certcheck/forge.py`, avec les autres imports.

### 2. Écrire requete()

Une requête avec requests tient en un appel :

```python
reponse = requests.request(methode, url, json=corps, timeout=DELAI_RESEAU,
                           headers={"Authorization": f"token {jeton}"})
reponse.raise_for_status()
return reponse.json()
```

`timeout=` borne l'attente, `headers=` porte le jeton, et
`raise_for_status()` lève une exception si la forge répond 4xx ou 5xx.
Entourez le tout d'un `try` / `except requests.RequestException as exc`, et
levez à la place `ErreurPublication(f"{methode} {url} : {exc}")` :
l'interface (`cli.py`) la traduit déjà en code 3. Le message cite l'URL,
jamais le jeton.

### 3. Écrire ticket_existe()

Lisez la liste des tickets ouverts avec `requete("GET", ...)` sur
`{base}/api/v1/repos/{depot}/issues?state=open&type=issues`, puis rendez
`True` si l'un d'eux porte **exactement** le titre `TITRE_TICKET`. Ce lab
s'en tient à la première page de la liste.

### 4. Essayer contre la forge factice

Dans un second terminal : `python3 forge_factice.py`. Puis :

```bash
export FORGE_URL=http://127.0.0.1:8099 FORGE_TOKEN=jeton-de-demo
export FORGE_REPO=exploitation/certificats
CERTCHECK_NOW=2026-06-01 bin/certcheck --publish; echo "code : $?"
```

Relancez : aucun second ticket. Essayez `FORGE_TOKEN=faux` (401), puis la
forge lancée avec `--panne` (503) : code 3 et un message clair.

### 5. Vérifier

`dsoxlab check appeler-une-api`.

## Hors de ce lab

La pagination au-delà de la première page et la reprise automatique sur
panne passagère figurent dans `CONTRAT.md`, mais relèvent d'un niveau plus
avancé : ce lab ne les note pas.
