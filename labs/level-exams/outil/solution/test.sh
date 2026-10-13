#!/usr/bin/env bash
# Lance la suite de tests de certcheck, en boîte noire, contre l'exécutable
# désigné par CERTCHECK_BIN (bin/certcheck par défaut). Sort en 0 si tout passe.
#
#   ./test.sh                                  # l'outil du dépôt
#   CERTCHECK_BIN=/usr/local/bin/certcheck ./test.sh   # un outil installé
set -euo pipefail
cd "$(dirname "$0")"
export CERTCHECK_BIN="${CERTCHECK_BIN:-$PWD/bin/certcheck}"
# --frozen : uv.lock fait foi, rien n'est résolu à nouveau.
exec uv run --frozen --quiet pytest -q -p no:cacheprovider
