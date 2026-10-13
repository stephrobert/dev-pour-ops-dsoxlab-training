# certcheck opens its ticket

## Situation

certcheck checks the fleet every night. The team wants it to also open a
ticket on the forge when certificates are due, instead of waiting for
someone to read its output. In `src/certcheck/forge.py`, the module that
talks to the forge, the `publier()` function is ready; the two functions
that talk to the API, `requete()` and `ticket_existe()`, are missing and
marked "À ÉCRIRE" (to write).

The forge is configured by three variables: `FORGE_URL` (the address),
`FORGE_TOKEN` (the token, a secret) and `FORGE_REPO` (the repository,
`exploitation/certificats`).

## Why these rules

This call will run every night, with nobody watching:

- a token glued to the URL ends up in server and proxy logs: it travels in
  a **header**;
- a forge that stops answering must not block the tool forever: every
  request has a **timeout**;
- an error (rejected token, forge down) must give **exit code 3** and a
  readable message, not a Python traceback;
- the tool runs every night: if it does not check whether a ticket is
  already open, it opens one **per night**.

## Steps

### 1. Declare requests in the project

`requests` is not in the standard library. Declare it, at an exact
version, as the rule written in `pyproject.toml` requires:

```bash
uv add requests==2.34.2
```

uv writes the dependency in `pyproject.toml`, freezes the whole set in
`uv.lock`, and installs it in `.venv`. Add `import requests` at the top of
`src/certcheck/forge.py`, with the other imports.

### 2. Write requete()

A request with requests fits in one call:

```python
reponse = requests.request(methode, url, json=corps, timeout=DELAI_RESEAU,
                           headers={"Authorization": f"token {jeton}"})
reponse.raise_for_status()
return reponse.json()
```

`timeout=` bounds the wait, `headers=` carries the token, and
`raise_for_status()` raises an exception if the forge answers 4xx or 5xx.
Wrap it all in a `try` / `except requests.RequestException as exc`, and
raise `ErreurPublication(f"{methode} {url} : {exc}")` instead: the interface
(`cli.py`) already turns it into code 3. The message names the URL, never
the token.

### 3. Write ticket_existe()

Read the list of open tickets with `requete("GET", ...)` on
`{base}/api/v1/repos/{depot}/issues?state=open&type=issues`, then return
`True` if one of them carries **exactly** the title `TITRE_TICKET`. This lab
sticks to the first page of the list.

### 4. Try it against the fake forge

In a second terminal: `python3 forge_factice.py`. Then:

```bash
export FORGE_URL=http://127.0.0.1:8099 FORGE_TOKEN=jeton-de-demo
export FORGE_REPO=exploitation/certificats
CERTCHECK_NOW=2026-06-01 bin/certcheck --publish; echo "code: $?"
```

Run it again: no second ticket. Try `FORGE_TOKEN=wrong` (401), then the
forge started with `--panne` (503): code 3 and a clear message.

### 5. Check

`dsoxlab check appeler-une-api`.

## Outside this lab

Pagination beyond the first page and automatic retries on a transient
failure are in `CONTRAT.md`, but belong to a more advanced level: this lab
does not grade them.
