# Andy Universal Security Report Contract v1

The contract is technology-independent. Web, Android, iOS, APIs, cloud,
desktop, network, IoT, embedded, and future specialists use the same outer
report shape. Domain-specific details belong in claims and evidence metadata,
not in the Andy Core contract.

## Required fields

| Field | Meaning |
|---|---|
| schema_version | Contract version, currently 1.0 |
| report_id | Stable report identifier |
| domain | Technology or security domain |
| report_type | Assessment, research, incident analysis, validation, etc. |
| objective | What the work set out to establish |
| scope | Boundary and authorisation context |
| claims | Atomic factual or analytical statements |
| evidence | Evidence records referenced by claims and tests |
| limitations | Explicit gaps, unavailable inputs, and uncertainty |

Optional tests records describe planned or executed validation.

## Scope and authorisation

scope.summary is required. scope.authorization_status must be one of:
- authorized: explicit permission and scope are documented
- hypothetical: illustrative or training scenario
- not_applicable: no target testing or access is involved
- unknown: authorisation is unclear; this is not permission to test

The contract records authorisation context. It does not grant permission or
enable tools. Actual operations require independent enforcement by a tool
gateway and explicit scope and approval.

## Claim classification

Every claim has a unique claim_id, non-empty text, classification, and
evidence_refs:
- verified: supported by one or more evidence records
- assumption: accepted temporarily but not established
- inference: reasoned interpretation from stated inputs
- unknown: unresolved or unavailable

A claim without evidence must never be labelled verified. Every evidence
reference must resolve within the same report. Optional severity values are
informational, low, medium, high, or critical. Every severity requires a
written severity_rationale.

## Evidence provenance

Each evidence item has a unique evidence_id, evidence_type, stable locator,
ISO-8601 captured_at, and content_summary.

Evidence types: source, artifact, observation, test_result, log, other.
A locator can be a URL, file/repository path, artifact identifier, or another
stable reference.

The v1 deterministic validator checks shape and linkage. It does not fetch
URLs, prove a source exists, assess source authority, or establish that an
excerpt supports a claim. Those require later quality-gate layers. An
"approved" result must not be represented as proof of factual truth.

## Tests

Each test has a unique test_id, status, and expected result. Status is planned,
executed, blocked, or not_applicable. An executed test must include observed
results and evidence references. Planned tests must never be described as run.

## Quality gate outcomes

- approved: deterministic v1 checks passed; not proof of truth, exploitability,
  source authority, or human approval
- revise: recognisable report with missing, inconsistent, or unsupported data
- rejected: invalid document or unsupported schema version

## Example

    {
      "schema_version": "1.0",
      "report_id": "report-2026-001",
      "domain": "web_application",
      "report_type": "security_assessment",
      "objective": "Assess access-control behaviour for an owned test service.",
      "scope": {
        "summary": "Local intentionally vulnerable test service.",
        "authorization_status": "authorized",
        "targets": ["http://127.0.0.1:8080"]
      },
      "claims": [{
        "claim_id": "claim-001",
        "text": "The test account can access the protected resource.",
        "classification": "verified",
        "evidence_refs": ["ev-001"],
        "severity": "medium",
        "severity_rationale": "Cross-account access was demonstrated in the isolated lab."
      }],
      "evidence": [{
        "evidence_id": "ev-001",
        "evidence_type": "test_result",
        "locator": "artifacts/run-001-response.txt",
        "captured_at": "2026-11-24T10:00:00Z",
        "content_summary": "Captured response from the authorised local test."
      }],
      "tests": [{
        "test_id": "test-001",
        "status": "executed",
        "expected": "The service denies access to another account's resource.",
        "observed": "The service returned the protected test record.",
        "evidence_refs": ["ev-001"]
      }],
      "limitations": ["Only the isolated test service and synthetic accounts were used."]
    }
