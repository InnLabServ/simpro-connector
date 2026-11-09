# Development status and roadmap

This page distinguishes merged capabilities from unmerged offline development and future authorization gates. A merged security foundation does **not** mean a live Simpro integration has been approved.

## Completed

| Milestone | PR | Outcome |
| --- | --- | --- |
| Package foundation | [#1](https://github.com/InnLabServ/simpro-connector/pull/1) | GET-only transport concept, normalized models, fictional fixtures, tests and CI |
| Public API reconnaissance and CI refresh | [#2](https://github.com/InnLabServ/simpro-connector/pull/2) | Documented API discovery and unknowns; modernized GitHub Actions |
| Offline lookup | [#3](https://github.com/InnLabServ/simpro-connector/pull/3) | Exact lookup, optional company scope, missing/ambiguous errors, immutable normalized records and no-network tests |
| Transport hardening | [#4](https://github.com/InnLabServ/simpro-connector/pull/4) | Strict enablement, host/path/token controls, sanitized outward errors, response limits and adversarial tests |\n| Public API contract evidence | [#6](https://github.com/InnLabServ/simpro-connector/pull/6) | Official-download-attested Swagger reconnaissance and explicit unknown identity semantics |\n| Synthetic provider-detail mapping | [#8](https://github.com/InnLabServ/simpro-connector/pull/8) | Explicit caller identity claim, separate raw Stage/Status, adversarial validation |

## Current offline milestone (PR #9, under review)

- Enumerate only **fabricated** Simpro-shaped job list pages within explicit
  maximum page and result budgets.
- Check complete one-based page coverage, consistent reported total counts,
  strict job IDs, and no duplicate provider IDs.
- Perform exact scoped lookup only against an explicit caller-supplied
  job-number identity claim and a matching fabricated detail record.
- Provide a runnable CLI demo with synthetic `DEMO-*` values; no HTTP request.
- Treat incomplete results or ambiguous claims as errors, not a best guess.

The current offline enumerator is not a native API paginator or a deployed
Simpro job lookup. It has no access to ILS accounts. Approval, schema matching,
precise filter semantics, secure network timing and an authorized private pilot
remain future work. The PR #9 work is not merged until separately approved.

## Next gated milestone

- Record version-pinned official API documentation and verify the authorized
  ILS company and displayed job-number mapping against a single private,
  expressly approved job.
- Define authentic pagination headers, endpoint request parameters and retry
  behavior before wiring any real HTTP adapter.
- Implement an end-to-end deadline and confidential error handling before a
  separately authorized read-only pilot.

## Before any real network connection

Follow the single canonical [Authorization and pilot-readiness checklist](approval.md), covering written permission, contract/privacy review, verified API semantics, private technical safeguards and explicit pilot sign-off. These are outstanding gates, not implemented capabilities.

A pilot is a separate authorization decision, not an automatic consequence of passing tests.

## Explicitly out of scope today

No production Simpro access, credential acquisition, live job synchronization, writes to Simpro, engineering Drive edits, MCP deployment or background polling. Reconciliation may someday propose a provenance-backed diff, but must not silently change either authoritative record system.

See [Approval checklist](approval.md), [Security](security.md) and [API discovery](simpro-api-contract.md).
