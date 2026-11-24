import unittest
from andy_core.quality_gate import validate_report

def valid_report():
    return {
        "schema_version": "1.0",
        "report_id": "report-001",
        "domain": "mobile",
        "report_type": "security_assessment",
        "objective": "Assess a sample application component boundary.",
        "scope": {
            "summary": "Hypothetical local training application only.",
            "authorization_status": "hypothetical",
            "targets": ["sample-app"],
        },
        "claims": [{
            "claim_id": "claim-001",
            "text": "The supplied manifest declares the component exported.",
            "classification": "verified",
            "evidence_refs": ["ev-001"],
            "severity": "medium",
            "severity_rationale": "The component is externally reachable in the stated configuration.",
        }],
        "evidence": [{
            "evidence_id": "ev-001",
            "evidence_type": "artifact",
            "locator": "artifacts/AndroidManifest.xml#activity-1",
            "captured_at": "2026-11-24T10:00:00+00:00",
            "content_summary": "Manifest excerpt showing the exported attribute.",
        }],
        "tests": [{
            "test_id": "test-001",
            "status": "planned",
            "expected": "The component should reject unauthorised access.",
            "evidence_refs": [],
        }],
        "limitations": ["No runtime test has been executed."],
    }

class QualityGateTests(unittest.TestCase):
    def test_approves_well_formed_report(self):
        result = validate_report(valid_report())
        self.assertEqual(result.status, "approved")
        self.assertEqual(result.issues, [])

    def test_rejects_unsupported_schema_version(self):
        report = valid_report()
        report["schema_version"] = "9.0"
        self.assertEqual(validate_report(report).status, "rejected")

    def test_verified_claim_without_evidence_requires_revision(self):
        report = valid_report()
        report["claims"][0]["evidence_refs"] = []
        result = validate_report(report)
        self.assertEqual(result.status, "revise")
        self.assertIn("UNSUPPORTED_VERIFIED_CLAIM", {x.code for x in result.issues})

    def test_dangling_citation_requires_revision(self):
        report = valid_report()
        report["claims"][0]["evidence_refs"] = ["fabricated-ref"]
        result = validate_report(report)
        self.assertEqual(result.status, "revise")
        self.assertIn("DANGLING_EVIDENCE_REFERENCE", {x.code for x in result.issues})

    def test_severity_requires_rationale(self):
        report = valid_report()
        report["claims"][0]["severity_rationale"] = ""
        result = validate_report(report)
        self.assertIn("SEVERITY_RATIONALE_MISSING", {x.code for x in result.issues})

    def test_executed_test_requires_observation_and_evidence(self):
        report = valid_report()
        report["tests"][0] = {
            "test_id": "test-002", "status": "executed",
            "expected": "Access is denied.", "observed": "", "evidence_refs": [],
        }
        codes = {x.code for x in validate_report(report).issues}
        self.assertIn("TEST_OBSERVATION_MISSING", codes)
        self.assertIn("TEST_EVIDENCE_MISSING", codes)

    def test_unknown_classification_is_not_accepted(self):
        report = valid_report()
        report["claims"][0]["classification"] = "probably_true"
        self.assertIn("INVALID_CLAIM_CLASSIFICATION",
                      {x.code for x in validate_report(report).issues})


    def test_malformed_untrusted_field_types_return_issues_not_exceptions(self):
        report = valid_report()
        report["scope"]["authorization_status"] = []
        report["claims"][0]["classification"] = {}
        report["claims"][0]["severity"] = []
        report["evidence"][0]["evidence_type"] = {}
        report["tests"][0]["status"] = []
        result = validate_report(report)
        self.assertEqual(result.status, "revise")
        self.assertGreater(len(result.issues), 0)

    def test_malformed_locator_is_rejected_cleanly(self):
        report = valid_report()
        report["evidence"][0]["locator"] = "http://[invalid-ipv6"
        result = validate_report(report)
        self.assertIn("INVALID_EVIDENCE_LOCATOR", {x.code for x in result.issues})

    def test_unknown_authorisation_is_flagged(self):
        report = valid_report()
        report["scope"]["authorization_status"] = "maybe"
        self.assertIn("INVALID_AUTHORIZATION_STATUS",
                      {x.code for x in validate_report(report).issues})

if __name__ == "__main__":
    unittest.main()
