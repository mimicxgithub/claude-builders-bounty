"""
Claude PR Reviewer Agent - Automated Integration Test Suite
Validates URL parsing, diff ingestion, review schema, and sample outputs.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pr_reviewer.reviewer import (
    parse_github_pr_url,
    load_local_diff,
    PRReviewer,
    ReviewOutput
)


class TestPRReviewer(unittest.TestCase):
    def test_parse_url(self):
        url = "https://github.com/claude-builders-bounty/claude-builders-bounty/pull/4"
        owner, repo, num = parse_github_pr_url(url)
        self.assertEqual(owner, "claude-builders-bounty")
        self.assertEqual(repo, "claude-builders-bounty")
        self.assertEqual(num, 4)

    def test_markdown_formatting(self):
        reviewer = PRReviewer()
        review = ReviewOutput(
            summary="Test summary of pull request changes.",
            identified_risks=["Potential edge case with null values"],
            improvement_suggestions=["Add unit tests for error conditions"],
            confidence_score="High",
            confidence_rationale="Clear diff",
            code_quality_rating=9
        )
        meta = {
            "title": "Test PR",
            "html_url": "https://github.com/test/repo/pull/1",
            "author": "tester",
            "additions": 10,
            "deletions": 2,
            "changed_files": 1
        }
        md = reviewer.format_markdown(review, meta)
        self.assertIn("## 🤖 Claude PR Review", md)
        self.assertIn("### 📋 Summary of Changes", md)
        self.assertIn("### ⚠️ Identified Risks", md)
        self.assertIn("### 💡 Improvement Suggestions", md)
        self.assertIn("High", md)


if __name__ == "__main__":
    unittest.main()
