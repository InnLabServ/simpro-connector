# Simpro Connector

An **offline-first Python foundation** for a potential, explicitly authorized **read-only Simpro job integration**. The codebase can validate and retrieve *synthetic* normalized job records today. It does **not** connect to an ILS Simpro instance, implement a verified Simpro API adapter, deploy a service, or provide an MCP server.

This is a public, MIT-licensed prototype, not an official Simpro product or an authorization to access any Simpro account.

## What works today

| Capability | Status |
| --- | --- |
| Normalized job/part/provenance models, preserving unknown administrative states | Implemented |
| In-memory exact job lookup with optional company scope and explicit missing/ambiguous results | Implemented, synthetic only |
| GET-only HTTP transport with allowlisted paths, host/token checks, and bounded JSON handling | Implemented foundation; no verified Simpro endpoints |
| Synthetic Simpro detail mapping with explicit identity claims | Implemented offline; mapping to ILS job numbers unverified |
| Bounded synthetic pagination and company-scoped exact lookup | Implemented offline; no native network adapter |
| Simpro authentication, deployed API pagination, endpoint wiring and identity matching | Not implemented or verified |
| Live ILS data access, synchronization, Drive writes or MCP deployment | Not authorized / not implemented |

**Authority boundaries:** Simpro governs administrative authorization, scheduling, billing and closure. Engineering service records govern visits, observations, evidence and FSRs. Shipment is not receipt, installation or a verified repair.

## Quick start (offline)

Requires Python **3.11+**. From the repository root, create and activate a virtual environment first (avoids externally managed system-Python installations):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python examples/offline_lookup.py
python examples/offline_paged_simpro.py
pytest -q
ruff check .
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of the `source` command. Both examples are deterministic and use fictional `DEMO-*` records. The package has no dependency on a Simpro account for this workflow.

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

`administrative_closed=None` means the source did **not establish** whether the job is closed; it does not mean `False` (open).

Lookup is exact and case-sensitive; malformed identifiers and Unicode-normalized collisions are handled explicitly. A `company_id` keyword can disambiguate records, but its existence in this normalized model does **not** establish the structure of Simpro's API. Details: [Offline lookup](docs/offline-lookup.md).

### Offline paged Simpro-shaped example

`python examples/offline_paged_simpro.py` enumerates two fabricated pages, validates that
the reported total and page order are complete, and looks up `DEMO-42` using an explicit
caller-supplied identity claim. It prints a synthetic administrative stage and status
without treating either as proof of repair or closure. Incomplete pages, duplicate IDs,
ambiguous claims and mismatched details fail closed. This is **not** a network client,
and no actual ILS `JN####` mapping has been established.

## Security and live-access boundary

The library's transport is disabled by default. It requires an explicit boolean enablement flag, exact allowed paths, a token and an approved hostname even with mock transports. These are *defense-in-depth controls*, not permission to access a live system. No genuine Simpro URL, credential, customer information or production payload belongs in this repository.

There is **no environment-variable configuration loader**. The sample `.env.example` describes hypothetical settings only and is not read by this package. Do not put credentials into it.

Live use additionally requires official API contract validation, written organizational authorization, contractual/privacy review and a private deployment. The existing request timing checks **do not guarantee an end-to-end deadline**.

## Documentation

- [Architecture and system authority](docs/architecture.md)
- [Offline lookup reference](docs/offline-lookup.md)
- [Offline synthetic provider mapping](docs/synthetic-adapter.md)
- [Transport security and known limitations](docs/security.md)
- [Simpro API discovery and unverified contract details](docs/simpro-api-contract.md)
- [Development milestones and next gates](docs/implementation-roadmap.md)
- [Approval and pilot readiness checklist](docs/approval.md)

## Project status

Offline foundations are merged through [PR #8](https://github.com/InnLabServ/simpro-connector/pull/8). Subsequent pagination work remains synthetic until a deployed contract and organizational access are approved. No release or production connection is implied.

MIT licensed. Not affiliated with or endorsed by Simpro.
