# Simpro API discovery: verified headings and unknown contracts

**Status:** public documentation reconnaissance, **not** a validated Simpro-native implementation contract. Reviewed for this repository on **2026-11-07**.

## Primary public entry points

- [Official Simpro Developer Center](https://developer.simprogroup.com/)
- [Official API documentation index](https://developer.simprogroup.com/apidoc/)

The documentation navigation identifies resource areas including **Jobs**, **Job Cost Centers**, **Customers**, **Sites**, **Schedules**, **Vendor/Supplier Orders**, **Status Codes**, **Companies** and **Work Orders / Job Cards**. It also exposes topics related to authentication/grant types and API call limits. A navigation entry is **not** proof of a particular endpoint shape, permission, grant or JSON schema.

A previous draft asserted availability of a Swagger/OpenAPI 2.0 file. Its precise official artifact URL and version were **not independently captured** for this repository; treat that claim as **unverified until the original specification is retrieved**. Do not assume that a machine-readable specification is publicly downloadable.

## Contract inventory

| Capability | Evidence presently documented | Still to verify |
| --- | --- | --- |
| Job lookup | Jobs resource listed | Company and job identifier semantics; GET path, schema and filtering |
| Customer/site | Customers and Sites listed | Associations, privacy fields and permissions |
| Scheduling | Schedules listed | Read routes, time zones and permissions |
| Materials/order state | Job Cost Centers and Vendor/Supplier Orders listed | Meaning and source of shipped, received and installed states |
| Status | Status Codes listed | Raw status representation and administrative closure mapping |
| Job cards | Work Orders / Job Cards listed | Read access and evidence semantics |
| Company scope | Companies listed | Scoping and identity rules |
| Authentication and call limits | Documentation navigation topics listed | Grant types, scopes, expiration, error/retry and rate-limit details |

**Unverified until primary evidence is available:** official request paths and parameters, authorization grants, company/build hostnames, ID conversion rules, response shapes, pagination, rate-limit values, error semantics and any provider-specific data retention/use restrictions.

Webhooks and provider write/configuration operations are outside this read-only prototype's scope.

## Evidence required before coding a live adapter

1. Retrieve the official specification and relevant authentication/limits reference pages; record URLs, access date, version and, when distributable, file hash.
2. Identify precise permitted GET endpoints and company/identifier behavior. Keep native responses separate from normalized internal models.
3. Check least-privilege authorization and company scoping with the ILS system owner. Do not put credentials, tokens or private contract excerpts in this public repo.
4. Confirm paging, retryability and limits using official evidence, not assumptions from a sidebar or a mock.
5. Have the appropriate owner review Simpro subscription/developer terms, customer confidentiality, external/AI processing, field allowlists, retention and recipient access.
6. Only after written approval, validate against an authorized job privately with a redacted evidence trail.

## Implemented internal contract (not Simpro API)

The merged offline repository exposes:

```python
OfflineJobRepository(jobs).get_job(job_number, *, company_id=None)
```

It returns a normalized `JobSummary` with required provenance or raises `JobNotFoundError` / `AmbiguousJobError` for missing or nonunique records. Malformed input is rejected. Matching is exact, while normalized Unicode/case collisions fail closed on ingestion.

`company_id` is a **provider-independent internal concept**; it does not assert a Simpro-native URL or query parameter. Use only synthetic `DEMO-*` fixtures in the public repository.

See [Offline lookup](offline-lookup.md), [Architecture](architecture.md) and [Approval](approval.md).
