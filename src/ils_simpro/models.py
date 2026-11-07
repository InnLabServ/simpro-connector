"""Normalized models independent of any provider-specific response schema."""

import unicodedata
from enum import Enum
from typing import Annotated

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    Strict,
    StrictBool,
    StrictInt,
    field_validator,
)


def valid_identifier(value: str) -> str:
    """Reject blank, padded and control-containing source identities."""
    if not value or value != value.strip() or any(unicodedata.category(c)[0] == "C" for c in value):
        raise ValueError("Identifier must be nonblank, unpadded and contain no control characters")
    return value


class PartState(str, Enum):
    UNKNOWN = "unknown"
    REQUESTED = "requested"
    ORDERED = "ordered"
    SHIPPED = "shipped"
    RECEIVED = "received"
    INSTALLED = "installed"


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    system: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    observed_at: Annotated[AwareDatetime, Strict()] | None = None


class PartSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    part_number: str = Field(min_length=1)
    quantity: Annotated[StrictInt, Field(ge=1, le=1000000)]
    state: PartState = PartState.UNKNOWN


class JobSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    job_number: str = Field(min_length=1)
    company_id: str | None = None
    customer_name: str | None = None
    site_name: str | None = None
    instrument: str | None = None
    operational_status: str | None = None
    administrative_closed: StrictBool | None = None
    administrative_status_raw: str | None = None
    administrative_stage_raw: str | None = None
    parts: tuple[PartSummary, ...] = ()
    provenance: tuple[Provenance, ...] = Field(min_length=1)
    unresolved: tuple[str, ...] = ()

    @field_validator("job_number", "company_id")
    @classmethod
    def validate_identifiers(cls, value: str | None) -> str | None:
        return valid_identifier(value) if value is not None else None
