# The script nobody wrote

## Situation

Every night, cron runs `certcheck.py` to check the expiry of the fleet's TLS
certificates. Julien wrote it two years ago, then moved to another team. Last
month, a host's certificate expired although the previous night's report said
`ok`. The script is now yours.

The working directory holds the script (`certcheck.py`, about eighty lines),
the inventory it reads (`inventaire.txt`) and the certificates collected on
the hosts (`certs/`).

## Goal

First **understand** the script as you received it, and write it down in
`reponses.yaml`: its role, its inputs, the function that decides, what it
prints and its exit code. Only then **modify** it:

1. a certificate that expires **exactly** at the threshold must become
   `warning`;
2. a certificate that has **already expired** must show `expired`, not
   `warning`.

## Hints

- Read from the bottom up: `if __name__ == "__main__"` calls `main()`, and
  `main()` calls the other functions.
- `python3 certcheck.py --help` lists the options without running anything
  else.
- The script only **reads**: it runs `openssl` on each certificate and prints
  one line per host. Running it changes nothing.
- `CERTCHECK_NOW=2026-10-31 python3 certcheck.py` replays the check as if it
  were 31 October 2026; `echo "code: $?"` then prints its exit code.
- A condition changes with one character: `<` and `<=` do not say the same
  thing at the boundary.
