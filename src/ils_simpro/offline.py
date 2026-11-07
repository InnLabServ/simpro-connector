"""Deterministic, provider-independent offline job lookup for synthetic fixtures."""

import unicodedata
from collections.abc import Iterable

from .models import JobSummary, valid_identifier


class JobNotFoundError(LookupError):
    """No job matches the exact requested identifier."""


class AmbiguousJobError(LookupError):
    """Multiple records share an identifier; never silently select one."""


class OfflineJobRepository:
    """Immutable, source-validated snapshot. No network or disk access."""

    def __init__(self, jobs: Iterable[JobSummary]) -> None:
        if isinstance(jobs, (str, bytes)):
            raise TypeError("jobs must be an iterable of JobSummary records")
        index: dict[str, list[JobSummary]] = {}
        normalized: dict[str, str] = {}
        for item in jobs:
            if not isinstance(item, JobSummary):
                raise TypeError("jobs must contain JobSummary records")
            # model_construct/model_copy(update=...) bypass Pydantic validation.
            job = JobSummary.model_validate(item.model_dump())
            key = unicodedata.normalize("NFKC", job.job_number).casefold()
            if key in normalized and normalized[key] != job.job_number:
                raise AmbiguousJobError("Conflicting normalized identifiers")
            normalized[key] = job.job_number
            index.setdefault(job.job_number, []).append(job)
        self._index = {key: tuple(values) for key, values in index.items()}

    def get_job(self, job_number: str, *, company_id: str | None = None) -> JobSummary:
        """Return a single exact match, optionally scoped by company."""
        if type(job_number) is not str:
            raise TypeError("job_number must be a string")
        valid_identifier(job_number)
        if company_id is not None:
            if type(company_id) is not str:
                raise TypeError("company_id must be a string")
            valid_identifier(company_id)
        matches = self._index.get(job_number, ())
        if company_id is not None:
            matches = tuple(job for job in matches if job.company_id == company_id)
        if not matches:
            raise JobNotFoundError("Job identifier not found")
        if len(matches) != 1:
            raise AmbiguousJobError("Multiple records share this job identifier")
        return matches[0].model_copy(deep=True)
