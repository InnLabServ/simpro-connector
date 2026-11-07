"""Normalized models independent of any provider-specific response schema."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PartState(str, Enum):
    UNKNOWN = "unknown"
    REQUESTED = "requested"
    ORDERED = "ordered"
    SHIPPED = "shipped"
    RECEIVED = "received"
    INSTALLED = "installed"


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system: str
    source_id: str
    observed_at: datetime | None = None


class PartSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    part_number: str
    quantity: int = Field(ge=1)
    state: PartState = PartState.UNKNOWN


class JobSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_number: str = Field(min_length=1)
    customer_name: str | None = None
    site_name: str | None = None
    instrument: str | None = None
    operational_status: str | None = None
    administrative_closed: bool | None = None
    parts: list[PartSummary] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
    unresolved: list[str] = Field(default_factory=list)
