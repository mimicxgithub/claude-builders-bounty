"""
Git Changelog Generator - Core Logic
Extracts commits from git history, auto-categorizes into Added/Fixed/Changed/Removed,
and generates Keep-a-Changelog compliant markdown.
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple


def run_git(args: List[str], cwd: str = ".") -> Tuple[int, str]:
    """Runs a git command and returns (exit_code, output)."""
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return res.returncode, res.stdout.strip()
    except Exception as e:
        return 1, str(e)


def get_latest_tag(cwd: str = ".") -> Optional[str]:
    """Retrieves the most recent git tag, or None if no tags exist."""
    code, out = run_git(["describe", "--tags", "--abbrev=0"], cwd=cwd)
    if code == 0 and out:
        return out
    return None


def get_commits_since(since_ref: Optional[str] = None, cwd: str = ".") -> List[Dict[str, str]]:
    """
    Fetches git commit logs since a specific tag/commit ref, or full history.
    Returns list of dicts: {"hash": ..., "author": ..., "date": ..., "subject": ...}
    """
    # Format: hash|author|date|subject
    git_format = "%h|%an|%as|%s"
    git_args = ["log", f"--format={git_format}"]

    if since_ref:
        git_args.append(f"{since_ref}..HEAD")

    code, out = run_git(git_args, cwd=cwd)
    if code != 0 or not out:
        return []

    commits = []
    for line in out.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0].strip(),
                "author": parts[1].strip(),
                "date": parts[2].strip(),
                "subject": parts[3].strip()
            })
    return commits


def categorize_commit(subject: str) -> str:
    """
    Categorizes commit message following Keep a Changelog / Conventional Commits standard:
    - Added: feat, add, new, create
    - Fixed: fix, bug, patch, resolve
    - Removed: remove, delete, drop, deprecate
    - Changed: refactor, update, perf, docs, chore, style, test, other
    """
    clean = subject.strip().lower()

    # Added
    if re.match(r"^(feat|feature|add|new|create)(\(.*?\))?:", clean) or any(clean.startswith(w) for w in ["add ", "feat: ", "feature: ", "new "]):
        return "Added"

    # Fixed
    if re.match(r"^(fix|bug|patch|resolve|hotfix)(\(.*?\))?:", clean) or any(clean.startswith(w) for w in ["fix ", "fix: ", "bugfix: ", "patch: "]):
        return "Fixed"

    # Removed
    if re.match(r"^(remove|delete|drop|deprecate)(\(.*?\))?:", clean) or any(clean.startswith(w) for w in ["remove ", "delete ", "drop "]):
        return "Removed"

    # Changed (default bucket for refactor, perf, update, docs, chore)
    return "Changed"


def clean_commit_subject(subject: str) -> str:
    """Strips conventional commit prefix for cleaner release notes."""
    cleaned = re.sub(r"^(feat|fix|refactor|perf|docs|chore|style|test|build|ci)(\(.*?\))?:\s*", "", subject, flags=re.IGNORECASE)
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned.strip()


def build_changelog_section(
    commits: List[Dict[str, str]],
    version: str = "Unreleased",
    date_str: Optional[str] = None
) -> str:
    """Generates Keep a Changelog Markdown for a list of commits."""
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    categories = {
        "Added": [],
        "Fixed": [],
        "Changed": [],
        "Removed": []
    }

    for c in commits:
        cat = categorize_commit(c["subject"])
        cleaned_sub = clean_commit_subject(c["subject"])
        entry = f"- {cleaned_sub} ([`{c['hash']}`](https://github.com/commit/{c['hash']})) - @{c['author']}"
        categories[cat].append(entry)

    md_lines = [f"## [{version}] - {date_str}"]

    has_entries = False
    for cat_name in ["Added", "Fixed", "Changed", "Removed"]:
        items = categories[cat_name]
        if items:
            has_entries = True
            md_lines.append(f"\n### {cat_name}")
            md_lines.extend(items)

    if not has_entries:
        md_lines.append("\n*No significant changes recorded.*")

    return "\n".join(md_lines)


def generate_full_changelog(
    repo_path: str = ".",
    version: str = "Unreleased",
    since_tag: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    End-to-end changelog generator.
    Fetches commits since last tag, formats into Keep a Changelog standard,
    and optionally writes to file.
    """
    last_tag = since_tag or get_latest_tag(cwd=repo_path)
    commits = get_commits_since(since_ref=last_tag, cwd=repo_path)

    header = """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
"""

    section = build_changelog_section(commits, version=version)
    full_md = f"{header}\n{section}\n"

    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(full_md, encoding="utf-8")

    return full_md
