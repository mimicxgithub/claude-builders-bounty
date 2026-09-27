# Claude Code Destructive Bash Block Hook

> **Bounty Deliverable for [claude-builders-bounty #3](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/3)** ($100 USD Bounty)

A `pre-tool-use` security hook for **Claude Code** that intercepts dangerous bash commands before execution, preventing accidental data loss, schema corruption, and destructive git history overwrites.

---

## What It Blocks

| Destructive Pattern | Example Intercepted | Rationale |
|---|---|---|
| `rm -rf` | `rm -rf /` or `rm -r -f ./dist` | Prevents recursive directory purging. |
| `DROP TABLE` | `DROP TABLE users;` | Prevents permanent SQL table destruction. |
| `git push --force` | `git push origin main --force` | Protects remote commit history. |
| `TRUNCATE` | `TRUNCATE TABLE accounts` | Prevents non-rollback table wipes. |
| `DELETE FROM` (no WHERE) | `DELETE FROM customers;` | Blocks bulk purge; allowed if `WHERE` is present. |

---

## Installation (2 Commands)

```bash
mkdir -p ~/.claude/hooks
cp hooks/block_destructive.py ~/.claude/hooks/pre-tool-use-bash.py && chmod +x ~/.claude/hooks/pre-tool-use-bash.py
```

---

## Configuration

In your `~/.claude/settings.json` (or `~/.claude/hooks/hooks.json`):

```json
{
  "hooks": {
    "pre-tool-use": [
      {
        "matcher": "bash",
        "command": "python3 ~/.claude/hooks/pre-tool-use-bash.py"
      }
    ]
  }
}
```

---

## Audit Logging

Every intercepted command is automatically recorded to `~/.claude/hooks/blocked.log` with an ISO-8601 timestamp, command string, target project directory, and safety reason:

```text
[2026-09-27T13:08:15.123456+00:00] BLOCKED: Recursive Force Removal
  Command: rm -rf /var/data
  Directory: /workspace/project
  Reason: Indiscriminate recursive file deletion (rm -rf) risks catastrophic data loss.
------------------------------------------------------------
```

---

## Verification

Run the automated test suite:
```bash
python hooks/test_hook.py
```
