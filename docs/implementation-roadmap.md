# Development status and roadmap

As of **2026-11-07**, this page tracks merged capabilities rather than treating completed PRs as future work. A merged security foundation does **not** mean a live Simpro integration has been approved.

## Completed

| Milestone | PR | Outcome |
| --- | --- | --- |
| Package foundation | [#1](https://github.com/InnLabServ/simpro-connector/pull/1) | GET-only transport concept, normalized models, fictional fixtures, tests and CI |
| Public API reconnaissance and CI refresh | [#2](https://github.com/InnLabServ/simpro-connector/pull/2) | Documented API discovery and unknowns; modernized GitHub Actions |
| Offline lookup | [#3](https://github.com/InnLabServ/simpro-connector/pull/3) | Exact lookup, optional company scope, missing/ambiguous errors, immutable normalized records and no-network tests |
| Transport hardening | [#4](https://github.com/InnLabServ/simpro-connector/pull/4) | Strict enablement, host/path/token controls, sanitized outward errors, response limits and adversarial tests |

## Next: verified provider-contract research

- Obtain the **official current** Simpro API specification through an authorized, appropriate route. Record retrieval date, version and digest; do not add proprietary material without permission.
- Verify actual job lookup semantics, internal identifiers versus displayed job numbers, company scope, authentication, response schemas, pagination, filters, limits and error behavior.
- Define a minimal read-only provider adapter against *verified* contracts, initially using fabricated data and mocks.
- Document unmapped fields and unknown states explicitly; do not infer repair completion, FSR delivery or billing closure from unrelated statuses.

This phase is **not yet implemented**. No guessed Simpro-native paths or payloads should be introduced as facts.

## Before any real network connection

1. Obtain explicit ILS system-owner authorization for the host, identity, permitted fields, users and scope.
2. Review Simpro subscription/developer terms, customer confidentiality and third-party/AI-processing restrictions; identify an accountable approver.
3. Establish the approved DNS hostname and scoped credentials in private deployment configuration.
4. Add and verify a genuine overall request deadline covering connection, TLS, headers and response body, not just per-read timeouts.
5. Validate schemas/limits against official sources and compare one **expressly approved** job with its Simpro UI using redacted private evidence.
6. Implement access controls, field minimization, auditing, retention, revocation and a disconnect plan.

A pilot is a separate authorization decision, not an automatic consequence of passing tests.

## Explicitly out of scope today

No production Simpro access, credential acquisition, live job synchronization, writes to Simpro, engineering Drive edits, MCP deployment or background polling. Reconciliation may someday propose a provenance-backed diff, but must not silently change either authoritative record system.

See [Approval checklist](approval.md), [Security](security.md) and [API discovery](simpro-api-contract.md).
