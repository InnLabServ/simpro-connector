"""Synthetic job lookup validates source identities and never invokes networking."""

import socket

import pytest
from pydantic import ValidationError

from ils_simpro.fixtures import sample_job
from ils_simpro.models import JobSummary, Provenance
from ils_simpro.offline import AmbiguousJobError, JobNotFoundError, OfflineJobRepository


def test_exact_lookup_preserves_provenance_and_unknowns() -> None:
    result = OfflineJobRepository([sample_job()]).get_job("DEMO-1001")
    assert result.job_number == "DEMO-1001"
    assert result.administrative_closed is None
    assert result.provenance[0].system == "synthetic_fixture"
    assert result.unresolved == ("Delivery, installation and repair outcome not confirmed",)


def test_absent_job_is_typed_not_found() -> None:
    with pytest.raises(JobNotFoundError):
        OfflineJobRepository([sample_job()]).get_job("DEMO-OTHER")


def test_duplicate_identifier_without_scope_fails_closed() -> None:
    first = sample_job().model_copy(update={"company_id": "COMPANY-A"})
    second = sample_job().model_copy(update={"company_id": "COMPANY-B"})
    repo = OfflineJobRepository([first, second])
    with pytest.raises(AmbiguousJobError):
        repo.get_job("DEMO-1001")
    assert repo.get_job("DEMO-1001", company_id="COMPANY-B").company_id == "COMPANY-B"


def test_normalized_identity_collision_rejected_on_ingest() -> None:
    other = sample_job().model_copy(update={"job_number": "demo-1001"})
    with pytest.raises(AmbiguousJobError):
        OfflineJobRepository([sample_job(), other])


@pytest.mark.parametrize("invalid", ["", " ", " DEMO-1001", "DEMO-1001 ", "\x00DEMO"])
def test_invalid_lookup_identifier_is_rejected(invalid: str) -> None:
    with pytest.raises(ValueError):
        OfflineJobRepository([sample_job()]).get_job(invalid)


@pytest.mark.parametrize("invalid", [1001, b"DEMO-1001", None])
def test_non_string_lookup_is_rejected(invalid: object) -> None:
    with pytest.raises(TypeError):
        OfflineJobRepository([sample_job()]).get_job(invalid)


def test_invalid_input_records_fail_closed() -> None:
    with pytest.raises(TypeError):
        OfflineJobRepository([{"job_number": "DEMO"}])
    with pytest.raises(TypeError):
        OfflineJobRepository("DEMO")
    invalid = sample_job().model_copy(update={"administrative_closed": "maybe"})
    # model_copy(update=...) intentionally bypasses validation. Pydantic warns
    # while serializing the invalid model before ingestion rejects it.
    with pytest.warns(UserWarning, match="Pydantic serializer warnings"):
        with pytest.raises(ValidationError):
            OfflineJobRepository([invalid])


def test_frozen_models_and_nested_collections() -> None:
    job = sample_job()
    with pytest.raises(ValidationError):
        job.customer_name = "changed"
    assert isinstance(job.parts, tuple)
    assert isinstance(job.provenance, tuple)


def test_no_inferred_operational_status_for_unpopulated_record() -> None:
    result = OfflineJobRepository([
        JobSummary(
            job_number="DEMO-EMPTY",
            provenance=(Provenance(system="synthetic_fixture", source_id="empty"),),
        )
    ]).get_job("DEMO-EMPTY")
    assert result.operational_status is None
    assert result.administrative_closed is None
    assert result.parts == ()


def test_offline_lookup_never_opens_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Offline lookup attempted socket access")

    monkeypatch.setattr(socket.socket, "connect", deny)
    assert OfflineJobRepository([sample_job()]).get_job("DEMO-1001").job_number == "DEMO-1001"


def test_repository_requires_provenance() -> None:
    with pytest.raises(ValidationError):
        JobSummary(job_number="DEMO")


def test_stored_identity_rejects_padding_and_controls() -> None:
    for invalid in ("  ", " DEMO", "DEMO\n"):
        with pytest.raises(ValidationError):
            JobSummary(job_number=invalid, provenance=(Provenance(system="synthetic", source_id="1"),))
