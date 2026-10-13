# A tool with a contract

## Situation

You read `certcheck.sh`: it always exits 0, reports a missing certificate as
"0 days", and has neither help nor machine-readable output. The team wrote
what it expects from its replacement in `CONTRAT.md`.

The entry point is fixed: `bin/certcheck`. Today it runs the inherited
script. Point it at your tool, written in the language of your choice:
Python (the lesson's), Go, or Bash if you can justify it.

## Goal

`bin/certcheck` honours the contract, except the real publication to the
forge, which is the next lab: help and version, usage errors as code 2,
codes 0, 1 and 2 depending on the certificates, a JSON output, configuration
through `CERTCHECK_INVENTORY`, `CERTCHECK_DAYS` and `CERTCHECK_NOW`, and a
`--dry-run` that sends nothing.

## Hints

- `CERTCHECK_NOW=YYYY-MM-DD` sets today's date: without it, no alert can be
  tested with fixed-date certificates.
- Python: `argparse` already exits 2 on a usage error; `print(...,
  file=sys.stderr)` writes to standard error.
- `openssl x509 -enddate -noout -in <file>` gives the expiry date; mind the
  single-digit days, written with two spaces.
