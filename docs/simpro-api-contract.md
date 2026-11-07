# Simpro API contract research: official public evidence

**Research date:** 2026-11-07. **Status:** publicly documented GET contract reconnaissance only. No account/build access, token acquisition, production request or private deployment schema validation was performed. A user-supplied Swagger archive has since been inspected and its origin attested by the downloader. This is not an authorization to access Simpro.

## Primary Simpro sources

- [Official API entry page](https://developer.simprogroup.com/apidoc/)
- [Jobs resource documentation](https://developer.simprogroup.com/apidoc/?page=12ceff2290bb9039beaa8f36d5dec226)
- [Advanced usage: multi-company and pagination](https://developer.simprogroup.com/apidoc/?page=07adc9c3c19b7c17e7309e86c22161a2)
- [Authentication documentation](https://developer.simprogroup.com/apidoc/?page=3366d2ea7906f693b27d57ed9cca3acb)
- [API call limits topic](https://developer.simprogroup.com/apidoc/?page=ed8457e003ba0f6197756eca5a61fde9)

**Evidence caveat:** The API documentation's direct public HTML retrieval sometimes exposes only navigation; search-indexed text from the linked official Simpro pages supplies the endpoint and field details below. The machine-readable specification was supplied by a user who confirms downloading it directly from the official Simpro Developer Center. Its exact download URL, publisher release date, current revision and compatibility with the ILS build have **not** been independently validated. Do not represent indexed page excerpts as a captured, version-pinned OpenAPI contract. No copied provider contract or payload has been committed.

## Confirmed in official published resource documentation

| Topic | Publicly documented behavior | Implementation caution |
| --- | --- | --- |
| Job list | `GET /api/v1.0/companies/{companyID}/jobs/` | Company ID is a required integer path parameter. A list is not an exact job-number lookup. |
| Specific job | `GET /api/v1.0/companies/{companyID}/jobs/{jobID}` | `jobID` is a required integer. The relationship to ILS's displayed `JN####` identifier must be verified, not guessed. |
| Job list response | JSON array; documented fields include integer `ID`, `Description`, `Total`. | `Description` is documented as supporting HTML; treat as untrusted text and do not display unsanitized HTML. |
| Job detail response | JSON object with integer `ID`, `Type`, `Customer`, `Site`, `Name`, `Description`, `Stage`, `Status`, `CompletedDate`, `DateModified` and more. | Nested field definitions and optional/null states must be mapped from a versioned primary contract before implementation. |
| Job detail errors | Documentation explicitly lists HTTP 200 and 404 for retrieval. | Other HTTP errors, retry rules and error-body structure remain unverified. |
| Company scope | Official advanced-usage example uses `/api/v1.0/companies/0` for single-company builds; `GET /api/v1.0/info/` exposes `MultiCompany`, and `GET /api/v1.0/companies/` lists company IDs. | Do not hardcode company 0 or discover/query a private build without approval. |
| Pagination | List default `pageSize=30`, documented maximum 250; `page` starts at 1. `Result-Total`, `Result-Pages`, `Result-Count` response headers are documented. | Implement a bounded, exact-scoped paginator in a later, separately reviewed change. |
| List options | Docs name `search`, `columns`, `pageSize`, `page`, `orderby`, `limit`. | Exact allowed filters, especially displayed number equality, have not been proven for a specific deployed build. |
| Authentication | Official page describes OAuth2 authorization-code, resource-owner-password, implicit, client-credentials and API-key workflows; bearer authorization header is shown. | These are documented options, **not** approval for any grant. Official page says OAuth `scope` parameter is not used; least privilege must therefore be confirmed from user/application permissions and owner governance, not an imagined OAuth scope. |
| Other read resources | The official navigation lists Customers, Sites, Schedules, Job Cost Centers, Vendor/Supplier Orders, Status Codes and Work Orders/Job Cards. | Specific subresource schemas/paths and rights still need dedicated evidence. |

Official job details document `Stage` values including `Pending`, `Progress`, `Complete`, `Invoiced`, `Archived`, plus `Status` and `CompletedDate`. Those are administrative provider fields; none alone establishes field repair completion, FSR delivery, shipping receipt or installed parts. `RequestNo` is documented as deprecated and referring to job name; `Name` and `OrderNo` are also documented fields. **Do not assert that any is ILS's job number without an authorized identity cross-check.**

## Locally supplied machine-readable specification (official-download origin attested)

On 2026-11-07, the project received a user-supplied `swagger.zip` containing one file, `swagger.json`. The downloader explicitly confirmed retrieving the archive directly from Simpro's official Developer Center. This is user-attested source provenance, not independent verification of the exact download URL or release version. The JSON parsed successfully and has `swagger: "2.0"`, `info.title: "Simpro Rest API"`, `info.version: "v1.0"`, **737** paths and **67** schema definitions. Uncompressed JSON length is 27,315,812 bytes.

SHA-256 of the **uncompressed JSON bytes**:
`4af5b2e30f09d6ac48967e511ade5f329f31ea10a2062ca604220072bc934889`

The hash establishes reproducible **file identity**. Direct official-source download is **attested by the downloader**, while the exact download URL, source publication timestamp, license/reuse permissions and version correspondence with ILS's deployed build are **not independently verified**. Keep the archive outside this public repository until redistribution rights are confirmed.

The supplied schema confirms:
- `GET /api/v1.0/companies/{companyID}/jobs/` with required integer `companyID`; query parameters `search`, `columns`, `pageSize` (default 30, max 250), `page` (default 1), `orderby`, `limit`.
- `GET /api/v1.0/companies/{companyID}/jobs/{jobID}` with required integer `companyID` and `jobID`, optional `columns`, and documented 200/404 responses.
- The list's default documented projection requires `ID`, `Description` and `Total`; it does **not** prove that the displayed ILS job number is returned as an exact-match key.
- Detail schema describes integer `ID` as "This job's ID" and includes `OrderNo`, `RequestNo`, `Name`, `Stage`, `Status` and other fields. Their semantics relative to ILS `JN####` **remain unverified**.
- The supplied Swagger root has no `host`, `securityDefinitions` or top-level `security`. That absence is **not** evidence of unauthenticated access. Refer to official security documentation and approval gates.

No production requests, credentials, proprietary schema uploads, or provider adapter changes were made.

## What remains unverified or gated

1. Record the official download URL, publisher revision/release date, reuse terms and ILS deployment compatibility for the user-attested official Swagger/OpenAPI artifact. The JSON is SHA-256 hashed; independent source verification and deployed-build matching remain outstanding.
2. Establish the actual build hostname from ILS's authorized system owner. Do not use a sample hostname as proof of ILS's environment or add unapproved network destinations.
3. Resolve job identity: provider integer `ID` versus ILS `JN####` display, duplicate/multi-company behavior, permitted exact-search predicates, and possible nonnumeric identities.
4. Validate current field-level job-detail schema with the official original contract. In particular, distinguish `Stage`, `Status`, `CompletedDate`, `ArchiveReason` and `DateModified` and preserve raw values and nulls.
5. Confirm actual call-rate/quota values, 429 behavior, headers and retry guidance from authoritative current policy. A sidebar link is not a numerical limit; no rate number is asserted here.
6. Decide authorized OAuth flow or API key deployment, effective per-user/application permissions, audit controls, retention, third-party and AI-processing permissions, and response/error confidentiality.
7. Implement and adversarially test an overall connection-to-body deadline before any live access. Existing transport checks do not supply one.
8. Pilot one expressly authorized job only after written ILS permission and contract/privacy approval. Keep credentials, customer records, token traces, provider sample responses and approval paperwork private.

## Proposed synthetic mapping boundary (not implemented)

A later adapter may accept a fabricated provider-shaped object carrying `ID`, `Name`, `Customer`, `Site`, `Stage`, `Status`, and `CompletedDate`, but it must not invent an association between `ID` and normalized `job_number`. Preserve `companyID` as an explicit separate scoping key; preserve raw administrative status as raw, and keep `administrative_closed=None` unless an approved mapping establishes closure semantics. Do not assume populated `CompletedDate` establishes an instrument repair. Fabricated examples must be clearly distinguished from copied proprietary samples.

The existing `OfflineJobRepository(jobs).get_job(job_number, *, company_id=None)` is a **provider-independent, offline internal contract**, not a native Simpro request. Until identity mapping is verified, do not bind that interface directly to `jobs/{jobID}`.

## Scope and governance

No Simpro writes, billing/closure operations, Drive engineering-record synchronization, automatic polling, authenticated tests, or MCP deployment are authorized. See [Approval checklist](approval.md), [Roadmap](implementation-roadmap.md) and [Offline lookup](offline-lookup.md).
