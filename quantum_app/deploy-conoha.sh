#!/usr/bin/env bash
set -euo pipefail

PUBLIC_ORIGIN="${1:-http://163.44.125.29}"
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

for command in docker openssl curl; do
  if ! command -v "$command" >/dev/null; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 is required." >&2
  exit 1
fi

if [[ ! -f .env ]]; then
  database_password="$(openssl rand -hex 24)"
  umask 077
  cat >.env <<EOF
POSTGRES_DB=multiverse
POSTGRES_USER=multiverse
POSTGRES_PASSWORD=$database_password
PUBLIC_API_URL=
CORS_ORIGINS=["$PUBLIC_ORIGIN"]
API_BIND=127.0.0.1
API_PORT=8000
WEB_BIND=0.0.0.0
WEB_PORT=80
EOF
  echo "Created a protected .env file."
else
  echo "Keeping the existing .env file."
fi

docker compose up --build -d

for attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null \
    && curl --fail --silent http://127.0.0.1/fusion >/dev/null; then
    echo "Deployment is healthy: $PUBLIC_ORIGIN/fusion"
    exit 0
  fi
  sleep 2
done

echo "Deployment did not become healthy in time." >&2
docker compose ps
exit 1
