"""Deterministic, technology-independent validation for Andy security reports."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping
from urllib.parse import urlparse

SUPPORTED_SCHEMA_VERSION = "1.0"
CLAIM_CLASSIFICATIONS = {"verified", "assumption", "inference", "unknown"}
EVIDENCE_TYPES = {"source", "artifact", "observation", "test_result", "log", "other"}
SEVERITY_LEVELS = {"informational", "low", "medium", "high", "critical"}

@dataclass(frozen=True, slots=True)
class QualityIssue:
    code: str
    path: str
    message: str
    severity: str = "error"

@dataclass(slots=True)
class QualityGateResult:
    status: str
    schema_version: str
    issues: list[QualityIssue] = field(default_factory=list)
    checks_performed: tuple[str, ...] = (
        "schema_version", "required_fields", "unique_identifiers",
        "evidence_references", "verified_claim_support", "severity_rationale",
        "test_result_completeness",
    )
    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "schema_version": self.schema_version,
            "issues": [asdict(issue) for issue in self.issues],
            "checks_performed": list(self.checks_performed),
        }

def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _is_iso_datetime(value: Any) -> bool:
    if not _non_empty_string(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (TypeError, ValueError):
        return False

def _valid_locator(value: Any) -> bool:
    if not _non_empty_string(value):
        return False
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https", "file", "urn"} if parsed.scheme else True
    except ValueError:
        return False

def _one_of(value: Any, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices

def validate_report(report: Mapping[str, Any]) -> QualityGateResult:
    """Check report structure and evidence linkage, not factual truth or source authority."""
    issues: list[QualityIssue] = []
    def add(code: str, path: str, message: str) -> None:
        issues.append(QualityIssue(code, path, message))

    if not isinstance(report, Mapping):
        return QualityGateResult("rejected", "unknown", [
            QualityIssue("REPORT_NOT_OBJECT", "$", "Report must be an object.")
        ])

    version = report.get("schema_version", "unknown")
    if version != SUPPORTED_SCHEMA_VERSION:
        add("UNSUPPORTED_SCHEMA_VERSION", "schema_version",
            f"Expected schema version {SUPPORTED_SCHEMA_VERSION!r}.")
    for key in ("report_id", "domain", "report_type", "objective"):
        if not _non_empty_string(report.get(key)):
            add("REQUIRED_FIELD_MISSING", key, f"{key} must be a non-empty string.")

    scope = report.get("scope")
    if not isinstance(scope, Mapping):
        add("INVALID_SCOPE", "scope", "scope must be an object.")
    else:
        if not _non_empty_string(scope.get("summary")):
            add("REQUIRED_FIELD_MISSING", "scope.summary", "A scope summary is required.")
        if not _one_of(scope.get("authorization_status"), {
            "authorized", "hypothetical", "not_applicable", "unknown"
        }):
            add("INVALID_AUTHORIZATION_STATUS", "scope.authorization_status",
                "Use authorized, hypothetical, not_applicable, or unknown.")

    evidence = report.get("evidence")
    claims = report.get("claims")
    limitations = report.get("limitations")
    if not isinstance(evidence, list):
        add("INVALID_EVIDENCE", "evidence", "evidence must be a list.")
        evidence = []
    if not isinstance(claims, list):
        add("INVALID_CLAIMS", "claims", "claims must be a list.")
        claims = []
    if not isinstance(limitations, list) or any(not _non_empty_string(x) for x in limitations):
        add("INVALID_LIMITATIONS", "limitations", "limitations must be non-empty strings in a list.")

    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    for i, item in enumerate(evidence):
        path = f"evidence[{i}]"
        if not isinstance(item, Mapping):
            add("INVALID_EVIDENCE_ITEM", path, "Evidence item must be an object.")
            continue
        evidence_id = item.get("evidence_id")
        if not _non_empty_string(evidence_id):
            add("EVIDENCE_ID_MISSING", f"{path}.evidence_id", "A non-empty evidence_id is required.")
            continue
        if evidence_id in evidence_by_id:
            add("DUPLICATE_EVIDENCE_ID", f"{path}.evidence_id", f"Duplicate evidence ID: {evidence_id}.")
            continue
        evidence_by_id[evidence_id] = item
        if not _one_of(item.get("evidence_type"), EVIDENCE_TYPES):
            add("INVALID_EVIDENCE_TYPE", f"{path}.evidence_type", "Unsupported evidence type.")
        if not _valid_locator(item.get("locator")):
            add("INVALID_EVIDENCE_LOCATOR", f"{path}.locator", "A stable non-empty locator is required.")
        if not _is_iso_datetime(item.get("captured_at")):
            add("INVALID_EVIDENCE_TIMESTAMP", f"{path}.captured_at", "Use an ISO-8601 timestamp.")
        if not _non_empty_string(item.get("content_summary")):
            add("EVIDENCE_SUMMARY_MISSING", f"{path}.content_summary", "A concise evidence summary is required.")

    claim_ids: set[str] = set()
    for i, claim in enumerate(claims):
        path = f"claims[{i}]"
        if not isinstance(claim, Mapping):
            add("INVALID_CLAIM", path, "Claim must be an object.")
            continue
        claim_id = claim.get("claim_id")
        if not _non_empty_string(claim_id):
            add("CLAIM_ID_MISSING", f"{path}.claim_id", "A non-empty claim_id is required.")
        elif claim_id in claim_ids:
            add("DUPLICATE_CLAIM_ID", f"{path}.claim_id", f"Duplicate claim ID: {claim_id}.")
        else:
            claim_ids.add(claim_id)
        if not _non_empty_string(claim.get("text")):
            add("CLAIM_TEXT_MISSING", f"{path}.text", "Claim text is required.")
        classification = claim.get("classification")
        if not _one_of(classification, CLAIM_CLASSIFICATIONS):
            add("INVALID_CLAIM_CLASSIFICATION", f"{path}.classification", "Unsupported claim classification.")
        refs = claim.get("evidence_refs", [])
        if not isinstance(refs, list) or any(not _non_empty_string(ref) for ref in refs):
            add("INVALID_EVIDENCE_REFS", f"{path}.evidence_refs", "evidence_refs must be a list of IDs.")
            refs = []
        for ref in refs:
            if ref not in evidence_by_id:
                add("DANGLING_EVIDENCE_REFERENCE", f"{path}.evidence_refs",
                    f"Referenced evidence ID does not exist: {ref}.")
        if classification == "verified" and not refs:
            add("UNSUPPORTED_VERIFIED_CLAIM", f"{path}.evidence_refs",
                "A verified claim must reference at least one evidence item.")
        severity = claim.get("severity")
        if severity is not None:
            if not _one_of(severity, SEVERITY_LEVELS):
                add("INVALID_SEVERITY", f"{path}.severity", "Unsupported severity level.")
            if not _non_empty_string(claim.get("severity_rationale")):
                add("SEVERITY_RATIONALE_MISSING", f"{path}.severity_rationale",
                    "A severity rating requires an explicit rationale.")

    tests = report.get("tests", [])
    if not isinstance(tests, list):
        add("INVALID_TESTS", "tests", "tests must be a list.")
        tests = []
    test_ids: set[str] = set()
    for i, test in enumerate(tests):
        path = f"tests[{i}]"
        if not isinstance(test, Mapping):
            add("INVALID_TEST", path, "Test record must be an object.")
            continue
        test_id = test.get("test_id")
        if not _non_empty_string(test_id) or test_id in test_ids:
            add("INVALID_TEST_ID", f"{path}.test_id", "Each test requires a unique non-empty test_id.")
        else:
            test_ids.add(test_id)
        if not _one_of(test.get("status"), {"planned", "executed", "blocked", "not_applicable"}):
            add("INVALID_TEST_STATUS", f"{path}.status", "Unsupported test status.")
        if not _non_empty_string(test.get("expected")):
            add("TEST_EXPECTATION_MISSING", f"{path}.expected", "Each test requires an expected result.")
        if test.get("status") == "executed":
            if not _non_empty_string(test.get("observed")):
                add("TEST_OBSERVATION_MISSING", f"{path}.observed", "Executed tests require an observed result.")
            refs = test.get("evidence_refs", [])
            if not isinstance(refs, list) or not refs:
                add("TEST_EVIDENCE_MISSING", f"{path}.evidence_refs", "Executed tests require evidence references.")
            else:
                for ref in refs:
                    if ref not in evidence_by_id:
                        add("DANGLING_EVIDENCE_REFERENCE", f"{path}.evidence_refs",
                            f"Referenced evidence ID does not exist: {ref}.")

    rejected = any(x.code in {"REPORT_NOT_OBJECT", "UNSUPPORTED_SCHEMA_VERSION"} for x in issues)
    status = "rejected" if rejected else ("revise" if issues else "approved")
    return QualityGateResult(status, str(version), issues)
