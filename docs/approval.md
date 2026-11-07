# Approval checklist

**No approval has been granted by this repository.**

Prior to a limited production pilot:

- Identify the ILS system owner and explicitly obtain their authorization.
- Verify current Simpro API entitlement, authentication flow, company scope, and endpoint documentation.
- Review Simpro license and data-use terms, especially third-party processing and AI-assisted workflows.
- Approve narrowly scoped read-only credentials for identified users or a service identity.
- Define which customer/job fields may leave Simpro and where those copies may be retained.
- Implement private deployment, access controls, audit trail, error reporting and rotation/revocation.
- Validate against one explicitly authorized job, compare API response to the Simpro UI, and record discrepancies.
- Document a rollback/disconnect procedure.
- Keep Simpro writes and administrative closure outside the approved scope unless separately authorized.

## Pilot acceptance

A job-number lookup must return a source-traceable, typed summary without changing any Simpro record. Missing identifiers and uncertainty must remain visible. There must be no accidental credentials or real customer information in public repo, logs or CI artifacts.
