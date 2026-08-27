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


class FusionScenario(BaseModel):
    name: str = Field(default="Baseline tokamak", min_length=1, max_length=100)
    temperature_kev: float = Field(default=15, ge=1, le=100)
    density_1e20_m3: float = Field(default=1.0, gt=0, le=10)
    confinement_time_s: float = Field(default=3.0, gt=0, le=100)
    magnetic_field_t: float = Field(default=5.3, gt=0, le=30)
    major_radius_m: float = Field(default=6.2, gt=0, le=30)
    minor_radius_m: float = Field(default=2.0, gt=0, le=10)
    elongation: float = Field(default=1.7, ge=1, le=3)
    external_heating_mw: float = Field(default=50, ge=0, le=1000)


class FusionAnalysisResponse(BaseModel):
    name: str
    volume_m3: float
    plasma_pressure_kpa: float
    beta_percent: float
    triple_product_kev_s_m3: float
    lawson_reference_ratio: float
    stored_energy_mj: float
    dt_reactivity_m3_s: float
    fusion_power_mw: float
    alpha_heating_mw: float
    transport_loss_mw: float
    plasma_gain_q: float | None
    net_heating_margin_mw: float
    diagnostics: list[str]
    assumptions: list[str]
    disclaimer: str


class FusionAssistantRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    scenario: FusionAnalysisResponse | None = None

    @field_validator("question")
    @classmethod
    def reject_blank_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value.strip()


class FusionAssistantResponse(BaseModel):
    answer: str
    model: str
