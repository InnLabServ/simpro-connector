# Simpro Connector

A small, **read-only by design** Python foundation for integrating authorized Simpro job data with engineering workflows.

> **Status:** Offline prototype. No organization access, credentials, production data, or Simpro connectivity are included or implied. Deployment and live API access require independent authorization and review of applicable Simpro API terms.

## Scope

- Typed, source-aware summaries of jobs and their related records.
- GET-only HTTP transport with restrictive endpoint allowlisting.
- Deterministic mock responses and tests without external access.
- An adapter boundary for later Google Drive reconciliation; **no Drive writes are implemented**.
- Conservative error handling and data minimization.

This library does **not** alter jobs, close work orders, update billing, deliver FSRs, or access customer data until explicitly configured and authorized. A warehouse shipping confirmation is not proof that a replacement part was received or installed.

## Try the offline example

```bash
python -m pip install -e '.[dev]'
python examples/offline_lookup.py
pytest
```

The fixture uses invented company names and identifiers. No Simpro token is required.

## API usage

```python
from ils_simpro import SimproClient, SimproConfig

# Live access is deliberately disabled by default.
config = SimproConfig(base_url="https://example.invalid", live_enabled=False)
# Client construction does not authorize network operations.
client = SimproClient(config=config)
```

The actual Simpro API's endpoint paths, pagination, account/company scoping and OAuth flow must be confirmed against the current official documentation and an authorized test account before enabling production calls. Do not treat the generic normalized schema as a claim about Simpro's native JSON structure.

See [architecture](docs/architecture.md), [security](docs/security.md) and [approval checklist](docs/approval.md).

## License

MIT. Simpro is a trademark of its respective owner; this project is not affiliated with or endorsed by Simpro.
