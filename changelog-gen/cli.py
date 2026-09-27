"""
Git Changelog Generator - Command-Line Interface (CLI)
Usage:
  python -m changelog_gen.cli --output CHANGELOG.md
  python cli.py --since v1.0.0 --version-name v1.1.0
"""

import sys
import argparse
from pathlib import Path

# UTF-8 reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add current directory and parent to sys.path for flexible execution
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from generator import generate_full_changelog, get_latest_tag
except ImportError:
    try:
        from changelog_gen.generator import generate_full_changelog, get_latest_tag
    except ImportError:
        from src.bounties.changelog_gen.generator import generate_full_changelog, get_latest_tag


def main():
    parser = argparse.ArgumentParser(
        description="Automated Structured CHANGELOG Generator from Git History"
    )
    parser.add_argument("--repo", "-r", default=".", help="Path to git repository (default: current directory)")
    parser.add_argument("--since", "-s", help="Starting tag or commit ref (default: auto-detected latest tag)")
    parser.add_argument("--version-name", "-v", default="Unreleased", help="Version title (default: Unreleased)")
    parser.add_argument("--output", "-o", default="CHANGELOG.md", help="Destination file (default: CHANGELOG.md)")

    args = parser.parse_args()

    last_tag = args.since or get_latest_tag(cwd=args.repo)
    tag_info = f"since tag '{last_tag}'" if last_tag else "(entire git history)"
    print(f"[Changelog Gen] Scanning git commits {tag_info} ...", file=sys.stderr)

    try:
        md = generate_full_changelog(
            repo_path=args.repo,
            version=args.version_name,
            since_tag=args.since,
            output_path=args.output
        )
    except Exception as e:
        print(f"[ERROR] Failed to generate changelog: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[SUCCESS] Structured CHANGELOG.md generated successfully at: {Path(args.output).resolve()}", file=sys.stderr)
    print(md)


if __name__ == "__main__":
    main()
