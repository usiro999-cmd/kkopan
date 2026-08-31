from datetime import datetime
from uuid import UUID, uuid4

from fastapi import status
from pydantic import BaseModel, Field

from satdrone_common.app import create_app

app = create_app("Mission Service")


class Coordinate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude_m: float = Field(gt=0, le=120)


class MissionPlan(BaseModel):
    anomaly_id: UUID
    drone_id: UUID
    waypoints: list[Coordinate] = Field(min_length=2)
    not_before: datetime | None = None


@app.post("/api/v1/missions", status_code=status.HTTP_201_CREATED, tags=["missions"])
async def create_mission(plan: MissionPlan) -> dict[str, str | UUID]:
    return {"mission_id": uuid4(), "status": "draft", "drone_id": plan.drone_id}

