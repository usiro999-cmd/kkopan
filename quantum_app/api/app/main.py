import asyncio
import logging
from contextlib import asynccontextmanager

from azure.core.exceptions import AzureError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from qiskit.exceptions import QiskitError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import Base, engine, get_session
from app.models import QuantumJobRecord, ScreeningRun
from app.schemas import (
    FusionAnalysisResponse,
    FusionAssistantRequest,
    FusionAssistantResponse,
    FusionScenario,
    QuantumConnectionStatus,
    QuantumJobRequest,
    QuantumJobResponse,
    QuantumTarget,
    ScreeningSummary,
    TutorRequest,
    TutorResponse,
    TwinScreeningRequest,
    TwinScreeningResponse,
)
from app.services.azure_quantum import (
    AzureQuantumConfigurationError,
    get_quantum_gateway,
    quantum_is_configured,
    valid_resource_id,
)
from app.services.screening import DISCLAIMER, screen_twin
from app.services.fusion import FusionInputs, analyze_plasma
from app.services.fusion_assistant import ask_fusion_assistant
from app.services.tutor import AIConfigurationError, ask_tutor


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Multiverse Quantum AI Academy API",
    version="2.0.0",
    lifespan=lifespan,
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/fusion/analyze", response_model=FusionAnalysisResponse)
async def analyze_fusion_scenario(
    request: FusionScenario,
) -> FusionAnalysisResponse:
    result = await asyncio.to_thread(
        analyze_plasma,
        FusionInputs(
            temperature_kev=request.temperature_kev,
            density_1e20_m3=request.density_1e20_m3,
            confinement_time_s=request.confinement_time_s,
            magnetic_field_t=request.magnetic_field_t,
            major_radius_m=request.major_radius_m,
            minor_radius_m=request.minor_radius_m,
            elongation=request.elongation,
            external_heating_mw=request.external_heating_mw,
        ),
    )
    return FusionAnalysisResponse(name=request.name, **result)


@app.post(
    "/api/v1/fusion/assistant",
    response_model=FusionAssistantResponse,
)
async def fusion_assistant(
    request: FusionAssistantRequest,
) -> FusionAssistantResponse:
    try:
        answer = await ask_fusion_assistant(
            request.question,
            request.scenario.model_dump() if request.scenario else None,
            settings,
        )
    except AIConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return FusionAssistantResponse(
        answer=answer, model=settings.azure_openai_deployment
    )


@app.post(
    "/api/v1/screenings",
    response_model=TwinScreeningResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_screening(
    request: TwinScreeningRequest,
    session: AsyncSession = Depends(get_session),
) -> TwinScreeningResponse:
    result = await asyncio.to_thread(
        screen_twin,
        request.alpha.profile.as_tuple(),
        request.beta.profile.as_tuple(),
        request.alpha.safety_weight,
        request.beta.safety_weight,
    )
    record = ScreeningRun(
        name=request.name,
        request_data=request.model_dump(by_alias=True),
        result_data=result,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return TwinScreeningResponse(
        id=record.id,
        created_at=record.created_at,
        disclaimer=DISCLAIMER,
        **result,
    )


@app.get("/api/v1/screenings", response_model=list[ScreeningSummary])
async def list_screenings(
    session: AsyncSession = Depends(get_session),
) -> list[ScreeningSummary]:
    records = (
        await session.scalars(
            select(ScreeningRun).order_by(ScreeningRun.created_at.desc()).limit(50)
        )
    ).all()
    return [
        ScreeningSummary(id=item.id, name=item.name, created_at=item.created_at)
        for item in records
    ]


@app.post("/api/v1/tutor", response_model=TutorResponse)
async def tutor(
    request: TutorRequest,
    session: AsyncSession = Depends(get_session),
) -> TutorResponse:
    context = None
    if request.screening_id is not None:
        record = await session.get(ScreeningRun, request.screening_id)
        if record is None:
            raise HTTPException(status_code=404, detail="screening not found")
        context = record.result_data
    try:
        answer = await ask_tutor(request.question, context, settings)
    except AIConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return TutorResponse(answer=answer, model=settings.azure_openai_deployment)


@app.get("/api/v1/quantum/status", response_model=QuantumConnectionStatus)
async def quantum_status() -> QuantumConnectionStatus:
    workspace_name = (
        settings.azure_quantum_resource_id.rstrip("/").rsplit("/", 1)[-1]
        if valid_resource_id(settings.azure_quantum_resource_id)
        else None
    )
    return QuantumConnectionStatus(
        configured=quantum_is_configured(settings),
        workspace_name=workspace_name,
        default_target=settings.azure_quantum_default_target or None,
    )


@app.get("/api/v1/quantum/targets", response_model=list[QuantumTarget])
async def quantum_targets() -> list[QuantumTarget]:
    if not quantum_is_configured(settings):
        raise HTTPException(
            status_code=503,
            detail="Azure Quantum workspace is not configured.",
        )
    try:
        return await asyncio.to_thread(get_quantum_gateway().list_targets)
    except AzureQuantumConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (AzureError, QiskitError, RuntimeError, ValueError) as error:
        logger.exception("Azure Quantum target discovery failed")
        raise HTTPException(
            status_code=502, detail="Azure Quantum target discovery failed."
        ) from error


@app.post(
    "/api/v1/quantum/jobs",
    response_model=QuantumJobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_quantum_job(
    request: QuantumJobRequest,
    session: AsyncSession = Depends(get_session),
) -> QuantumJobResponse:
    if not quantum_is_configured(settings):
        raise HTTPException(
            status_code=503,
            detail="Azure Quantum workspace is not configured.",
        )
    try:
        job = await asyncio.to_thread(
            get_quantum_gateway().submit_bell, request.target, request.shots
        )
        job_status = job.status().name
    except AzureQuantumConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (AzureError, QiskitError, RuntimeError, ValueError) as error:
        logger.exception("Azure Quantum job submission failed")
        raise HTTPException(
            status_code=502, detail="Azure Quantum job submission failed."
        ) from error

    record = QuantumJobRecord(
        azure_job_id=job.job_id(),
        target=request.target,
        circuit=request.circuit,
        shots=request.shots,
        status=job_status,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return QuantumJobResponse(
        id=record.id,
        azure_job_id=record.azure_job_id,
        target=record.target,
        circuit=record.circuit,
        shots=record.shots,
        status=record.status,
        created_at=record.created_at,
    )


@app.get(
    "/api/v1/quantum/jobs/{record_id}",
    response_model=QuantumJobResponse,
)
async def get_quantum_job(
    record_id: int,
    session: AsyncSession = Depends(get_session),
) -> QuantumJobResponse:
    record = await session.get(QuantumJobRecord, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="quantum job not found")
    try:
        job = await asyncio.to_thread(
            get_quantum_gateway().get_job, record.azure_job_id
        )
        current_status = job.status().name
        counts = None
        if current_status == "DONE":
            result = await asyncio.to_thread(job.result)
            counts = {
                str(outcome): int(count)
                for outcome, count in result.get_counts().items()
            }
        record.status = current_status
        record.result_data = counts
        await session.commit()
    except AzureQuantumConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (AzureError, QiskitError, RuntimeError, ValueError) as error:
        logger.exception("Azure Quantum job retrieval failed")
        raise HTTPException(
            status_code=502, detail="Azure Quantum job retrieval failed."
        ) from error
    return QuantumJobResponse(
        id=record.id,
        azure_job_id=record.azure_job_id,
        target=record.target,
        circuit=record.circuit,
        shots=record.shots,
        status=record.status,
        counts=record.result_data,
        created_at=record.created_at,
    )
