# The application nobody wrote

## Situation

Every night, the `certcheck` command checks the expiry of the fleet's TLS
certificates. It is a Python package: Julien structured it in 2024, Karim
extended it, and both have moved to other teams. Last month a certificate
expired without any alert going out: the code is now yours.

The working directory holds the project (`pyproject.toml`, `uv.lock`, the
package under `src/certcheck/`), the inventory it reads, the certificates
collected on the hosts (`certs/`), and its Git history as a bundle
(`historique.bundle`).

## Goal

Understand what the application does **before** changing it, and prove it
in `reponses.yaml`: its entry point and the modules it loads, its side
effects, what running it shows, its real defects, and the commit that
started swallowing errors.

## Hints

- A command installed by a Python package does not necessarily start in a
  `main` function: `pyproject.toml` declares it in `[project.scripts]`, in
  the form `module:function`.
- Read from the entry point to the functions it calls, opening each
  imported module. An import can hide inside a function.
- Running it safely: without `FORGE_TOKEN`, certcheck does not call the
  forge, and `CERTCHECK_NOW` sets today's date.
- `git log -S '<string>'` finds the commits that added or removed a string;
  `git blame` tells who wrote each current line.
