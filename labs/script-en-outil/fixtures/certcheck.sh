#!/usr/bin/env bash
#
# certcheck.sh - controle d'expiration des certificats du parc
#
# Lance chaque nuit par cron sur la machine d'admin :
#   30 6 * * * cd /opt/certcheck && ./certcheck.sh inventaire.txt
#
# Lit l'inventaire (hote + chemin du certificat collecte), affiche l'etat de
# chaque certificat, ecrit un rapport, et ouvre un ticket sur la forge quand
# des certificats sont a renouveler.
#
# Historique : ecrit par Julien en 2024, repris par l'equipe exploitation.
# Ne pas toucher a la partie forge sans prevenir Karim.

set -u

INVENTAIRE="${1:-/etc/certcheck/inventaire.txt}"
SEUIL=30
RAPPORT="certcheck-rapport.txt"

# Forge de l'equipe (Forgejo). Le jeton vient de l'environnement du cron.
FORGE_URL="${FORGE_URL:-https://forge.lab.example}"
FORGE_REPO="${FORGE_REPO:-exploitation/certificats}"

NB_OK=0
NB_ALERTE=0
NB_EXPIRE=0
ALERTES=""

maintenant() {
  date +%s
}

# Renvoie la date d'expiration du certificat, en secondes depuis l'epoque.
expiration() {
  local cert="$1"
  local fin
  fin=$(openssl x509 -enddate -noout -in "$cert" 2>/dev/null | cut -d= -f2)
  date -d "$fin" +%s
}

# Nombre de jours entiers avant l'expiration (negatif si deja expire).
jours_restants() {
  local cert="$1"
  local fin
  fin=$(expiration "$cert")
  echo $(( (fin - $(maintenant)) / 86400 ))
}

journal() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$RAPPORT"
}

verifier_un() {
  local hote="$1"
  local cert="$2"
  local jours

  jours=$(jours_restants "$cert")

  if [ "$jours" -lt 0 ]; then
    echo "EXPIRE  $hote (depuis $(( -jours )) jours)"
    journal "EXPIRE $hote $jours"
    NB_EXPIRE=$((NB_EXPIRE + 1))
    ALERTES="${ALERTES}- ${hote} : expire depuis $(( -jours )) jours\n"
  elif [ "$jours" -le "$SEUIL" ]; then
    echo "ALERTE  $hote expire dans $jours jours"
    journal "ALERTE $hote $jours"
    NB_ALERTE=$((NB_ALERTE + 1))
    ALERTES="${ALERTES}- ${hote} : expire dans ${jours} jours\n"
  else
    echo "OK      $hote ($jours jours)"
    journal "OK $hote $jours"
    NB_OK=$((NB_OK + 1))
  fi
}

ouvrir_ticket() {
  local corps="$1"
  local url="${FORGE_URL}/api/v1/repos/${FORGE_REPO}/issues?access_token=${FORGE_TOKEN}"

  echo "Appel de la forge : POST $url"
  journal "POST $url"

  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Certificats a renouveler\", \"body\": \"${corps}\"}" \
    "$url" > /dev/null
}

if [ ! -f "$INVENTAIRE" ]; then
  echo "Inventaire introuvable : $INVENTAIRE" >&2
  exit 1
fi

journal "debut du controle ($INVENTAIRE)"

while read -r hote cert; do
  # lignes vides et commentaires
  if [ -z "$hote" ]; then
    continue
  fi
  case "$hote" in
    \#*) continue ;;
  esac

  # le chemin du certificat est relatif au dossier de l'inventaire
  case "$cert" in
    /*) ;;
    *) cert="$(dirname "$INVENTAIRE")/$cert" ;;
  esac

  verifier_un "$hote" "$cert"
done < "$INVENTAIRE"

echo
echo "Resume : $NB_OK ok, $NB_ALERTE a renouveler, $NB_EXPIRE expires"
journal "fin : $NB_OK ok, $NB_ALERTE alertes, $NB_EXPIRE expires"

if [ $((NB_ALERTE + NB_EXPIRE)) -gt 0 ]; then
  if [ -n "${FORGE_TOKEN:-}" ]; then
    ouvrir_ticket "$ALERTES"
  else
    echo "FORGE_TOKEN absent : pas de ticket ouvert."
  fi
fi

exit 0
