#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

if [[ ! -f .env ]]; then
  echo "Run deploy-conoha.sh before publishing JupyterLab." >&2
  exit 1
fi

jupyter_token="$(sed -n 's/^JUPYTER_TOKEN=//p' .env)"
if [[ -z "$jupyter_token" ]]; then
  echo "JUPYTER_TOKEN is missing from quantum_os/.env." >&2
  exit 1
fi

cloudflared_image="cloudflare/cloudflared@sha256:0aa26e284f05e6c77ae375b8c9c11d9eb6a448fb7bcd8d40f31cb6176189eb38"
docker pull "$cloudflared_image"
docker rm --force quantum-jupyter-tunnel >/dev/null 2>&1 || true
docker run --detach \
  --name quantum-jupyter-tunnel \
  --restart unless-stopped \
  --network quantum_os_default \
  "$cloudflared_image" \
  tunnel --no-autoupdate --url http://quantum-os:8888 >/dev/null

public_url=""
for attempt in {1..30}; do
  public_url="$(
    docker logs quantum-jupyter-tunnel 2>&1 \
      | grep -Eo 'https://[-a-z0-9]+\.trycloudflare\.com' \
      | tail -n 1 || true
  )"
  if [[ -n "$public_url" ]]; then
    break
  fi
  sleep 2
done

if [[ -z "$public_url" ]]; then
  echo "Cloudflare did not issue a public URL." >&2
  docker logs quantum-jupyter-tunnel >&2
  exit 1
fi

echo "JupyterLab public URL: $public_url/lab"
echo "Login token: $jupyter_token"
echo "This Quick Tunnel URL changes when the tunnel is recreated."
