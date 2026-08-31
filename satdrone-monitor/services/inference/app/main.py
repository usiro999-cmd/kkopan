from enum import StrEnum
from uuid import UUID, uuid4

from fastapi import status
from pydantic import BaseModel, Field

from satdrone_common.app import create_app

app = create_app("Inference Service")


class DetectionModel(StrEnum):
    solar_defect = "solar-defect"
    crop_stress = "crop-stress"
    disaster_damage = "disaster-damage"
    intrusion = "intrusion"


class InferenceRequest(BaseModel):
    scene_id: UUID
    model: DetectionModel
    confidence_threshold: float = Field(default=0.6, ge=0, le=1)


@app.post("/api/v1/jobs", status_code=status.HTTP_202_ACCEPTED, tags=["inference"])
async def create_job(request: InferenceRequest) -> dict[str, str | UUID]:
    return {"job_id": uuid4(), "status": "queued", "model": request.model}

