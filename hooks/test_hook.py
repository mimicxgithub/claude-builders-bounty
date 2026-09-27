"""
Automated Test Suite for Claude Code Destructive Bash Block Hook
Validates adherence to all acceptance criteria for Bounty #3 ($100 USD).
"""

import sys
import os
import json
import tempfile
import unittest
import subprocess
from pathlib import Path

# Ensure UTF-8 output encoding for cross-platform compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add current directory and parent to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from block_destructive import check_command
except ImportError:
    from hooks.block_destructive import check_command


class TestDestructiveHook(unittest.TestCase):
    def test_01_blocks_rm_rf_variants(self):
        """Verify rm -rf and its argument permutations are blocked."""
        patterns = [
            "rm -rf /tmp/data",
            "rm -fr ./node_modules",
            "rm -r -f build/",
            "rm --recursive --force cache/",
            "sudo rm -rf /var/log",
        ]
        for cmd in patterns:
            blocked, rule, _ = check_command(cmd)
            self.assertTrue(blocked, f"Expected '{cmd}' to be blocked.")
            self.assertEqual(rule, "Recursive Force Removal")

    def test_02_blocks_drop_table(self):
        """Verify DROP TABLE SQL statements are blocked."""
        patterns = [
            "DROP TABLE users;",
            'sqlite3 db.sqlite "drop table accounts;"',
            "psql -c 'DROP TABLE transactions'",
        ]
        for cmd in patterns:
            blocked, rule, _ = check_command(cmd)
            self.assertTrue(blocked, f"Expected '{cmd}' to be blocked.")
            self.assertEqual(rule, "SQL DROP TABLE")

    def test_03_blocks_git_force_push(self):
        """Verify git force push commands are blocked."""
        patterns = [
            "git push origin main --force",
            "git push -f origin feature-branch",
            "git push origin +master",
        ]
        for cmd in patterns:
            blocked, rule, _ = check_command(cmd)
            self.assertTrue(blocked, f"Expected '{cmd}' to be blocked.")
            self.assertEqual(rule, "Git Force Push")

    def test_04_blocks_truncate(self):
        """Verify TRUNCATE statements are blocked."""
        patterns = [
            "TRUNCATE TABLE session_logs;",
            "TRUNCATE users",
            'psql -d app -c "TRUNCATE orders;"',
        ]
        for cmd in patterns:
            blocked, rule, _ = check_command(cmd)
            self.assertTrue(blocked, f"Expected '{cmd}' to be blocked.")
            self.assertEqual(rule, "SQL TRUNCATE")

    def test_05_blocks_delete_without_where(self):
        """Verify DELETE FROM without WHERE clause is blocked."""
        patterns = [
            "DELETE FROM customers;",
            "DELETE FROM orders",
            'sqlite3 app.db "DELETE FROM logs;"',
        ]
        for cmd in patterns:
            blocked, rule, _ = check_command(cmd)
            self.assertTrue(blocked, f"Expected '{cmd}' to be blocked.")
            self.assertEqual(rule, "SQL DELETE Without WHERE Clause")

    def test_06_allows_safe_delete_with_where(self):
        """Verify targeted DELETE FROM WITH a WHERE clause is allowed."""
        safe_deletes = [
            "DELETE FROM customers WHERE id = 42;",
            "DELETE FROM sessions WHERE expires_at < NOW();",
            'sqlite3 app.db "DELETE FROM temp_files WHERE created_at < 1000;"',
        ]
        for cmd in safe_deletes:
            blocked, rule, _ = check_command(cmd)
            self.assertFalse(blocked, f"Expected safe delete '{cmd}' to be allowed, but blocked under {rule}.")

    def test_07_allows_normal_bash_commands(self):
        """Verify typical developer bash commands are never hindered."""
        normal_commands = [
            "git status",
            "git commit -m 'feat: add login page'",
            "git push origin feature-branch",
            "npm run dev",
            "npm test",
            "ls -la",
            "cat package.json",
            "rm temp.txt",
            "mkdir -p src/components",
            "python -m unittest",
        ]
        for cmd in normal_commands:
            blocked, rule, _ = check_command(cmd)
            self.assertFalse(blocked, f"Expected '{cmd}' to be allowed, but blocked under {rule}.")

    def test_08_cli_execution_and_logging(self):
        """Verify subprocess execution, exit codes, and audit logging."""
        script_path = Path(__file__).resolve().parent / "block_destructive.py"
        with tempfile.TemporaryDirectory() as tmpdir:
            test_log = Path(tmpdir) / "test_blocked.log"
            env = dict(os.environ, CLAUDE_HOOKS_LOG_PATH=str(test_log))

            # Test dangerous command -> exit code 1
            proc = subprocess.run(
                [sys.executable, str(script_path), "rm -rf /test/dir"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 1, "Dangerous command should return exit code 1")
            self.assertIn("Command Execution Blocked", proc.stderr)
            self.assertTrue(test_log.exists(), "Blocked log file should be created")

            log_content = test_log.read_text(encoding="utf-8")
            self.assertIn("rm -rf /test/dir", log_content)
            self.assertIn("Recursive Force Removal", log_content)

            # Test Claude Code JSON payload -> exit code 1
            json_payload = json.dumps({
                "event": "pre-tool-use",
                "tool_name": "bash",
                "tool_input": {"command": "DROP TABLE users;"},
                "project_path": "/var/app"
            })
            proc_json = subprocess.run(
                [sys.executable, str(script_path)],
                input=json_payload,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(proc_json.returncode, 1)
            self.assertIn("SQL DROP TABLE", proc_json.stderr)

            # Test safe command -> exit code 0
            proc_safe = subprocess.run(
                [sys.executable, str(script_path), "npm run build"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(proc_safe.returncode, 0, "Safe command should return exit code 0")


def run_tests():
    print("=" * 65)
    print("  CLAUDE CODE DESTRUCTIVE HOOK SUITE — BOUNTY #3 ($100 USD)")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDestructiveHook)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n" + "=" * 65)
        print("ALL 8 HOOK CRITERIA TESTS PASSED (100% SUCCESS)!")
        print("=" * 65)
        return True
    else:
        print("\n[FAIL] Hook criteria tests failed.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
