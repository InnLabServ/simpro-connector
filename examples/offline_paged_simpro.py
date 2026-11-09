"""Runnable, entirely offline two-page Simpro-shaped job lookup.

From repository root: python examples/offline_paged_simpro.py
"""

from ils_simpro.offline_paging import SyntheticJobPage, lookup_synthetic_job
from ils_simpro.simpro_synthetic import VerifiedJobIdentity

synthetic_pages = (
    SyntheticJobPage(page=1, total_pages=2, total_results=2, records=({"ID": 41},)),
    SyntheticJobPage(page=2, total_pages=2, total_results=2, records=({"ID": 42},)),
)
synthetic_details = {
    42: {
        "ID": 42,
        "Name": "Fictional job, not an ILS identifier",
        "Stage": "Progress",
        "Status": {"ID": 5, "Name": "Awaiting approval", "Color": "#ABC"},
    },
}
fabricated_identity_claims = (
    VerifiedJobIdentity(
        company_id=0,
        provider_job_id=42,
        job_number="DEMO-42",
        evidence_source="fabricated-cross-check-42",
    ),
)

if __name__ == "__main__":
    job = lookup_synthetic_job(
        "DEMO-42",
        company_id=0,
        pages=synthetic_pages,
        details_by_id=synthetic_details,
        identities=fabricated_identity_claims,
    )
    print(f"Job: {job.job_number} (synthetic)")
    print(f"Provider company: {job.company_id}")
    print(f"Administrative stage: {job.administrative_stage_raw}")
    print(f"Administrative status: {job.administrative_status_raw}")
    print(f"Administrative closure verified: {job.administrative_closed}")
    print("No live Simpro connection or ILS job-number mapping performed.")
