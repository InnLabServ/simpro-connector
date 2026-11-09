"""Adversarial offline pagination and identity lookup, without native API access."""

import socket
import subprocess
import sys
from pathlib import Path

import pytest

from ils_simpro.offline_paging import (
    AmbiguousProviderIdentityError,
    IncompleteProviderPagesError,
    ProviderJobNotFoundError,
    SyntheticJobPage,
    enumerate_provider_job_ids,
    lookup_synthetic_job,
)
from ils_simpro.simpro_synthetic import UnverifiedJobIdentityError, VerifiedJobIdentity


def page(number: int = 1, total: int = 2, count: int = 2, ids: tuple[int, ...] = (41,)) -> SyntheticJobPage:
    return SyntheticJobPage(number, total, count, tuple({"ID": value} for value in ids))


def pages() -> tuple[SyntheticJobPage, ...]:
    return page(), page(2, ids=(42,))


def identity(job_number: str = "DEMO-42", provider_id: int = 42, company_id: int = 0) -> VerifiedJobIdentity:
    return VerifiedJobIdentity(
        job_number=job_number,
        provider_job_id=provider_id,
        company_id=company_id,
        evidence_source="fabricated-external-identity",
    )


def detail(provider_id: int = 42) -> dict[str, object]:
    return {"ID": provider_id, "Stage": "Complete", "Status": {"ID": 5, "Name": "Closed"}}


def run_lookup(
    *,
    sequence: tuple[SyntheticJobPage, ...] | None = None,
    claims: tuple[VerifiedJobIdentity, ...] | None = None,
    details: dict[int, dict[str, object]] | None = None,
    company_id: int = 0,
):
    return lookup_synthetic_job(
        "DEMO-42",
        company_id=company_id,
        pages=pages() if sequence is None else sequence,
        identities=(identity(),) if claims is None else claims,
        details_by_id={42: detail()} if details is None else details,
    )


def test_complete_scoped_lookup_does_not_infer_closure() -> None:
    result = run_lookup()
    assert result.job_number == "DEMO-42"
    assert result.company_id == "0"
    assert result.administrative_stage_raw == "Complete"
    assert result.administrative_status_raw == "Closed"
    assert result.administrative_closed is None
    assert result.operational_status is None
    assert enumerate_provider_job_ids(pages()) == (41, 42)


def test_complete_empty_snapshot_is_supported_but_not_matched() -> None:
    empty = (SyntheticJobPage(1, 1, 0, ()),)
    assert enumerate_provider_job_ids(empty) == ()
    with pytest.raises(ProviderJobNotFoundError):
        run_lookup(sequence=empty)


@pytest.mark.parametrize(
    "sequence",
    [
        (page(),),
        (page(), page(3, ids=(42,))),
        (page(), page(1, ids=(42,))),
        (page(), page(2, 3, ids=(42,))),
        (page(), page(2, ids=(41,))),
        (page(), page(2, ids=())),
        (page(), page(2, ids=(42,)), page(3, 3, 3, (43,))),
        (page(1, 2, 3, (41, 42)), page(2, 2, 3, ())),
    ],
)
def test_partial_duplicate_and_inconsistent_pages_fail_closed(
    sequence: tuple[SyntheticJobPage, ...],
) -> None:
    with pytest.raises(IncompleteProviderPagesError):
        run_lookup(sequence=sequence)


@pytest.mark.parametrize(
    "value",
    [True, False, -1, 0, "2", 2.0],
)
def test_invalid_page_count_types_are_rejected(value: object) -> None:
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids((SyntheticJobPage(1, value, 1, ({"ID": 42},)),))


@pytest.mark.parametrize("bad_id", [False, "42", 42.0, -1, 0, None])
def test_invalid_native_list_ids_fail_closed(bad_id: object) -> None:
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids((SyntheticJobPage(1, 1, 1, ({"ID": bad_id},)),))


def test_missing_final_page_does_not_return_first_match() -> None:
    with pytest.raises(IncompleteProviderPagesError):
        run_lookup(sequence=(page(1, 2, 2, (42,)),))


