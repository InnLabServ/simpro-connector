# Offline synthetic Simpro job adapter

This module accepts **fabricated** Simpro-shaped job-detail dictionaries only. It does not
fetch, authenticate, enumerate, page through, or write to Simpro, and does not
turn an arbitrary provider ID into an ILS job number.

## Source research

The user-attested official Simpro Swagger 2.0 archive (`swagger.json`, SHA-256
`4af5b2e30f09d6ac48967e511ade5f329f31ea10a2062ca604220072bc934889`)
describes GET `/api/v1.0/companies/{companyID}/jobs/{jobID}`:

- `ID`: integer, "This job's ID".
- `Name` and `OrderNo`: strings, with **no verified relation** to ILS `JN####`.
- `RequestNo`: string, deprecated and referring to the job name.
- `Stage`: string, enumerated as Pending, Progress, Complete, Invoiced, Archived.
- `Status`: a separate object with `ID` (integer), `Name` (string) and `Color`.
- List `search` selects all/any conditions; it is not an exact-job-number API.

The schema does document company ID 0 as the default for a build without
multi-company setup, but this is **not** grounds to hardcode a live build ID.
Release/build compatibility and job-number formatting remain unknown.

## Example (fabricated only)

```python
from ils_simpro.simpro_synthetic import (
    VerifiedJobIdentity,
    normalize_synthetic_simpro_job,
)

fake_detail = {
    "ID": 73,
    "Name": "A fictional provider job",
    "Stage": "Progress",
    "Status": {"ID": 5, "Name": "Waiting for approval", "Color": "#00F"},
}
fake_identity = VerifiedJobIdentity(
    company_id=0,
    provider_job_id=73,
    job_number="DEMO-73",
    evidence_source="fabricated-cross-check-73",
)
job = normalize_synthetic_simpro_job(fake_detail, company_id=0, identity=fake_identity)
assert job.job_number == "DEMO-73"
assert job.administrative_stage_raw == "Progress"
assert job.administrative_status_raw == "Waiting for approval"
assert job.administrative_closed is None
```

The caller must supply a `VerifiedJobIdentity` identity claim whose
company and provider job IDs match the detail record. This is a **claim made by
the caller**, not evidence that the adapter independently validated a live
ILS job number. The public tests use only fabricated identity associations.

The adapter projects two distinct raw fields into `JobSummary`: provider
`Stage` to `administrative_stage_raw` and `Status.Name` to
`administrative_status_raw`. Other native fields are ignored in this narrow
projection; a supplied `Status` object requires validated `ID` and `Name`,
while `Color` is ignored. Only `Status.Name` is projected; `Status.ID` is not
normalized. The original native payload must be retained separately by any
future authorized integration that needs full fidelity.

Unknown and future stages remain raw strings rather than being mapped to
completion. Malformed types, invalid prebuilt Pydantic instances and mismatched identity claims fail closed. The adapter
does **not** infer technical repair, part receipt/installation, or administrative
closure. It must not be connected to live request transport without separate
authorization, provider/build validation, privacy review, and a complete
request-deadline implementation. See [API contract](simpro-api-contract.md)
and [Approval checklist](approval.md).
