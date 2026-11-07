# Authorization and pilot-readiness checklist

**No approval is conveyed by source code, a merged PR or a passing CI run.** This checklist tracks work required before a limited, read-only ILS Simpro pilot. All categories below are outstanding unless independently documented and signed off.

## 1. Responsible owner and authorization

- [ ] Identify the ILS Simpro system owner and the approver authorized to grant API access.
- [ ] Record written permission for a specific environment, intended users, identity, data scope and dates.
- [ ] Define a revocation owner and emergency disconnect procedure.
- [ ] Record where approval is retained **privately**, not in this public repository.

## 2. Contracts, confidentiality and AI data handling

- [ ] Identify and review the applicable Simpro subscription agreement, API/developer terms and any partner/integration restrictions.
- [ ] Identify and review ILS customer-contract confidentiality obligations.
- [ ] Determine whether data may be processed by external systems, AI providers or MCP components, and under which agreements.
- [ ] Define a **field-level allowlist**, intended recipients, permitted purposes, retention limits and deletion process.
- [ ] Record approval by the appropriate business/privacy/security owners. Do not infer consent from technical access.

## 3. Technical readiness

- [ ] Retrieve and verify current official API contracts, host, company/identifier semantics, paging, limits and error behavior.
- [ ] Confirm least-privilege read-only credentials, private storage, rotation and revocation.
- [ ] Implement a **true end-to-end request deadline** including connection, TLS, headers and body, and test slow/trickling responses. Existing checks do not provide one.
- [ ] Verify exact allowed request paths and approved hostnames against actual authorized deployment requirements.
- [ ] Define private access controls, field minimization, audit trails and error reporting that does not capture secrets or raw customer data.
- [ ] Specify retention, rollback/disconnect and a bounded pilot scope.

## 4. Pilot acceptance and evidence

- [ ] Select one expressly approved job; privately compare returned fields and statuses against the Simpro UI.
- [ ] Verify that missing/duplicate identities and unknown states remain explicit; no cross-company mix-ups occur.
- [ ] Verify no Simpro writes, administrative closure changes, engineering-record writes or unsupported assumptions.
- [ ] Store only permitted, redacted evidence in an approved private location; never publish payloads, tokens, customer identifiers or private contracts to GitHub.
- [ ] Obtain explicit go/no-go sign-off and document how to stop access.

The initial pilot is **read-only**. Simpro retains authority over billing and administrative closure; engineering records retain authority over field observations, FSRs and evidence. An ordered or shipped part is not proof of installation or repair.

See [Security](security.md), [API discovery](simpro-api-contract.md) and [Roadmap](implementation-roadmap.md).
