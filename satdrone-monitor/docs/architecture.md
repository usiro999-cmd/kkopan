# Architecture

## Principles

- Domain services own their data and publish versioned events.
- The API gateway is the only browser-facing backend.
- Commands that can move an aircraft require explicit safety approval.
- Satellite files and video segments belong in object storage; PostgreSQL
  stores metadata and PostGIS geometry.
- Work that may take more than an HTTP request is queued through RabbitMQ.
- Redis is reserved for ephemeral state, rate limits, and current telemetry.
- Every request and event carries a correlation identifier.

## Service boundaries

| Service | Responsibility | Persistent data |
| --- | --- | --- |
| API gateway | Authentication boundary, aggregation, rate limiting | None |
| Imagery | Provider adapters, scene catalog, geospatial footprints | PostGIS |
| Inference | YOLO/PyTorch workers, model registry, detections | PostGIS/object storage |
| Mission | Route planning, approvals, mission state machine | PostgreSQL/PostGIS |
| Drone | MAVSDK/MAVLink adapters and live vehicle state | Redis/PostgreSQL audit |
| Stream | RTSP ingest and WebRTC/HLS session lifecycle | Redis/object storage |

The repository currently supplies synchronous API boundaries and event
contracts. Provider-specific satellite clients, model weights, object storage,
and physical aircraft adapters are intentionally left behind explicit service
boundaries. This keeps local development safe and prevents vendor coupling.

## Primary flow

1. Imagery records a satellite scene and emits `scene.ingested.v1`.
2. Inference consumes the event, runs the configured model, stores detections,
   and emits `anomaly.detected.v1`.
3. Mission applies policy, terrain, weather, range, and geofence constraints.
4. An authorized operator approves the resulting mission.
5. Drone performs preflight checks and submits MAVSDK commands.
6. Telemetry and stream session updates are delivered to the dashboard.

## Production topology

Run stateless services as separate Kubernetes Deployments. Inference workers
should use a dedicated GPU node pool and must not share a pod with public APIs.
Use managed PostgreSQL/PostGIS, Redis, RabbitMQ, and S3-compatible object
storage where available. The manifests under `infra/kubernetes/base` are a
deployment baseline, not a substitute for a production secret manager,
database operator, ingress controller, network policy, backup policy, or
observability stack.

## Security and flight safety

- Integrate an OIDC provider at the gateway and use short-lived tokens.
- Apply organization and site authorization to every domain resource.
- Encrypt service traffic, databases, queues, and object storage.
- Store an immutable audit trail for approvals and aircraft commands.
- Require geofence, battery, GNSS, weather, connectivity, and airspace checks.
- Provide hardware and software return-to-launch and operator override paths.
- Never expose MAVLink endpoints directly to a public network.

## Delivery roadmap

1. Persistence schemas, migrations, OIDC, and the transactional outbox.
2. Satellite provider and S3-compatible object-storage adapters.
3. Isolated GPU inference worker with model provenance and evaluation.
4. Mission state machine, geofence engine, and approval workflow.
5. PX4/ArduPilot simulation-in-the-loop before physical flight adapters.
6. WebSocket telemetry, a media gateway, and WebRTC/HLS playback.
7. OpenTelemetry, metrics, alerting, backups, and disaster recovery testing.

