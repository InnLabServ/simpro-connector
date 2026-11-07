# Architecture

The design separates provider access, normalization and downstream reconciliation:

1. **Transport:** An allowlisted, GET-only client. The shipping package has no POST/PATCH/PUT/DELETE operation.
2. **Provider mapping (future):** Map verified Simpro responses to explicit normalized models. Do not guess field names or assert API coverage before testing against current documentation.
3. **Reconciliation (future):** Compare administrative facts with a separately maintained engineering register. Generate a proposed diff with source provenance; do not silently overwrite disputed values.
4. **Delivery (future):** An authenticated integration or MCP server exposing deliberately restricted read operations. This project does not implement or deploy one yet.

## Authority boundaries

- Simpro owns job identity, authorization, commercial details, scheduling and formal administrative closure.
- The engineering records system owns instrument service history, dated observations, evidence and field reports.
- OEM documents own technical specifications and procedures.
- A model or assistant is not an authority for successful repairs.

These are architectural boundaries, not production configuration values.

## Normalization policy

Record the exact source identity and timestamps if available. Preserve explicit unknowns. Keep part states ordered, shipped, received and installed distinct. Never infer a successful repair or issued FSR from order fulfillment. A job description mentioning a mass spectrometer does not establish that the mass spectrometer is the affected subsystem.
