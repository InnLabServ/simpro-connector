# Simpro Connector

An **offline-first Python foundation** for a potential, explicitly authorized **read-only Simpro job integration**. The codebase can validate and retrieve *synthetic* normalized job records today. It does **not** connect to an ILS Simpro instance, implement a verified Simpro API adapter, deploy a service, or provide an MCP server.

This is a public, MIT-licensed prototype, not an official Simpro product or an authorization to access any Simpro account.

## What works today

| Capability | Status |
| --- | --- |
| Normalized job/part/provenance models, preserving unknown administrative states | Implemented |
| In-memory exact job lookup with optional company scope and explicit missing/ambiguous results | Implemented, synthetic only |
| GET-only HTTP transport with allowlisted paths, host/token checks, and bounded JSON handling | Implemented foundation; no verified Simpro endpoints |
| Simpro-specific authentication, pagination, endpoint mapping and schemas | Not implemented or verified |
| Live ILS data access, synchronization, Drive writes or MCP deployment | Not authorized / not implemented |

**Authority boundaries:** Simpro governs administrative authorization, scheduling, billing and closure. Engineering service records govern visits, observations, evidence and FSRs. Shipment is not receipt, installation or a verified repair.

## Quick start (offline)

Requires Python **3.11+**.

```bash
python -m pip install -e '.[dev]'
python examples/offline_lookup.py
pytest -q
ruff check .
```

The example is deterministic and uses fictional `DEMO-*` records. The package has no dependency on a Simpro account for this workflow.

### Minimal lookup

```python
from ils_simpro.fixtures import sample_job
from ils_simpro.offline import OfflineJobRepository, JobNotFoundError

repository = OfflineJobRepository([sample_job()])
job = repository.get_job("DEMO-1001")
print(job.job_number, job.administrative_closed)  # DEMO-1001 None

try:
    repository.get_job("DEMO-NOT-FOUND")
except JobNotFoundError:
    print("No exact match")
```

Lookup is exact and case-sensitive; malformed identifiers and Unicode-normalized collisions are handled explicitly. A `company_id` keyword can disambiguate records, but its existence in this normalized model does **not** establish the structure of Simpro's API. Details: [Offline lookup](docs/offline-lookup.md).

## Security and live-access boundary

The library's transport is disabled by default. It requires an explicit boolean enablement flag, exact allowed paths, a token and an approved hostname even with mock transports. These are *defense-in-depth controls*, not permission to access a live system. No genuine Simpro URL, credential, customer information or production payload belongs in this repository.

There is **no environment-variable configuration loader**. The sample `.env.example` describes hypothetical settings only and is not read by this package. Do not put credentials into it.

Live use additionally requires official API contract validation, written organizational authorization, contractual/privacy review and a private deployment. The existing request timing checks **do not guarantee an end-to-end deadline**.

## Documentation

- [Architecture and system authority](docs/architecture.md)
- [Offline lookup reference](docs/offline-lookup.md)
- [Transport security and known limitations](docs/security.md)
- [Simpro API discovery and unverified contract details](docs/simpro-api-contract.md)
- [Development milestones and next gates](docs/implementation-roadmap.md)
- [Approval and pilot readiness checklist](docs/approval.md)

## Project status

Foundational development is complete through PRs [#1](https://github.com/InnLabServ/simpro-connector/pull/1), [#2](https://github.com/InnLabServ/simpro-connector/pull/2), [#3](https://github.com/InnLabServ/simpro-connector/pull/3) and [#4](https://github.com/InnLabServ/simpro-connector/pull/4). No release or production connection is implied.

MIT licensed. Not affiliated with or endorsed by Simpro.
