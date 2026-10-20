import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.bounty_gate import validate_record


def record():
    return {
        "schema_version": "1.0",
        "target": {
            "program": "Example Program", "asset": "Example Contract",
            "source_url": "https://example.org/scope", "repository": "org/repo",
            "revision": "abc123def456", "eligible_release_confirmed": True,
            "in_scope": True, "scope_snapshot_checked_at": "2026-10-20T10:00:00Z",
            "allowed_environments": ["local", "local-fork"],
            "prohibited_actions": ["public-network-testing", "denial-of-service"],
            "allowed_actions": []
        },
        "claim": {
            "id": "H-001", "status": "REPRODUCED",
            "title": "Invariant mismatch in local model",
            "hypothesis": "A permitted state transition may violate an accounting invariant.",
            "claimed_impact": "Funds accounting discrepancy under specified local preconditions",
            "first_discovered_at": "2026-10-20T10:30:00Z"
        },
        "experiment": {
            "environment": "local-fork", "target_matches_scope": True, "destructive": False,
            "uses_public_network": False, "reproducible": True, "poc_passed": True
        },
        "evidence": [{
            "id": "E-001", "kind": "test-log", "path": "tests/fixtures/run.txt", "sha256": None,
            "target_revision": "abc123def456", "observed_at": "2026-10-20T10:45:00Z",
            "reproducible": True
        }],
        "gates": {
            "scope_reviewed": True, "release_pinned": True, "known_issues_reviewed": True,
            "audits_reviewed": True, "impact_mapped_to_program": True,
            "independent_review_passed": False, "human_approved": False,
            "submission_human_authored": True, "ai_generated_report": False,
            "deadline_checked": True, "eligibility_confirmed": True
        },
        "program_terms": {
            "poc_required": True, "report_deadline_hours": 24,
            "deadline_rule_confirmed": True, "ai_report_policy": "prohibited",
            "scope_refresh_max_age_hours": 24
        }
    }


class ValidateRecordTests(unittest.TestCase):
    def test_valid_record_still_requires_human_review_gates(self):
        result = validate_record(record(), root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertTrue(result["valid"])
        self.assertFalse(result["submission_gate_pass"])
        self.assertIn("gates.independent_review_passed", result["blocking_gates"])
        self.assertIn("gates.human_approved", result["blocking_gates"])

    def test_rejects_moving_ref(self):
        item = record()
        item["target"]["revision"] = "main"
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertIn("target.revision must be an immutable commit/hash, not a branch or moving ref", result["errors"])

    def test_rejects_environment_not_in_scope_contract(self):
        item = record()
        item["experiment"]["environment"] = "public-mainnet"
        item["experiment"]["uses_public_network"] = True
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertTrue(any("environment" in error for error in result["errors"]))

    def test_public_network_is_not_authorized_by_environment_allowlist_alone(self):
        item = record()
        item["target"]["allowed_environments"].append("public-mainnet")
        item["target"]["prohibited_actions"] = ["denial-of-service"]
        item["experiment"]["environment"] = "public-mainnet"
        item["experiment"]["uses_public_network"] = True
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertIn("experiment uses a public network without explicit program authorization", result["errors"])

    def test_rejects_unauthorized_destructive_testing(self):
        item = record()
        item["experiment"]["destructive"] = True
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertIn("experiment is destructive but destructive testing is not explicitly authorized", result["errors"])

    def test_rejects_target_scope_mismatch(self):
        item = record()
        item["experiment"]["target_matches_scope"] = False
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertIn("experiment target is not confirmed within the current program scope", result["errors"])

    def test_reproduced_claim_requires_evidence(self):
        item = record()
        item["evidence"] = []
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertIn("claim status REPRODUCED or later requires at least one evidence item", result["errors"])

    def test_rejects_evidence_from_different_revision(self):
        item = record()
        item["evidence"][0]["target_revision"] = "def456abc789"
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertTrue(any("target_revision" in error for error in result["errors"]))

    def test_rejects_elapsed_reporting_deadline(self):
        item = record()
        item["claim"]["first_discovered_at"] = "2026-10-19T10:00:00Z"
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertTrue(any("reporting deadline has elapsed" in error for error in result["errors"]))

    def test_unknown_reporting_rule_blocks_submission_gate(self):
        item = record()
        item["program_terms"]["deadline_rule_confirmed"] = False
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertTrue(result["valid"])
        self.assertFalse(result["submission_gate_pass"])
        self.assertIn("program_terms.deadline_rule_confirmed", result["blocking_gates"])

    def test_ai_generated_report_is_rejected_when_program_prohibits_it(self):
        item = record()
        item["gates"]["ai_generated_report"] = True
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertIn("AI-generated external reports are prohibited by the current program terms", result["errors"])

    def test_missing_human_authorship_blocks_submission(self):
        item = record()
        item["gates"]["submission_human_authored"] = False
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertTrue(result["valid"])
        self.assertFalse(result["submission_gate_pass"])
        self.assertIn("gates.submission_human_authored", result["blocking_gates"])

    def test_verifies_sha256_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "artifacts" / "run.txt"
            artifact.parent.mkdir()
            artifact.write_text("deterministic evidence\n", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            item = record()
            item["evidence"][0]["path"] = "artifacts/run.txt"
            item["evidence"][0]["sha256"] = digest
            result = validate_record(item, root=root, now="2026-10-20T11:00:00Z")
            self.assertTrue(result["valid"])

    def test_rejects_sha256_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "artifacts" / "run.txt"
            artifact.parent.mkdir()
            artifact.write_text("evidence payload\n", encoding="utf-8")
            item = record()
            item["evidence"][0]["path"] = "artifacts/run.txt"
            item["evidence"][0]["sha256"] = "0" * 64
            result = validate_record(item, root=root, now="2026-10-20T11:00:00Z")
            self.assertFalse(result["valid"])
            self.assertIn("evidence[0].sha256 does not match the evidence file", result["errors"])

    def test_rejects_artifact_path_escape(self):
        item = record()
        item["evidence"][0]["path"] = "../../secrets.txt"
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertTrue(any("escapes repository root" in error for error in result["errors"]))

    def test_unknown_ai_report_policy_blocks_submission(self):
        item = record()
        item["program_terms"]["ai_report_policy"] = "unknown"
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertTrue(result["valid"])
        self.assertFalse(result["submission_gate_pass"])
        self.assertIn("program_terms.ai_report_policy", result["blocking_gates"])

    def test_stale_scope_snapshot_blocks_submission(self):
        item = record()
        item["target"]["scope_snapshot_checked_at"] = "2026-10-18T10:00:00Z"
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertTrue(result["valid"])
        self.assertIn("scope_snapshot_freshness", result["blocking_gates"])

    def test_missing_local_artifact_is_invalid(self):
        item = record()
        item["evidence"][0]["path"] = "tests/fixtures/does-not-exist.log"
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertFalse(result["valid"])
        self.assertTrue(any("does not resolve to an existing evidence file" in error for error in result["errors"]))

    def test_hypothesis_is_never_promoted_automatically(self):
        item = record()
        item["claim"]["status"] = "HYPOTHESIS"
        item["evidence"] = []
        result = validate_record(item, root=Path(__file__).resolve().parents[1], now="2026-10-20T11:00:00Z")
        self.assertEqual(result["claim_status"], "HYPOTHESIS")
        self.assertFalse(result["submission_gate_pass"])
        self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
