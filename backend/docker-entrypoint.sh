#!/bin/sh
set -e

CERTFILE=${SSL_CERTFILE:-/app/backend/certs/cert.pem}
KEYFILE=${SSL_KEYFILE:-/app/backend/certs/key.pem}

if [ ! -f "$CERTFILE" ] || [ ! -f "$KEYFILE" ]; then
  echo "Erreur : le certificat ou la clé est introuvable."
  echo "Vérifiez que backend/certs/cert.pem et backend/certs/key.pem existent."
  exit 1
fi

exec uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-certfile "$CERTFILE" \
  --ssl-keyfile "$KEYFILE"
