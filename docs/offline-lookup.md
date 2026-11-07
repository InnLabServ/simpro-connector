# Offline job lookup contract

`OfflineJobRepository` stores revalidated, immutable normalized `JobSummary` records and performs no network access. The supplied example records are fictional; these are **not** native Simpro API responses.

```python
from ils_simpro.fixtures import sample_job
from ils_simpro.offline import OfflineJobRepository

repo = OfflineJobRepository([sample_job()])
job = repo.get_job("DEMO-1001")
assert job.administrative_closed is None
```

## Behavior

- Exact identifiers only; malformed, blank, padded or control-containing stored identities fail validation.
- Unicode NFKC/casefold *collisions* across distinct textual IDs fail closed at ingestion. Matching remains exact and case-sensitive.
- Lookup accepts optional keyword-only `company_id`. When multiple companies share an exact ID, an unscoped lookup is ambiguous.
- Missing identifiers raise `JobNotFoundError`; multiple exact matches raise `AmbiguousJobError`. Non-string input raises `TypeError`.
- Source models are revalidated at ingestion to catch unsafe `model_construct` and `model_copy(update=...)` state.
- Models are frozen, their nested collections use tuples, and returned records are separate deep copies.
- Every normalized job must include at least one provenance record.
- Unknown values remain unknown. No Simpro-native paths, schemas, API calls or live access are implemented.

The optional company-scoping concept is internal and **does not** establish Simpro's native routing behavior.

See [Architecture](architecture.md) and [API discovery](simpro-api-contract.md).
