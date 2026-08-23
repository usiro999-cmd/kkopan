from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field, field_validator


TARGETS = ("D2", "5-HT2A", "NMDA", "M1")


class TargetProfile(BaseModel):
    D2: float = Field(ge=0, le=1)
    serotonin_2a: float = Field(alias="5-HT2A", ge=0, le=1)
    NMDA: float = Field(ge=0, le=1)
    M1: float = Field(ge=0, le=1)

    model_config = {"populate_by_name": True}

    def as_tuple(self) -> tuple[float, ...]:
        return (self.D2, self.serotonin_2a, self.NMDA, self.M1)


class ScreeningCondition(BaseModel):
    profile: TargetProfile
    safety_weight: float = Field(default=0.35, ge=0, le=1)


class TwinScreeningRequest(BaseModel):
    name: str = Field(default="Graduate twin experiment", min_length=1, max_length=120)
    alpha: ScreeningCondition
    beta: ScreeningCondition


class MolecularDescriptors(BaseModel):
    molecular_weight: float
    log_p: float
    h_bond_donors: int
    polar_surface_area: float


class Explanation(BaseModel):
    target_fit: float
    quantum_fidelity: float
    molecular_suitability: float
    safety: float


class CandidateResult(BaseModel):
    id: str
    rank: int
    score: float
    quantum_fidelity: float
    descriptors: MolecularDescriptors
    explanation: Explanation


class ConditionResult(BaseModel):
    candidates: list[CandidateResult]


class ComparisonResult(BaseModel):
    spearman_rho: float
    same_leader: bool


class TwinScreeningResponse(BaseModel):
    id: int
    alpha: ConditionResult
    beta: ConditionResult
    comparison: ComparisonResult
    created_at: datetime
    disclaimer: str


class ScreeningSummary(BaseModel):
    id: int
    name: str
    created_at: datetime


class TutorRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    screening_id: int | None = None

    @field_validator("question")
    @classmethod
    def reject_empty_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value.strip()


class TutorResponse(BaseModel):
    answer: str
    model: str


class QuantumConnectionStatus(BaseModel):
    configured: bool
    provider: str = "Azure Quantum"
    workspace_name: str | None = None
    default_target: str | None = None


class QuantumTarget(BaseModel):
    name: str
    description: str | None = None


class QuantumJobRequest(BaseModel):
    target: str = Field(min_length=1, max_length=160)
    circuit: Literal["bell"] = "bell"
    shots: int = Field(default=100, ge=1, le=10_000)


class QuantumJobResponse(BaseModel):
    id: int
    azure_job_id: str
    target: str
    circuit: str
    shots: int
    status: str
    counts: dict[str, int] | None = None
    created_at: datetime
