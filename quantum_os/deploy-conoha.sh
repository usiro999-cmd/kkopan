#!/usr/bin/env bash
set -euo pipefail

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
  jupyter_token="$(openssl rand -hex 32)"
  postgres_password="$(openssl rand -hex 24)"
  updater_password="$(openssl rand -hex 24)"
  docker_gid="$(stat -c '%g' /var/run/docker.sock)"
  umask 077
  cat >.env <<EOF
JUPYTER_TOKEN=$jupyter_token
JUPYTER_PORT=8888
JUPYTER_BIND=127.0.0.1
QUANTUM_UID=1000
QUANTUM_GID=1000
QUANTUM_OS_IMAGE=multiverse-quantum-os:ubuntu-24.04
POSTGRES_DB=quantum_research
POSTGRES_USER=quantum
POSTGRES_PASSWORD=$postgres_password
UPDATER_PORT=9090
UPDATER_BIND=127.0.0.1
UPDATE_ADMIN_PASSWORD=$updater_password
DOCKER_GID=$docker_gid
EOF
  echo "Created protected credentials in quantum_os/.env."
else
  echo "Keeping the existing quantum_os/.env."
  jupyter_token="$(sed -n 's/^JUPYTER_TOKEN=//p' .env)"
fi

if [[ -z "$jupyter_token" ]]; then
  echo "JUPYTER_TOKEN is missing from quantum_os/.env." >&2
  exit 1
fi

docker compose -f compose.yml up --build -d research-db quantum-os

for attempt in {1..60}; do
  if curl --fail --silent \
    "http://127.0.0.1:8888/api/status?token=$jupyter_token" >/dev/null; then
    docker compose -f compose.yml run --rm --entrypoint quantum-info quantum-os
    echo "Science stack and PostgreSQL are healthy."
    echo "Jupyter token is stored in /opt/kkopan/quantum_os/.env."
    exit 0
  fi
  sleep 3
done

echo "Quantum OS did not become healthy in time." >&2
docker compose -f compose.yml ps
exit 1
