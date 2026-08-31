from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, BaseModel

from satdrone_common.app import create_app

app = create_app("Stream Service")


class Protocol(StrEnum):
    webrtc = "webrtc"
    hls = "hls"


class StreamRequest(BaseModel):
    drone_id: UUID
    source_uri: str
    output_protocol: Protocol = Protocol.webrtc


class StreamSession(BaseModel):
    session_id: UUID
    playback_url: AnyHttpUrl
    status: str


@app.post("/api/v1/streams", response_model=StreamSession, tags=["streaming"])
async def create_stream(request: StreamRequest) -> StreamSession:
    session_id = uuid4()
    extension = "whep" if request.output_protocol == Protocol.webrtc else "index.m3u8"
    return StreamSession(
        session_id=session_id,
        playback_url=f"http://localhost:8889/{session_id}/{extension}",
        status="starting",
    )

