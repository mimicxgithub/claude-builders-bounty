#!/usr/bin/env python3
"""
Claude Code Pre-Tool-Use Hook: Block Destructive Bash Commands
Acceptance Criteria:
  1. Blocks: rm -rf, DROP TABLE, git push --force, TRUNCATE, DELETE FROM without WHERE.
  2. Logs blocked commands to ~/.claude/hooks/blocked.log (timestamp, command, project path).
  3. Displays explicit warning to Claude explaining why the command was blocked.
  4. Does not interfere with normal bash commands.
"""

import sys
import os
import re
import json
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 output encoding for cross-platform compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Default log file path; configurable via env var for testing
DEFAULT_LOG_PATH = Path.home() / ".claude" / "hooks" / "blocked.log"
LOG_FILE = Path(os.environ.get("CLAUDE_HOOKS_LOG_PATH", str(DEFAULT_LOG_PATH)))

# Dangerous pattern rules with human-readable rationale
DESTRUCTIVE_RULES = [
    {
        "name": "Recursive Force Removal",
        "pattern": re.compile(
            r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|-[a-zA-Z]*r\s+-[a-zA-Z]*f|--recursive\s+--force|--force\s+--recursive)\b",
            re.IGNORECASE
        ),
        "reason": "Indiscriminate recursive file deletion (rm -rf) risks catastrophic data loss."
    },
    {
        "name": "SQL DROP TABLE",
        "pattern": re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
        "reason": "Destructive SQL table deletion destroys database structures and records permanently."
    },
    {
        "name": "Git Force Push",
        "pattern": re.compile(r"\bgit\s+push\s+.*(--force|-f\b|\+[a-zA-Z0-9_\-/]+)", re.IGNORECASE),
        "reason": "Force-pushing overwrites remote git commit history and can delete team collaborators' commits."
    },
    {
        "name": "SQL TRUNCATE",
        "pattern": re.compile(r"\bTRUNCATE(\s+TABLE)?\s+[a-zA-Z0-9_.]+", re.IGNORECASE),
        "reason": "SQL TRUNCATE wipes entire table contents without transactional rollback."
    },
    {
        "name": "SQL DELETE Without WHERE Clause",
        "pattern": re.compile(r"\bDELETE\s+FROM\s+[a-zA-Z0-9_.]+(\s*;|\s*$|\s+(?!WHERE\b))", re.IGNORECASE),
        "reason": "SQL DELETE statement without a WHERE filter clause will purge all records in the table."
    }
]


def check_command(command: str):
    """
    Evaluates command against destructive rules.
    Returns (is_blocked: bool, rule_name: str, reason: str).
    """
    cleaned = command.strip()
    
    # Special check for DELETE FROM with WHERE clause
    if re.search(r"\bDELETE\s+FROM\b", cleaned, re.IGNORECASE):
        if re.search(r"\bWHERE\b", cleaned, re.IGNORECASE):
            # Safe DELETE with WHERE clause
            pass
        else:
            return True, "SQL DELETE Without WHERE Clause", "SQL DELETE statement without a WHERE filter clause will purge all records in the table."

    for rule in DESTRUCTIVE_RULES:
        if rule["name"] == "SQL DELETE Without WHERE Clause":
            continue
        if rule["pattern"].search(cleaned):
            return True, rule["name"], rule["reason"]

    return False, None, None


def log_blocked(command: str, rule_name: str, reason: str, project_path: str):
    """Appends an entry to the blocked commands log file."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        now_utc = datetime.now(timezone.utc).isoformat()
        log_line = (
            f"[{now_utc}] BLOCKED: {rule_name}\n"
            f"  Command: {command}\n"
            f"  Directory: {project_path}\n"
            f"  Reason: {reason}\n"
            f"{'-' * 60}\n"
        )
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[Hook Warning] Failed to write to {LOG_FILE}: {e}", file=sys.stderr)


def inspect_payload(payload_str: str, project_dir: str = None):
    """
    Parses Claude Code hook event or raw command string.
    Returns (command, project_path).
    """
    project_path = project_dir or os.getcwd()
    cmd = payload_str.strip()

    # Try parsing as JSON Claude Code hook payload
    if cmd.startswith("{") and cmd.endswith("}"):
        try:
            data = json.loads(cmd)
            tool_input = data.get("tool_input", {})
            if isinstance(tool_input, dict):
                cmd = tool_input.get("command", "")
            elif isinstance(tool_input, str):
                cmd = tool_input
            project_path = data.get("project_path") or data.get("cwd") or project_path
        except json.JSONDecodeError:
            pass

    return cmd, project_path


def main():
    raw_input = ""
    if len(sys.argv) > 1:
        raw_input = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        raw_input = sys.stdin.read()

    if not raw_input.strip():
        sys.exit(0)

    command, project_path = inspect_payload(raw_input)
    if not command.strip():
        sys.exit(0)

    is_blocked, rule_name, reason = check_command(command)

    if is_blocked:
        log_blocked(command, rule_name, reason, project_path)

        print(
            f"\n⛔ [CLAUDE CODE SECURITY HOOK] Command Execution Blocked!\n"
            f"────────────────────────────────────────────────────────────\n"
            f"Violation     : {rule_name}\n"
            f"Attempted Cmd : {command}\n"
            f"Target Dir    : {project_path}\n"
            f"Safety Reason : {reason}\n"
            f"Log Reference : {LOG_FILE}\n"
            f"────────────────────────────────────────────────────────────\n"
            f"To protect against accidental repository or database destruction,\n"
            f"this command was aborted. If this was intentional, perform it\n"
            f"manually outside of Claude Code.\n",
            file=sys.stderr
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
