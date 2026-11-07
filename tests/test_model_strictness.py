"""Guard against silently coercing unverified administrative facts."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from ils_simpro.models import JobSummary, PartSummary, Provenance


def _source() -> tuple[Provenance, ...]:
    return (Provenance(system="synthetic_fixture", source_id="demo"),)


@pytest.mark.parametrize("value", ["yes", "false", 1, 0, 1.0])
def test_administrative_status_requires_strict_bool(value: object) -> None:
    with pytest.raises(ValidationError):
        JobSummary(job_number="DEMO", provenance=_source(), administrative_closed=value)


@pytest.mark.parametrize("value", ["3", True, 0, 1000001])
def test_part_quantity_requires_bounded_integer(value: object) -> None:
    with pytest.raises(ValidationError):
        PartSummary(part_number="DEMO-PART", quantity=value)


@pytest.mark.parametrize("value", [0, "0", datetime(2026, 1, 1)])
def test_provenance_requires_aware_datetime(value: object) -> None:
    with pytest.raises(ValidationError):
        Provenance(system="synthetic_fixture", source_id="demo", observed_at=value)


def test_provenance_accepts_aware_datetime() -> None:
    record = Provenance(
        system="synthetic_fixture",
        source_id="demo",
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert record.observed_at is not None
