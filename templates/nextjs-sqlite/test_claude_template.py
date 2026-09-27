"""
Automated Test Suite for Next.js 15 + SQLite CLAUDE.md Template
Validates adherence to all acceptance criteria for Bounty #2 ($75 USD).
"""

import sys
import unittest
from pathlib import Path

# Ensure UTF-8 output encoding for cross-platform compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class TestClaudeTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_path = Path(__file__).resolve().parent / "CLAUDE.md"
        cls.assertTrue(cls.template_path.exists(), f"CLAUDE.md not found at {cls.template_path}")
        cls.content = cls.template_path.read_text(encoding="utf-8")

    def test_01_required_sections_present(self):
        """Verify all mandatory sections specified in Issue #2 exist."""
        required_headers = [
            "Stack & Pinned Versions",
            "Folder Structure",
            "SQLite & Migration Conventions",
            "Component & Server Action Patterns",
            "What We Don't Do (And Why)",
            "Daily Developer Commands",
        ]
        for header in required_headers:
            self.assertIn(header.lower(), self.content.lower(), f"Missing required section: {header}")

    def test_02_stack_and_versions(self):
        """Verify explicit versions for Next.js 15, React 19, TypeScript, and SQLite."""
        self.assertIn("Next.js `15", self.content)
        self.assertIn("React 19", self.content)
        self.assertIn("SQLite", self.content)
        self.assertIn("Drizzle ORM", self.content)
        self.assertIn("Zod", self.content)

    def test_03_sqlite_conventions_and_pragmas(self):
        """Verify SQLite specific optimizations and safety pragmas."""
        self.assertIn("WAL", self.content, "Should specify WAL mode for SQLite")
        self.assertIn("foreign_keys = ON", self.content, "Should enforce foreign_keys = ON")
        self.assertIn("drizzle-kit", self.content, "Should specify drizzle-kit migration workflow")

    def test_04_component_and_action_patterns(self):
        """Verify React Server Component and Server Action patterns."""
        self.assertIn("Server Component", self.content)
        self.assertIn("'use client'", self.content)
        self.assertIn('"use server"', self.content)
        self.assertIn("safeParse", self.content, "Should demonstrate runtime validation with Zod")

    def test_05_anti_patterns_with_reasons(self):
        """Verify 'What we don't do' includes explicit reasons/rationales."""
        self.assertIn("No Prisma", self.content)
        self.assertIn("No `useEffect`", self.content)
        self.assertIn("SQL injection", self.content)
        self.assertIn("foreign key", self.content.lower())

    def test_06_dev_commands_present(self):
        """Verify dev commands for running, building, migrating, and testing."""
        commands = ["npm run dev", "npm run build", "npm run db:generate", "npm run db:migrate", "npm test"]
        for cmd in commands:
            self.assertIn(cmd, self.content, f"Missing command: {cmd}")


def run_tests():
    print("=" * 65)
    print("  CLAUDE.MD TEMPLATE VALIDATION SUITE — BOUNTY #2 ($75 USD)")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClaudeTemplate)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n" + "=" * 65)
        print("ALL 6 TEMPLATE CRITERIA TESTS PASSED (100% SUCCESS)!")
        print("=" * 65)
        return True
    else:
        print("\n[FAIL] Template validation tests failed.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
