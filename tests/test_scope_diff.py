import unittest
from copy import deepcopy
from tools.scope_diff import diff_snapshots


def snapshot():
    return {
        "schema_version": "1.0",
        "program": {
            "id": "example:program",
            "name": "Example Bounty",
            "source_url": "https://example.org/program/scope",
            "retrieved_at": "2026-10-20T10:00:00Z",
            "page_last_updated": "2026-10-19",
            "terms": {
                "reward_ceiling": 100000, "reward_currency": "USDC", "kyc_required": False,
                "report_deadline_hours": 24, "deadline_rule": "from first discovery",
                "poc_required": True, "ai_report_policy": "prohibited",
                "allowed_environments": ["local-fork"],
                "prohibited_actions": ["public-network-testing", "denial-of-service"],
                "disclosure_policy": "coordinated", "known_issue_policy": "excluded"
            }
        },
        "assets": [{
            "id": "order-contract", "name": "Order Contract", "status": "in-scope",
            "source_url": "https://example.org/program/scope#order",
            "eligible_release": "tag:4.3.4@abc123def456",
            "impacts": ["unauthorized asset loss", "signature bypass"],
            "max_reward": 50000, "reward_currency": "USDC",
            "allowed_environments": ["local-fork"],
            "prohibited_actions": ["public-network-testing"], "poc_required": True
        }]
    }


class ScopeDiffTests(unittest.TestCase):
    def test_ignores_retrieval_and_page_timestamps_without_material_change(self):
        old, new = snapshot(), snapshot()
        new["program"]["retrieved_at"] = "2026-10-21T10:00:00Z"
        new["program"]["page_last_updated"] = "2026-10-20"
        result = diff_snapshots(old, new)
        self.assertFalse(result["changed"])
        self.assertEqual(result["deltas"], [])

    def test_detects_program_scope_url_change(self):
        old, new = snapshot(), snapshot()
        new["program"]["source_url"] = "https://example.org/new-scope-page"
        result = diff_snapshots(old, new)
        self.assertTrue(any(d["path"] == "program.source_url" for d in result["deltas"]))

    def test_detects_new_asset(self):
        old, new = snapshot(), snapshot()
        new["assets"].append({"id": "new-vault", "name": "New Vault", "status": "in-scope", "source_url": "https://example.org/scope#vault"})
        result = diff_snapshots(old, new)
        self.assertTrue(result["changed"])
        self.assertEqual(result["deltas"][0]["kind"], "asset_added")
        self.assertTrue(result["deltas"][0]["material"])

    def test_detects_removed_asset(self):
        old, new = snapshot(), snapshot()
        new["assets"] = []
        result = diff_snapshots(old, new)
        self.assertEqual(result["deltas"][0]["kind"], "asset_removed")

    def test_detects_eligible_release_change(self):
        old, new = snapshot(), snapshot()
        new["assets"][0]["eligible_release"] = "tag:4.3.5@def456abc789"
        result = diff_snapshots(old, new)
        self.assertIn("assets[order-contract].eligible_release", [d["path"] for d in result["deltas"]])

    def test_detects_reward_change(self):
        old, new = snapshot(), snapshot()
        new["program"]["terms"]["reward_ceiling"] = 250000
        result = diff_snapshots(old, new)
        self.assertTrue(any(d["path"] == "terms.reward_ceiling" for d in result["deltas"]))

    def test_detects_deadline_shortening(self):
        old, new = snapshot(), snapshot()
        new["program"]["terms"]["report_deadline_hours"] = 12
        result = diff_snapshots(old, new)
        self.assertTrue(any(d["path"] == "terms.report_deadline_hours" for d in result["deltas"]))

    def test_detects_kyc_change(self):
        old, new = snapshot(), snapshot()
        new["program"]["terms"]["kyc_required"] = True
        result = diff_snapshots(old, new)
        self.assertTrue(any(d["path"] == "terms.kyc_required" for d in result["deltas"]))

    def test_detects_environment_and_prohibited_action_changes(self):
        old, new = snapshot(), snapshot()
        new["program"]["terms"]["allowed_environments"] = ["local"]
        new["program"]["terms"]["prohibited_actions"].append("fork-testing")
        result = diff_snapshots(old, new)
        paths = {d["path"] for d in result["deltas"]}
        self.assertIn("terms.allowed_environments", paths)
        self.assertIn("terms.prohibited_actions", paths)

    def test_list_order_does_not_trigger_change(self):
        old, new = snapshot(), snapshot()
        new["assets"][0]["impacts"].reverse()
        new["program"]["terms"]["prohibited_actions"].reverse()
        self.assertFalse(diff_snapshots(old, new)["changed"])

    def test_missing_critical_field_is_material_delta(self):
        old, new = snapshot(), snapshot()
        del new["assets"][0]["eligible_release"]
        result = diff_snapshots(old, new)
        delta = next(d for d in result["deltas"] if d["path"].endswith("eligible_release"))
        self.assertTrue(delta["material"])
        self.assertEqual(delta["after"], "NOT_RECORDED")

    def test_rejects_duplicate_asset_ids(self):
        old, new = snapshot(), snapshot()
        new["assets"].append(deepcopy(new["assets"][0]))
        with self.assertRaises(ValueError):
            diff_snapshots(old, new)

    def test_rejects_different_programs(self):
        old, new = snapshot(), snapshot()
        new["program"]["id"] = "other:program"
        with self.assertRaises(ValueError):
            diff_snapshots(old, new)

    def test_deltas_have_deterministic_order(self):
        old, new = snapshot(), snapshot()
        new["assets"][0]["eligible_release"] = "tag:4.3.5"
        new["program"]["terms"]["kyc_required"] = True
        new["program"]["terms"]["reward_ceiling"] = 200000
        first = diff_snapshots(old, new)
        self.assertEqual(first, diff_snapshots(old, new))
        self.assertEqual([d["path"] for d in first["deltas"]], sorted(d["path"] for d in first["deltas"]))


if __name__ == "__main__":
    unittest.main()
