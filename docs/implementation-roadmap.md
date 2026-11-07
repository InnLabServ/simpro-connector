# Roadmap and acceptance gates

## Phase A (merged PR #1)

- Python package, GET-only allowlisted transport, normalized model, synthetic fixture.
- Tests and lint in pull-request CI.

## Phase B (PR #2)

- Document the officially observable API surface and unknowns.
- Update GitHub Actions off deprecated Node.js 20 action versions.
- Do not claim undocumented endpoint/JSON behavior.

## Phase C (PR #3)

- Build provider-independent offline job lookup and deterministic synthetic repository.
- Support found/missing/ambiguous jobs and preserve null or unknown statuses.
- Include negative tests proving no HTTP request is made in offline lookup.
- Do not implement private Drive writes, live API calls or any data export.

## Gate before asking an administrator

Demonstrate deterministic offline lookup, targeted tests, and a reviewed permission/data-governance request. Confirm Simpro terms permit the proposed handling. A public source code repository is not a place for production payloads.

## Gate before deployment

Explicit ILS approval, private runtime configuration, least privilege, source-provenance/audit design, actual endpoint validation, token rotation, retention and revocation plan. Admin/billing closure remains in Simpro; engineering records remain separate. No provider writes in initial pilot.
