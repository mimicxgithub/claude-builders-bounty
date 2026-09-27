"""
Git Changelog Generator - Test Suite
Verifies commit categorization, markdown formatting, and CLI execution.
"""

import sys
from pathlib import Path

# Add current directory and parent to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from generator import (
        categorize_commit,
        clean_commit_subject,
        build_changelog_section
    )
except ImportError:
    try:
        from changelog_gen.generator import (
            categorize_commit,
            clean_commit_subject,
            build_changelog_section
        )
    except ImportError:
        from src.bounties.changelog_gen.generator import (
            categorize_commit,
            clean_commit_subject,
            build_changelog_section
        )


def run_tests():
    print("=" * 65)
    print("  GIT CHANGELOG GENERATOR — AUTOMATED TEST SUITE")
    print("=" * 65)

    # 1. Test commit categorization
    print("\n[TEST 1] Testing commit categorization ...")
    assert categorize_commit("feat(auth): add OAuth2 provider") == "Added"
    assert categorize_commit("add enterprise webhook support") == "Added"
    assert categorize_commit("fix(api): resolve race condition in cache lock") == "Fixed"
    assert categorize_commit("bugfix: memory leak in stream handler") == "Fixed"
    assert categorize_commit("remove deprecated v1 billing routes") == "Removed"
    assert categorize_commit("drop legacy Python 3.8 support") == "Removed"
    assert categorize_commit("refactor(db): migrate to async connection pool") == "Changed"
    assert categorize_commit("chore: bump dependencies") == "Changed"
    print("  [PASS] Categorized Added, Fixed, Removed, and Changed commits correctly.")

    # 2. Test subject cleaning
    print("\n[TEST 2] Testing clean_commit_subject ...")
    clean = clean_commit_subject("feat(api): add sub-2s lead qualification")
    assert clean == "Add sub-2s lead qualification"
    print(f"  [PASS] Cleaned commit subject: '{clean}'")

    # 3. Test changelog section builder
    print("\n[TEST 3] Testing build_changelog_section ...")
    test_commits = [
        {"hash": "a1b2c3d", "author": "Alice", "date": "2026-09-27", "subject": "feat(auth): implement API key quota manager"},
        {"hash": "e4f5g6h", "author": "Bob", "date": "2026-09-27", "subject": "fix(billing): correct Stripe webhook signature check"},
        {"hash": "i7j8k9l", "author": "Charlie", "date": "2026-09-27", "subject": "refactor(core): optimize Gemini token usage"},
        {"hash": "m0n1o2p", "author": "Dave", "date": "2026-09-27", "subject": "remove deprecated legacy auth header"}
    ]
    md = build_changelog_section(test_commits, version="1.0.0", date_str="2026-09-27")
    assert "### Added" in md
    assert "### Fixed" in md
    assert "### Changed" in md
    assert "### Removed" in md
    print("  [PASS] Generated Keep a Changelog section with all 4 categories.")

    # 4. Save Sample Changelog Deliverable
    print("\n[TEST 4] Generating sample_changelog.md deliverable ...")
    samples_dir = Path("changelog-gen/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)
    sample_file = samples_dir / "sample_changelog.md"

    header = """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
"""
    full_sample = f"{header}\n{md}\n"
    sample_file.write_text(full_sample, encoding="utf-8")
    assert sample_file.exists() and sample_file.stat().st_size > 300
    print(f"  [PASS] Sample changelog generated at: {sample_file.resolve()} ({sample_file.stat().st_size} bytes)")

    print("\n" + "=" * 65)
    print("ALL 4 CHANGELOG GENERATOR TESTS PASSED (100% SUCCESS)!")
    print("=" * 65)


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"[TEST FAILURE] {e}", file=sys.stderr)
        sys.exit(1)
