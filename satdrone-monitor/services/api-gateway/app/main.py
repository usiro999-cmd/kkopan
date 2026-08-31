import asyncio

import httpx
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from satdrone_common.app import create_app

app = create_app("API Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
)

SERVICES = {
    "imagery": "http://imagery:8080",
    "inference": "http://inference:8080",
    "mission": "http://mission:8080",
    "drone": "http://drone:8080",
    "stream": "http://stream:8080",
}


async def service_health(
    client: httpx.AsyncClient, name: str, url: str
) -> tuple[str, str]:
    try:
        response = await client.get(f"{url}/health/live")
        response.raise_for_status()
    except httpx.HTTPError:
        return name, "unavailable"
    return name, "operational"


@app.get("/api/v1/system/status", tags=["system"])
async def system_status() -> dict[str, object]:
    async with httpx.AsyncClient(timeout=2) as client:
        checks = await asyncio.gather(
            *(service_health(client, name, url) for name, url in SERVICES.items())
        )
    statuses = dict(checks)
    if all(status == "unavailable" for status in statuses.values()):
        raise HTTPException(status_code=503, detail={"services": statuses})
    return {"status": "operational", "services": statuses}
