"""Preserve unknowns and distinguish shipping from installation."""

from pydantic import ValidationError
import pytest

from ils_simpro.fixtures import sample_job
from ils_simpro.models import JobSummary, PartState


def test_synthetic_job_is_not_closed_or_installed() -> None:
    job = sample_job()
    assert job.administrative_closed is None
    assert job.parts[0].state is PartState.SHIPPED
    assert job.parts[0].state is not PartState.INSTALLED


def test_extra_fields_not_silently_accepted() -> None:
    with pytest.raises(ValidationError):
        JobSummary(job_number="DEMO", unsupported="value")
