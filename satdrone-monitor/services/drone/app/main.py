from enum import StrEnum
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel

from satdrone_common.app import create_app

app = create_app("Drone Service")


class Command(StrEnum):
    arm = "arm"
    launch = "launch"
    pause = "pause"
    return_to_launch = "return-to-launch"


class DroneCommand(BaseModel):
    mission_id: UUID
    command: Command
    operator_id: UUID
    safety_approved: bool = False


@app.post("/api/v1/drones/{drone_id}/commands", tags=["drones"])
async def command_drone(drone_id: UUID, command: DroneCommand) -> dict[str, str | UUID]:
    if not command.safety_approved:
        raise HTTPException(status_code=409, detail="Safety approval is required")
    return {"drone_id": drone_id, "status": "accepted", "command": command.command}

