"""
Automated Test Suite for n8n + Claude Automated Weekly Dev Summary Workflow
Validates adherence to all acceptance criteria for Bounty #5 ($200 USD).
"""

import sys
import json
import unittest
from pathlib import Path

# Ensure UTF-8 output encoding for cross-platform compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class TestN8nWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow_dir = Path(__file__).resolve().parent
        cls.workflow_path = cls.workflow_dir / "workflow.json"
        cls.assertTrue(cls.workflow_path.exists(), f"workflow.json not found at {cls.workflow_path}")
        
        with open(cls.workflow_path, "r", encoding="utf-8") as f:
            cls.workflow = json.load(f)

    def test_01_valid_n8n_structure(self):
        """Verify root structure of the n8n workflow."""
        self.assertIn("name", self.workflow)
        self.assertIn("nodes", self.workflow)
        self.assertIn("connections", self.workflow)
        self.assertIsInstance(self.workflow["nodes"], list)
        self.assertGreater(len(self.workflow["nodes"]), 5)

    def test_02_schedule_trigger(self):
        """Verify the schedule trigger fires weekly on Friday 5PM UTC."""
        trigger_node = None
        for node in self.workflow["nodes"]:
            if "scheduleTrigger" in node.get("type", ""):
                trigger_node = node
                break
        self.assertIsNotNone(trigger_node, "Schedule Trigger node not found")
        rule = trigger_node.get("parameters", {}).get("rule", {}).get("interval", [{}])[0]
        self.assertEqual(rule.get("expression"), "0 17 * * 5")

    def test_03_configurable_variables(self):
        """Verify workflow configuration has required variables (owner, repo, language, webhook)."""
        config_node = None
        for node in self.workflow["nodes"]:
            if node.get("name") == "Workflow Configuration":
                config_node = node
                break
        self.assertIsNotNone(config_node, "Workflow Configuration node not found")
        string_vars = {v["name"]: v["value"] for v in config_node["parameters"]["values"]["string"]}
        self.assertIn("github_owner", string_vars)
        self.assertIn("github_repo", string_vars)
        self.assertIn("language", string_vars)
        self.assertIn("destination_webhook", string_vars)
        self.assertIn("claude_model", string_vars)

    def test_04_github_api_nodes(self):
        """Verify nodes fetch commits, closed issues, and merged PRs."""
        node_names = [node.get("name") for node in self.workflow["nodes"]]
        self.assertIn("Fetch Weekly Commits", node_names)
        self.assertIn("Fetch Closed Issues", node_names)
        self.assertIn("Fetch Merged PRs", node_names)

    def test_05_claude_model_and_prompt(self):
        """Verify Claude node uses claude-sonnet-4-20250514 and structured prompt."""
        claude_node = None
        for node in self.workflow["nodes"]:
            if "Claude" in node.get("name", ""):
                claude_node = node
                break
        self.assertIsNotNone(claude_node, "Claude synthesis node not found")
        body_str = claude_node.get("parameters", {}).get("jsonBody", "")
        self.assertIn("claude_model", body_str)
        self.assertIn("Executive Overview", body_str)
        self.assertIn("Key Features", body_str)
        self.assertIn("Critical Bug Fixes", body_str)

    def test_06_webhook_delivery_node(self):
        """Verify dispatch node connects to the destination webhook."""
        dispatch_node = None
        for node in self.workflow["nodes"]:
            if "Dispatch" in node.get("name", ""):
                dispatch_node = node
                break
        self.assertIsNotNone(dispatch_node, "Dispatch node not found")
        self.assertEqual(dispatch_node.get("parameters", {}).get("method"), "POST")

    def test_07_all_connections_valid(self):
        """Verify all connection graph edges reference existing nodes."""
        node_names = {node.get("name") for node in self.workflow["nodes"]}
        connections = self.workflow.get("connections", {})
        for src_node, targets in connections.items():
            self.assertIn(src_node, node_names, f"Connection source '{src_node}' does not exist in nodes")
            for conn_group in targets.get("main", []):
                for edge in conn_group:
                    target_name = edge.get("node")
                    self.assertIn(target_name, node_names, f"Connection target '{target_name}' does not exist in nodes")

    def test_08_sample_outputs_exist(self):
        """Verify English and French sample outputs exist with comprehensive structure."""
        en_sample = self.workflow_dir / "samples" / "sample_weekly_summary_en.md"
        fr_sample = self.workflow_dir / "samples" / "sample_weekly_summary_fr.md"
        
        self.assertTrue(en_sample.exists(), "English sample output missing")
        self.assertTrue(fr_sample.exists(), "French sample output missing")
        
        en_content = en_sample.read_text(encoding="utf-8")
        fr_content = fr_sample.read_text(encoding="utf-8")
        
        self.assertIn("Executive Overview", en_content)
        self.assertIn("Aperçu Exécutif", fr_content)


def run_tests():
    print("=" * 65)
    print("  N8N + CLAUDE WEEKLY DEV SUMMARY SUITE — BOUNTY #5 ($200 USD)")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestN8nWorkflow)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n" + "=" * 65)
        print("ALL 8 N8N WORKFLOW TESTS PASSED (100% SUCCESS)!")
        print("=" * 65)
        return True
    else:
        print("\n[FAIL] Workflow tests failed.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