def test_pagination_limits_enforced() -> None:
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids(pages(), max_pages=1)
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids(pages(), max_results=1)
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids(pages(), max_pages=True)
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids(pages(), max_results=0)


def test_non_tuple_records_rejected() -> None:
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids((SyntheticJobPage(1, 1, 1, [{"ID": 42}]),))  # type: ignore[arg-type]


def test_more_than_250_records_rejected() -> None:
    records = tuple({"ID": value} for value in range(1, 252))
    with pytest.raises(IncompleteProviderPagesError):
        enumerate_provider_job_ids((SyntheticJobPage(1, 1, 251, records),))


def test_ambiguous_identity_claims_fail_closed() -> None:
    with pytest.raises(AmbiguousProviderIdentityError):
        run_lookup(claims=(identity(), identity(provider_id=41)))


def test_same_provider_id_with_different_job_numbers_is_ambiguous() -> None:
    with pytest.raises(AmbiguousProviderIdentityError):
        run_lookup(claims=(identity(), identity(job_number="DEMO-99")))


@pytest.mark.parametrize(
    "other_name",
    ["demo-42", "ＤＥＭＯ-42"],
)
def test_normalized_job_number_collisions_are_ambiguous(other_name: str) -> None:
    with pytest.raises(AmbiguousProviderIdentityError):
        run_lookup(claims=(identity(), identity(job_number=other_name, provider_id=41)))


def test_unrelated_conflict_in_same_company_blocks_lookup() -> None:
    with pytest.raises(AmbiguousProviderIdentityError):
        run_lookup(
            claims=(
                identity(),
                identity(job_number="OTHER-A", provider_id=41),
                identity(job_number="OTHER-B", provider_id=41),
            )
        )


def test_other_company_conflicts_do_not_pollute_company_scope() -> None:
    result = run_lookup(
        claims=(
            identity(),
            identity(job_number="OTHER-A", provider_id=41, company_id=1),
            identity(job_number="OTHER-B", provider_id=41, company_id=1),
        )
    )
    assert result.job_number == "DEMO-42"


def test_distinct_claims_for_distinct_jobs_remain_valid() -> None:
    result = run_lookup(claims=(identity(), identity(job_number="DEMO-41", provider_id=41)))
    assert result.job_number == "DEMO-42"


def test_company_mismatch_is_not_a_candidate() -> None:
    with pytest.raises(ProviderJobNotFoundError):
        run_lookup(claims=(identity(company_id=1),))


def test_exact_job_number_required() -> None:
    with pytest.raises(ProviderJobNotFoundError):
        run_lookup(claims=(identity(job_number="demo-42"),))


def test_claimed_job_must_exist_in_full_list_and_details() -> None:
    with pytest.raises(ProviderJobNotFoundError):
        run_lookup(claims=(identity(provider_id=73),))
    with pytest.raises(ProviderJobNotFoundError):
        run_lookup(details={})


def test_detail_id_must_match_claimed_id() -> None:
    with pytest.raises(UnverifiedJobIdentityError):
        run_lookup(details={42: detail(41)})


def test_invalid_claim_instance_revalidated() -> None:
    bad = identity().model_copy(update={"unknown": "injected"})
    with pytest.raises(ValueError):
        run_lookup(claims=(bad,))


def test_offline_lookup_does_not_open_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("unexpected network access")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    assert run_lookup().job_number == "DEMO-42"


def test_documented_cli_demo_runs_offline() -> None:
    project_root = Path(__file__).resolve().parents[1]
    outcome = subprocess.run(
        [sys.executable, "examples/offline_paged_simpro.py"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    )
    assert "Job: DEMO-42 (synthetic)" in outcome.stdout
    assert "Administrative stage: Progress" in outcome.stdout
    assert "Administrative status: Awaiting approval" in outcome.stdout
    assert "Administrative closure verified: None" in outcome.stdout
    assert "No live Simpro connection" in outcome.stdout
