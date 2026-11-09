# Transport security and data governance

This is an offline-first proof of concept, **not an authorized live integration**. Source code and synthetic fixtures are public. Production records, credentials, contact details, customer agreements and private operating instructions are not.

## Controls implemented

- Live access is disabled by default, with a strict boolean guard and a nonempty immutable allowlist.
- Requests use GET only; configured paths must be ASCII-safe and match the path sent.
- HTTPS DNS names are validated using HTTPX URL semantics, excluding canonical IP literals, numeric/hex host forms, local hosts, userinfo and nonstandard ports.
- All requests, including mocked transports, require a token and an explicitly approved exact hostname supplied by private runtime configuration.
- Redirects and environment proxies are disabled.
- Tokens must be printable ASCII. Sanitized outward-facing errors contain no raw HTTP objects, URLs, credentials or response bodies in their traceback frame locals; underlying in-process transport state cannot be made inaccessible to malicious code.
- Responses must be uncompressed JSON. Compression is rejected until bounded decompression is supported. Raw response streaming is capped at a configurable, provisional 5 MiB default. The existing synchronous `SimproClient` uses HTTPX per-operation timeouts and a body-only best-effort elapsed-time check; **it has no overall deadline**. A separate opt-in `AsyncSimproClient` provides one `asyncio.timeout` across request dispatch, cooperative connection/header handling, response streaming, and response parsing. Its total deadline is **cooperative, not a hard preemptive guarantee**: blocking synchronous callbacks, non-cooperative transports or blocking C-level operations may exceed it. The async path is only validated against `httpx.MockTransport` and is **not approved as a production network client**.
- Non-finite JSON numbers and duplicate keys are rejected.
- Administrative closure and quantity use strict types. Unknown and unverified states stay unknown.

Mock transports are for development/testing, and follow the same authorization gates. They are **not** proof of TLS, DNS or approved Simpro behavior. The HTTP client is still a Python object accessible to code in the same process; application-level guards cannot prevent malicious in-process code from constructing its own HTTP requests.

## Remaining approval gates

ILS owner authorization; review of Simpro API subscription/developer agreements and customer confidentiality; AI-processing approval; official endpoint schema and company scoping; a production hostname allowlist; scoped credentials/rotation; retention and access controls; field-level minimization; auditable private deployment and an authorized live pilot. Never use real customer records in this repository.

Do not claim that a GET-only interface itself grants access or satisfies authorization.
