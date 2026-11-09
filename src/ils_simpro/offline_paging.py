"""Bounded offline enumeration and lookup over fabricated Simpro-shaped pages.

Page metadata and details are caller-supplied synthetic values, not API responses.
No network, filesystem, credential or real-job access.
"""

import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictInt, ValidationError

from .models import JobSummary, valid_identifier
from .simpro_synthetic import VerifiedJobIdentity, normalize_synthetic_simpro_job


class IncompleteProviderPagesError(ValueError):
    """Pagination is missing, malformed, contradictory, duplicated or over budget."""


class AmbiguousProviderIdentityError(ValueError):
    """More than one purported identity matches an exact scoped lookup."""


class ProviderJobNotFoundError(LookupError):
    """The desired identity or provider job is absent from the complete snapshot."""


class _ListItem(BaseModel):
    # The default native list projection has more fields; only ID is consumed.
    model_config = ConfigDict(extra="ignore", frozen=True, revalidate_instances="always")

    ID: Annotated[StrictInt, Field(ge=1)]


@dataclass(frozen=True)
class SyntheticJobPage:
    page: int
    total_pages: int
    total_results: int
    records: tuple[Mapping[str, object], ...]


def _strict_positive_int(value: object, name: str) -> int:
    if type(value) is not int or value < 1:
        raise IncompleteProviderPagesError(f"{name} must be a positive integer")
    return value


def enumerate_provider_job_ids(
    pages: Iterable[SyntheticJobPage],
    *,
    max_pages: int = 100,
    max_results: int = 25000,
) -> tuple[int, ...]:
    """Require a contiguous, complete, bounded and internally consistent snapshot.

    This deliberately does not issue or search native API requests. A future
    provider must supply independently validated pagination metadata.
    """
    _strict_positive_int(max_pages, "max_pages")
    _strict_positive_int(max_results, "max_results")
    if isinstance(pages, (str, bytes, Mapping)):
        raise TypeError("pages must be an iterable of SyntheticJobPage")
    iterator = iter(pages)
    seen: set[int] = set()
    ids: list[int] = []
    expected_pages: int | None = None
    expected_total: int | None = None

    for page_number in range(1, max_pages + 1):
        try:
            page = next(iterator)
        except StopIteration:
            raise IncompleteProviderPagesError("Pagination ended before completion") from None
        if type(page) is not SyntheticJobPage:
            raise IncompleteProviderPagesError("Invalid page representation")
        if type(page.page) is not int or page.page != page_number:
            raise IncompleteProviderPagesError("Page numbers must be contiguous starting at 1")
        count = _strict_positive_int(page.total_pages, "total_pages")
        if count > max_pages:
            raise IncompleteProviderPagesError("Page count exceeds configured bound")
        if type(page.total_results) is not int or not 0 <= page.total_results <= max_results:
            raise IncompleteProviderPagesError("Invalid or oversized total_results")
        if expected_pages is None:
            expected_pages, expected_total = count, page.total_results
        elif (count, page.total_results) != (expected_pages, expected_total):
            raise IncompleteProviderPagesError("Pagination metadata changed")
        if type(page.records) is not tuple or len(page.records) > 250:
            raise IncompleteProviderPagesError("Page records must be a tuple of at most 250 items")
        for raw in page.records:
            if not isinstance(raw, Mapping):
                raise IncompleteProviderPagesError("Invalid list record")
            try:
                native_id = _ListItem.model_validate(raw).ID
            except ValidationError:
                raise IncompleteProviderPagesError("Invalid provider job ID") from None
            if native_id in seen:
                raise IncompleteProviderPagesError("Duplicate provider ID in paginated snapshot")
            seen.add(native_id)
            ids.append(native_id)
            if len(ids) > max_results:
                raise IncompleteProviderPagesError("Result count exceeds configured bound")
        if page_number == expected_pages:
            if len(ids) != expected_total:
                raise IncompleteProviderPagesError("Collected result count differs from declared total")
            try:
                next(iterator)
            except StopIteration:
                return tuple(ids)
            raise IncompleteProviderPagesError("Unexpected extra page after final page")
    raise IncompleteProviderPagesError("Pagination did not finish within configured bound")


def lookup_synthetic_job(
    job_number: str,
    *,
    company_id: int,
    pages: Iterable[SyntheticJobPage],
    details_by_id: Mapping[int, Mapping[str, object]],
    identities: Iterable[VerifiedJobIdentity],
    max_pages: int = 100,
    max_results: int = 25000,
) -> JobSummary:
    """Exact scoped lookup only after verifying an entire synthetic page sequence.

    Identity evidence and the page's company scope are caller assertions, not
    independent proof of an ILS job mapping or provider response.
    """
    if type(job_number) is not str:
        raise TypeError("job_number must be a string")
    valid_identifier(job_number)
    if type(company_id) is not int or company_id < 0:
        raise ValueError("company_id must be a non-negative integer")
    if not isinstance(details_by_id, Mapping):
        raise TypeError("details_by_id must be a mapping")
    ids = enumerate_provider_job_ids(pages, max_pages=max_pages, max_results=max_results)
    candidates: list[VerifiedJobIdentity] = []
    provider_to_job: dict[int, str] = {}
    normalized_jobs: dict[str, str] = {}
    if isinstance(identities, (str, bytes, Mapping)):
        raise TypeError("identities must be an iterable of VerifiedJobIdentity instances")
    for index, identity in enumerate(identities):
        if index >= max_results:
            raise IncompleteProviderPagesError("Identity claim count exceeds configured bound")
        if not isinstance(identity, VerifiedJobIdentity):
            raise TypeError("identities must contain VerifiedJobIdentity instances")
        identity = VerifiedJobIdentity.model_validate(identity)
        if identity.company_id != company_id:
            continue
        previous_job = provider_to_job.get(identity.provider_job_id)
        if previous_job is not None and previous_job != identity.job_number:
            raise AmbiguousProviderIdentityError("Provider ID has conflicting job-number claims")
        provider_to_job[identity.provider_job_id] = identity.job_number
        normalized = unicodedata.normalize("NFKC", identity.job_number).casefold()
        previous_spelling = normalized_jobs.get(normalized)
        if previous_spelling is not None and previous_spelling != identity.job_number:
            raise AmbiguousProviderIdentityError("Conflicting normalized job-number claims")
        normalized_jobs[normalized] = identity.job_number
        if identity.job_number == job_number:
            candidates.append(identity)
    if not candidates:
        raise ProviderJobNotFoundError("No matching verified identity claim in scope")
    if len(candidates) != 1:
        raise AmbiguousProviderIdentityError("Multiple claims for the same scoped job number")
    candidate = candidates[0]
    if candidate.provider_job_id not in ids or candidate.provider_job_id not in details_by_id:
        raise ProviderJobNotFoundError("Claimed provider job absent from complete snapshot")
    return normalize_synthetic_simpro_job(
        details_by_id[candidate.provider_job_id],
        company_id=company_id,
        identity=candidate,
    )
