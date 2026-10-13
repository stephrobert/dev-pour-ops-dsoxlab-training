#!/usr/bin/env bash
# Fabrique historique.bundle, l'historique Git du script hérité du fil rouge.
#
# Cinq commits datés, deux auteurs, et un commit qui introduit l'erreur
# avalée (`2>/dev/null` sur openssl) : le lab lire-du-code demande de le
# retrouver avec `git log -S` ou `git blame`. Dates et identités fixes : le
# bundle se reconstruit à l'identique, empreintes comprises.
#
#   bash scripts/generer_historique.sh labs/lire-du-code/fixtures/historique.bundle
set -euo pipefail

sortie="$(realpath -m "$1")"
racine="$(cd "$(dirname "$0")/.." && pwd)"
final="$racine/donnees/herite/certcheck.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cd "$tmp"
git init -q -b main
git config user.name "inutilise"
git config user.email "inutilise@example.invalid"
git config commit.gpgsign false

commit() {
  local auteur="$1" courriel="$2" jour="$3" message="$4"
  git add certcheck.sh
  GIT_AUTHOR_NAME="$auteur" GIT_AUTHOR_EMAIL="$courriel" GIT_AUTHOR_DATE="$jour" \
  GIT_COMMITTER_NAME="$auteur" GIT_COMMITTER_EMAIL="$courriel" GIT_COMMITTER_DATE="$jour" \
    git commit -q -m "$message"
}

# 1. La première version : pas de rapport, pas de forge, openssl bavard.
python3 - "$final" > certcheck.sh <<'PY'
import re, sys
s = open(sys.argv[1]).read()
s = s.replace(' 2>/dev/null', '')
debut = s.index('ouvrir_ticket() {')
fin = s.index('if [ ! -f "$INVENTAIRE" ]')
s = s[:debut] + s[fin:]
s = re.sub(r'\n# Forge de l.equipe.*?\n\n', '\n\n', s, flags=re.S)
s = s.replace('\nif [ $((NB_ALERTE + NB_EXPIRE)) -gt 0 ]; then\n  if [ -n "${FORGE_TOKEN:-}" ]; then\n    ouvrir_ticket "$ALERTES"\n  else\n    echo "FORGE_TOKEN absent : pas de ticket ouvert."\n  fi\nfi\n', '\n')
s = s.replace('SEUIL=30', 'SEUIL=15')
s = re.sub(r'\njournal\(\) \{.*?\n\}\n', '\njournal() {\n  :\n}\n', s, flags=re.S)
s = s.replace('RAPPORT="certcheck-rapport.txt"\n', '')
sys.stdout.write(s)
PY
commit "Julien Marchand" "julien.marchand@exploitation.example" "2024-03-04T09:12:00+01:00" "certcheck : premier controle des certificats du parc"

# 2. Le rapport sur disque.
python3 - "$final" > certcheck.sh.new <<'PY'
import re, sys
s = open(sys.argv[1]).read()
s = s.replace(' 2>/dev/null', '')
debut = s.index('ouvrir_ticket() {')
fin = s.index('if [ ! -f "$INVENTAIRE" ]')
s = s[:debut] + s[fin:]
s = re.sub(r'\n# Forge de l.equipe.*?\n\n', '\n\n', s, flags=re.S)
s = s.replace('\nif [ $((NB_ALERTE + NB_EXPIRE)) -gt 0 ]; then\n  if [ -n "${FORGE_TOKEN:-}" ]; then\n    ouvrir_ticket "$ALERTES"\n  else\n    echo "FORGE_TOKEN absent : pas de ticket ouvert."\n  fi\nfi\n', '\n')
s = s.replace('SEUIL=30', 'SEUIL=15')
sys.stdout.write(s)
PY
mv certcheck.sh.new certcheck.sh
commit "Julien Marchand" "julien.marchand@exploitation.example" "2024-05-21T16:40:00+02:00" "ajoute le rapport certcheck-rapport.txt pour l'audit"

# 3. Le commit qui avale l'erreur d'openssl.
sed 's| -in "$cert")| -in "$cert" 2>/dev/null)|; s|-in "\$cert" |&|' certcheck.sh > certcheck.sh.new
python3 - certcheck.sh.new <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace('-noout -in "$cert" | cut', '-noout -in "$cert" 2>/dev/null | cut')
open(p, 'w').write(s)
PY
mv certcheck.sh.new certcheck.sh
commit "Karim Benali" "karim.benali@exploitation.example" "2025-01-14T08:05:00+01:00" "masque les messages d'openssl qui polluent les mails du cron"

# 4. La publication sur la forge.
python3 - "$final" > certcheck.sh <<'PY'
import sys
s = open(sys.argv[1]).read()
s = s.replace('SEUIL=30', 'SEUIL=15')
sys.stdout.write(s)
PY
commit "Karim Benali" "karim.benali@exploitation.example" "2025-06-02T11:30:00+02:00" "ouvre un ticket sur la forge quand des certificats sont a renouveler"

# 5. Le seuil passe à 30 jours.
cp "$final" certcheck.sh
commit "Julien Marchand" "julien.marchand@exploitation.example" "2025-09-08T10:00:00+02:00" "seuil a 30 jours, demande de l'equipe securite"

git bundle create -q "$sortie" HEAD main
echo "historique écrit : $sortie"
git log --format='%h %an %s'
