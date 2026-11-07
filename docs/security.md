# Security and data governance

## Public repository boundary

Only synthetic examples may enter source control, CI artifacts and public issues. Do not commit real customer names, personal contact information, instrument serial numbers, job records, API responses, internal document links, emails, authorization codes, refresh tokens or screenshots. Never publish internal Mem/standing-order documents.

## Runtime controls

- Default network access is disabled by application policy.
- Live transport requires explicit opt-in and an allowlisted path.
- GET is the only implemented HTTP method; redirects are disabled.
- Use least-privilege OAuth credentials after formal approval; do not put tokens in URLs, issues, logs or code.
- Configure separate private deployment secrets and access logs. Avoid logging raw customer payloads.
- Review token rotation, retention, revocation and exposure-response procedures before production use.
- Do not enable live access solely by changing a public repository configuration.
- Do not assume GET operations are free of effects server-side; production authorization is still required.

## Deployment gate

No live Simpro access, internal data export, ChatGPT-connected exposure, production synchronization, or write operation without ILS authorization and review of provider terms, information security and intended recipients.
