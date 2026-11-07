"""Synthetic examples. Never replace these with unsanitized customer data."""

from .models import JobSummary, PartState, PartSummary, Provenance


def sample_job() -> JobSummary:
    return JobSummary(
        job_number="DEMO-1001",
        customer_name="Example Research Laboratory",
        site_name="Demonstration Site",
        instrument="Example LC system",
        operational_status="awaiting parts",
        administrative_closed=None,
        parts=[PartSummary(part_number="DEMO-PART-A", quantity=1, state=PartState.SHIPPED)],
        provenance=[Provenance(system="synthetic_fixture", source_id="demo-1001")],
        unresolved=["Delivery, installation and repair outcome not confirmed"],
    )
