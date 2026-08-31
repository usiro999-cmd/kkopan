from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from fastapi import status
from pydantic import BaseModel, Field

from satdrone_common.app import create_app

app = create_app("Imagery Service")


class Provider(StrEnum):
    sentinel_2 = "sentinel-2"
    landsat_9 = "landsat-9"
    custom = "custom"


class IngestScene(BaseModel):
    provider: Provider
    source_uri: str
    captured_at: datetime
    area_wkt: str = Field(description="Observation footprint in WKT")


class SceneAccepted(BaseModel):
    scene_id: UUID
    status: str


@app.post(
    "/api/v1/scenes",
    response_model=SceneAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["imagery"],
)
async def ingest_scene(scene: IngestScene) -> SceneAccepted:
    return SceneAccepted(scene_id=uuid4(), status="queued")

