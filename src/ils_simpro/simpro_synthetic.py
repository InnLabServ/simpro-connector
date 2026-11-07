"""Offline-only Simpro-shaped job mapping with explicit identity evidence.

These models describe a narrow subset of supplied Swagger v1.0 job-detail fields.
They accept additional native fields but never infer an ILS job number from ID,
Name, OrderNo or deprecated RequestNo. No networking or file access.
"""

from collections.abc import Mapping
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, Strict, StrictInt, ValidationError, field_validator

from .models import JobSummary, Provenance, valid_identifier


class UnverifiedJobIdentityError(ValueError):
    """A provider job cannot be associated with a verified ILS job number."""


class VerifiedJobIdentity(BaseModel):
    """Explicit externally checked association; synthetic evidence only in public fixtures."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    company_id: Annotated[StrictInt, Field(ge=0)]
    provider_job_id: Annotated[StrictInt, Field(ge=1)]
    job_number: str = Field(min_length=1)
    evidence_source: str = Field(min_length=1)

    @field_validator("job_number", "evidence_source")
    @classmethod
    def validate_identity(cls, value: str) -> str:
        return valid_identifier(value)


class _SimproStatus(BaseModel):
    # Simpro Status is an object, not the Stage enum string.
    model_config = ConfigDict(extra="ignore", frozen=True)

    ID: Annotated[StrictInt, Field(ge=0)]
    Name: Annotated[str, Strict(), Field(min_length=1)]


class _SimproJobDetail(BaseModel):
    # The real job-detail response has many additional keys. Validate only
    # the fields used for this narrow offline projection.
    model_config = ConfigDict(extra="ignore", frozen=True)

    ID: Annotated[StrictInt, Field(ge=1)]
    Name: Annotated[str, Strict()] | None = None
    OrderNo: Annotated[str, Strict()] | None = None
    RequestNo: Annotated[str, Strict()] | None = None
    Stage: Annotated[str, Strict(), Field(min_length=1)] | None = None
    Status: _SimproStatus | None = None


def normalize_synthetic_simpro_job(
    payload: Mapping[str, object],
    *,
    company_id: int,
    identity: VerifiedJobIdentity | None,
) -> JobSummary:
    """Validate a fabricated Simpro detail and apply a separately verified identity.

    This is deliberately not a live Simpro client. It accepts neither an
    inferred ID-to-JN mapping nor an unchecked company identity.
    """
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    if type(company_id) is not int or company_id < 0:
        raise ValueError("company_id must be a non-negative integer")
    if identity is None:
        raise UnverifiedJobIdentityError("A verified provider-to-job identity is required")
    if not isinstance(identity, VerifiedJobIdentity):
        raise TypeError("identity must be a VerifiedJobIdentity")
    # model_copy(update=...) bypasses validation; reconstruct from fields.
    identity = VerifiedJobIdentity.model_validate(
        {
            "company_id": identity.company_id,
            "provider_job_id": identity.provider_job_id,
            "job_number": identity.job_number,
            "evidence_source": identity.evidence_source,
        }
    )
    # Deliberately validate before comparing ID or normalizing any fields.
    detail = _SimproJobDetail.model_validate(payload)
    if identity.company_id != company_id or identity.provider_job_id != detail.ID:
        raise UnverifiedJobIdentityError("Identity evidence does not match company and provider job ID")

    result = JobSummary(
        job_number=identity.job_number,
        company_id=str(company_id),
        administrative_stage_raw=detail.Stage,
        administrative_status_raw=detail.Status.Name if detail.Status is not None else None,
        administrative_closed=None,
        provenance=(
            Provenance(system="synthetic_simpro_job_detail", source_id=f"{company_id}/{detail.ID}"),
            Provenance(system="synthetic_identity_evidence", source_id=identity.evidence_source),
        ),
        unresolved=("Administrative closure and technical repair not established",),
    )
    return result
