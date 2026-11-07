# Simpro Connector

A public, offline-first Python framework for future, **authorized read-only** Simpro job integration.

This is **not** a live Simpro connector. No internal records, real credentials, API endpoints, production data, private links or operational access are included.

## Development

```bash
python -m pip install -e '.[dev]'
python examples/offline_lookup.py
pytest -q
ruff check .
```

The offline example uses synthetic `DEMO-*` records and does not connect to Simpro.

The transport explicitly requires strict enablement, a fixed endpoint allowlist and, for non-mock network calls, a private approved hostname plus credential. It rejects compressed/oversized/malformed responses and does not expose raw HTTP objects through its documented exceptions. This is an application safety control, **not authorization** to access any organization's Simpro instance.

Documentation: [API discovery](docs/simpro-api-contract.md), [offline lookup](docs/offline-lookup.md), [security](docs/security.md), [approval checklist](docs/approval.md).

MIT licensed. Not affiliated with or endorsed by Simpro.
