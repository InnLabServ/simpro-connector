"""Adversarial, entirely synthetic tests for provider job normalization."""

import socket

import pytest
from pydantic import ValidationError

from ils_simpro.offline import OfflineJobRepository
from ils_simpro.simpro_synthetic import (
    UnverifiedJobIdentityError,
    VerifiedJobIdentity,
    normalize_synthetic_simpro_job,
)


def detail() -> dict[str, object]:
    return {
        "ID": 73,
        "Name": "An unrelated provider job name",
        "OrderNo": "PO-DEMO",
        "RequestNo": "Deprecated provider value",
        "Stage": "Progress",
        "Status": {"ID": 5, "Name": "Waiting for approval", "Color": "#00F"},
        "CompletedDate": None,
        "UnmodeledFutureField": {"expected": "additional native fields"},
    }


def verified() -> VerifiedJobIdentity:
    return VerifiedJobIdentity(
        company_id=0,
        provider_job_id=73,
        job_number="DEMO-73",
        evidence_source="fabricated-cross-check-73",
    )


def test_normalization_is_explicit_and_preserves_distinct_statuses() -> None:
    result = normalize_synthetic_simpro_job(detail(), company_id=0, identity=verified())
    assert result.job_number == "DEMO-73"
    assert result.company_id == "0"
    assert result.administrative_stage_raw == "Progress"
    assert result.administrative_status_raw == "Waiting for approval"
    assert result.administrative_closed is None
    assert result.operational_status is None
    assert result.parts == ()
    assert result.provenance[0].system == "synthetic_simpro_job_detail"
    assert result.provenance[0].source_id == "0/73"
    assert result.provenance[1].source_id == "fabricated-cross-check-73"
    assert "technical repair" in result.unresolved[0]
    assert OfflineJobRepository([result]).get_job("DEMO-73", company_id="0") == result


def test_provider_name_order_request_do_not_infer_job_number() -> None:
    payload = detail()
    payload.update({"Name": "JN73", "OrderNo": "JN73", "RequestNo": "JN73"})
    with pytest.raises(UnverifiedJobIdentityError):
        normalize_synthetic_simpro_job(payload, company_id=0, identity=None)


def test_provider_id_is_not_implicitly_converted_to_ils_number() -> None:
    payload = detail()
    payload["ID"] = 8465
    with pytest.raises(UnverifiedJobIdentityError):
        normalize_synthetic_simpro_job(payload, company_id=0, identity=verified())


@pytest.mark.parametrize("company", [1, 2])
def test_company_mismatch_fails_closed(company: int) -> None:
    with pytest.raises(UnverifiedJobIdentityError):
        normalize_synthetic_simpro_job(detail(), company_id=company, identity=verified())


@pytest.mark.parametrize("company", [True, False, -1, "0", None, 0.0])
def test_bad_company_scope_rejected(company: object) -> None:
    with pytest.raises(ValueError):
        normalize_synthetic_simpro_job(detail(), company_id=company, identity=verified())  # type: ignore[arg-type]


@pytest.mark.parametrize("bad_id", [None, True, "73", 73.0, -5, 0])
def test_invalid_provider_ids_rejected(bad_id: object) -> None:
    payload = detail()
    payload["ID"] = bad_id
    with pytest.raises(ValidationError):
        normalize_synthetic_simpro_job(payload, company_id=0, identity=verified())


@pytest.mark.parametrize("status", [False, "ready", 17, [], {"ID": "5", "Name": "Pending"}, {"ID": 5, "Name": 123}])
def test_malformed_status_rejected(status: object) -> None:
    payload = detail()
    payload["Status"] = status
    with pytest.raises(ValidationError):
        normalize_synthetic_simpro_job(payload, company_id=0, identity=verified())


def test_null_status_and_stage_preserve_unknown() -> None:
    payload = detail()
    payload["Status"] = None
    payload["Stage"] = None
    result = normalize_synthetic_simpro_job(payload, company_id=0, identity=verified())
    assert result.administrative_stage_raw is None
    assert result.administrative_status_raw is None
    assert result.administrative_closed is None


@pytest.mark.parametrize("stage", [3, False, [], {}])
def test_malformed_stage_rejected(stage: object) -> None:
    payload = detail()
    payload["Stage"] = stage
    with pytest.raises(ValidationError):
        normalize_synthetic_simpro_job(payload, company_id=0, identity=verified())


def test_future_stage_preserved_without_inventing_closure() -> None:
    payload = detail()
    payload["Stage"] = "FutureProviderStage"
    result = normalize_synthetic_simpro_job(payload, company_id=0, identity=verified())
    assert result.administrative_stage_raw == "FutureProviderStage"
    assert result.administrative_closed is None


@pytest.mark.parametrize("job_number", ["", " DEMO", "DEMO ", "DEMO\n"])
def test_evidence_rejects_malformed_job_numbers(job_number: str) -> None:
    with pytest.raises(ValidationError):
        VerifiedJobIdentity(
            company_id=0, provider_job_id=73, job_number=job_number, evidence_source="DEMO"
        )


@pytest.mark.parametrize("evidence", ["", " ", "evidence\n"])
def test_evidence_must_have_valid_source(evidence: str) -> None:
    with pytest.raises(ValidationError):
        VerifiedJobIdentity(
            company_id=0, provider_job_id=73, job_number="DEMO-73", evidence_source=evidence
        )


def test_mutated_unvalidated_identity_rejected() -> None:
    identity = verified().model_copy(update={"company_id": True})
    with pytest.raises(ValidationError):
        normalize_synthetic_simpro_job(detail(), company_id=0, identity=identity)


def test_extra_evidence_field_rejected() -> None:
    with pytest.raises(ValidationError):
        VerifiedJobIdentity(
            company_id=0,
            provider_job_id=73,
            job_number="DEMO-73",
            evidence_source="DEMO",
            unsupported="not-allowed",
        )


@pytest.mark.parametrize("payload", [None, [], "{}", 42])
def test_non_mapping_payload_rejected(payload: object) -> None:
    with pytest.raises(TypeError):
        normalize_synthetic_simpro_job(payload, company_id=0, identity=verified())  # type: ignore[arg-type]


def test_normalization_has_no_network_access(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Synthetic mapping attempted socket access")

    monkeypatch.setattr(socket.socket, "connect", deny)
    assert normalize_synthetic_simpro_job(detail(), company_id=0, identity=verified()).job_number == "DEMO-73"
