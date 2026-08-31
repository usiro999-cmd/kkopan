# SatDrone Monitor OSS

SatDrone Monitor is an Apache-2.0 platform for turning satellite observations
into verified field intelligence. It combines imagery ingestion, AI anomaly
detection, autonomous drone missions, live telemetry, and video monitoring.

## Repository layout

```text
apps/web/                 React operations dashboard
services/api-gateway/     Public API and system aggregation
services/imagery/         Satellite scene ingestion and catalog
services/inference/       AI detection job orchestration
services/mission/         Mission planning and lifecycle
services/drone/           MAVSDK adapter boundary
services/stream/          RTSP/WebRTC/HLS session management
services/common/          Shared FastAPI runtime and contracts
contracts/                Event definitions
infra/kubernetes/         Kubernetes baseline manifests
docs/                     Architecture and operating documentation
```

## Quick start

Requirements: Docker Engine with Compose v2 and GNU Make.

```bash
cp .env.example .env
docker compose up --build
```

Open the dashboard at <http://localhost:5173>. The API gateway is available at
<http://localhost:8000/docs>. Service health is reported at `/health/live` and
dependency readiness at `/health/ready`.

The included credentials are development-only. Change all secrets before
deploying outside a local machine.

## Development

```bash
make bootstrap
make test
make validate
```

See [the architecture guide](docs/architecture.md) for service boundaries,
data flow, deployment guidance, and the path from this foundation to a
production installation.

## Safety

Drone commands are never issued directly by the browser. Production adapters
must enforce geofences, authorization, preflight validation, operator override,
and jurisdiction-specific aviation requirements. The initial drone service is
a safe simulation boundary and does not connect to an aircraft.

## License

Copyright 2026 SatDrone Monitor contributors.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

