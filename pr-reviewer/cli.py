"""
Claude PR Reviewer Agent - Command-Line Interface (CLI)
Usage:
  python -m pr_reviewer.cli --pr https://github.com/owner/repo/pull/123
  python -m pr_reviewer.cli --diff sample.diff --output review.md
  python -m pr_reviewer.cli --pr https://github.com/owner/repo/pull/123 --post-comment
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding for cross-platform compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pr_reviewer.reviewer import (
    PRReviewer,
    fetch_pr_diff,
    load_local_diff
)


def main():
    parser = argparse.ArgumentParser(
        description="Claude PR Reviewer Agent - Automated Structured PR Code Reviews"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr", "-p", help="Full GitHub PR URL (e.g. https://github.com/owner/repo/pull/123)")
    group.add_argument("--diff", "-d", help="Path to local diff file (e.g. changes.diff)")

    parser.add_argument("--output", "-o", help="Optional output path to save the generated Markdown review")
    parser.add_argument("--post-comment", action="store_true", help="Post review comment directly to the GitHub PR (requires GITHUB_TOKEN)")
    parser.add_argument("--token", help="GitHub Personal Access Token (defaults to GITHUB_TOKEN env var)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON analysis instead of Markdown")
    parser.add_argument("--model", default="gemini-3.5-flash-lite", help="LLM model to use (default: gemini-3.5-flash-lite)")

    args = parser.parse_args()

    reviewer = PRReviewer(model=args.model)

    try:
        if args.pr:
            print(f"[Claude Reviewer] Fetching PR diff from {args.pr} ...", file=sys.stderr)
            diff_text, metadata = fetch_pr_diff(args.pr, token=args.token)
        else:
            print(f"[Claude Reviewer] Loading local diff from {args.diff} ...", file=sys.stderr)
            diff_text, metadata = load_local_diff(args.diff)
    except Exception as e:
        print(f"[ERROR] Failed to load diff: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[Claude Reviewer] Analyzing changes (+{metadata.get('additions')}/-{metadata.get('deletions')}) with {args.model} ...", file=sys.stderr)
    try:
        review_output = reviewer.analyze_diff(diff_text, metadata)
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        formatted_result = json.dumps(review_output.model_dump(), indent=2)
    else:
        formatted_result = reviewer.format_markdown(review_output, metadata)

    # Print to stdout
    print(formatted_result)

    # Save to file if requested
    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(formatted_result, encoding="utf-8")
        print(f"\n[Claude Reviewer] Review saved to: {out_p.resolve()}", file=sys.stderr)

    # Post to PR if requested
    if args.post_comment:
        if not args.pr:
            print("[WARN] --post-comment requires --pr URL. Skipping comment post.", file=sys.stderr)
        else:
            print(f"[Claude Reviewer] Posting review comment to {args.pr} ...", file=sys.stderr)
            success = reviewer.post_comment_to_pr(args.pr, formatted_result, token=args.token)
            if success:
                print("[SUCCESS] Comment posted to GitHub PR!", file=sys.stderr)
            else:
                print("[ERROR] Failed to post comment to GitHub PR.", file=sys.stderr)


if __name__ == "__main__":
    main()
