# 📝 Git Changelog Generator

> **Bounty Deliverable:** GitHub Issue #1 ($50 USD via Opire)  
> **Repository:** `claude-builders-bounty/claude-builders-bounty`  
> **Purpose:** Automatically generates a structured `CHANGELOG.md` from git commit history following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.

---

## 🚀 Quick Setup (3 Steps or Fewer)

### Step 1: Run the Command
Generate `CHANGELOG.md` directly using Python or Bash:
```bash
# Python CLI:
python -m changelog_gen.cli --output CHANGELOG.md

# OR Bash script:
bash changelog-gen/changelog.sh CHANGELOG.md
```

### Step 2: (Optional) Specify Tag or Version
Generate notes for a specific version release since a git tag:
```bash
python -m changelog_gen.cli --since v1.0.0 --version-name v1.1.0
```

### Step 3: Use with Claude Code (`/generate-changelog`)
Copy [`SKILL.md`](SKILL.md) to your `.claude/skills/` directory and type `/generate-changelog` inside any Claude Code session.

---

## 🎯 Automatic Categorization
Commits are automatically grouped into:
- 🟢 **Added:** Features and additions (`feat:`, `add:`, `new:`)
- 🛠️ **Fixed:** Bug fixes and security patches (`fix:`, `bug:`, `patch:`)
- 🔄 **Changed:** Refactoring, performance improvements, updates (`refactor:`, `perf:`, `chore:`)
- 🗑️ **Removed:** Deprecations and removed features (`remove:`, `drop:`, `deprecate:`)

---

## 🧪 Sample Deliverable
See [`samples/sample_changelog.md`](samples/sample_changelog.md) for a tested sample output generated according to the Keep a Changelog standard.
