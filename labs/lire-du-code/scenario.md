# The script nobody wrote

## Situation

Every night, `certcheck.sh` checks the expiry of the fleet's TLS
certificates. Julien wrote it in 2024, Karim extended it, and both have moved
to other teams. Last month a certificate expired without any alert going
out: the script is now yours.

The working directory holds the script, the inventory it reads, the
certificates collected on the hosts (`certs/`), and its Git history as a
bundle (`historique.bundle`).

## Goal

Understand what the script does **before** changing it, and prove it in
`reponses.yaml`: its external commands, its side effects, what running it
shows, its real defects, and the commit that started hiding errors.

## Hints

- Read from the entry point (the code outside functions, at the bottom) to
  the functions it calls.
- `type -t <word>` tells whether a word is a Bash builtin, a keyword or a
  program from the PATH.
- Running it safely: without `FORGE_TOKEN`, the script does not call the
  forge. It still writes a file: which one?
- `git log -S '<string>'` finds the commits that added or removed a string;
  `git blame` tells who wrote each current line.
