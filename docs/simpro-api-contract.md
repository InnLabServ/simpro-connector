# Simpro API reconnaissance (public documentation only)

Status: **documentation discovery, not a validated implementation contract**. Last reviewed 2026-11-07.

## Official sources

- [Simpro Developer Center](https://developer.simprogroup.com/)
- [Simpro API documentation](https://developer.simprogroup.com/apidoc/)
- [Getting started and OAuth2](https://developer.simprogroup.com/apidoc/)

The official documentation describes the service as a REST API using OAuth2 and says a Swagger/OpenAPI 2.0 specification is available. Its navigation visibly includes **Jobs**, **Job Cost Centers**, **Customers**, **Sites**, **Schedules**, **Vendor/Supplier Orders**, **Status Codes** and **Work Orders / Job Cards**.

**Not yet verified:** individual HTTP paths, job-number versus internal-ID lookup semantics, company scoping, response JSON shapes, authentication grant selection, token refresh behavior, pagination, filters, response codes, rate-limit headers and field-level permissions. The official documentation is dynamically presented and its navigational headings alone do not establish these details. Do not invent paths or commit unverified payload models as Simpro-native.

## Contract inventory

| Capability | Public documentation discovery | Endpoint and schema | Initial priority |
| --- | --- | --- | --- |
| Job lookup | Jobs section listed | **Unverified** | P0 |
| Customer/site | Customers and Sites sections listed | **Unverified** | P0 |
| Schedule | Schedules section listed | **Unverified** | P1 |
| Job materials | Jobs/Job Cost Centers and supplier order sections listed | **Unverified** | P1 |
| Status | Status Codes section listed | **Unverified** | P1 |
| Job cards | Work Orders / Job Cards section listed | **Unverified** | P2 |

Do not conflate supplier shipment, receipt, installation or verification. A status code in Simpro is not automatically an engineering repair result.

## Required research before live integration

1. Retrieve and review the **current official OpenAPI specification** and version/source provenance.
2. Record precise permitted GET endpoints, path parameters, job identity semantics, pagination/filtering and response models.
3. Verify OAuth grant model and least-privilege scopes with the ILS system administrator, without publishing tokens.
4. Confirm rate limits and errors from official documentation. Implement bounded retries only for safe, retryable failures.
5. Determine which fields may be processed externally under Simpro license and ILS policy, including AI-assisted access.
6. Test an explicitly approved job against its Simpro UI; redact all demonstration artifacts.

No API permission or production data access has been granted. The GitHub source repository is public.

## Offline interface contract

PR #3 may implement an **internal mock contract**: `get_job(job_number)` yields a normalized `JobSummary` with provenance, or a typed NotFound/Ambiguous error. This mock contract is *not* a statement of Simpro-native API endpoints.

Recommended examples: `DEMO-1001`, fictional customer name and part identifiers. All fixtures must be synthetic.
