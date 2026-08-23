from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ScreeningRun(Base):
    __tablename__ = "screening_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    request_data: Mapped[dict] = mapped_column(JSON)
    result_data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class QuantumJobRecord(Base):
    __tablename__ = "quantum_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    azure_job_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    target: Mapped[str] = mapped_column(String(160))
    circuit: Mapped[str] = mapped_column(String(40))
    shots: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40))
    result_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
