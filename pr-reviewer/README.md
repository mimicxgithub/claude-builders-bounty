# 🤖 Claude PR Reviewer Agent

> **Bounty Deliverable:** GitHub Issue #4 ($150 USD via Opire)  
> **Repository:** `claude-builders-bounty/claude-builders-bounty`  
> **Purpose:** Automated code reviewer agent that inspects Pull Request diffs and posts structured, actionable Markdown review comments.

---

## ✨ Features
- 🚀 **Dual Intake:** Review live PRs directly via URL (`--pr`) or local patch files (`--diff`).
- 🎯 **Strict Structured Output:** Enforces 4 mandatory sections:
  1. **Summary of Changes:** 2–3 sentences highlighting what changed and the author's intent.
  2. **Identified Risks:** Scrutinizes security vulnerabilities, breaking changes, race conditions, and performance regressions.
  3. **Improvement Suggestions:** Actionable, concrete suggestions to improve test coverage, typing, or architecture.
  4. **Confidence Score:** High / Medium / Low with explicit reasoning and a 1–10 code quality rating.
- 💬 **GitHub Automated Commenting:** Optional `--post-comment` flag posts the formatted review directly to the PR thread.
- ⚡ **Sub-2-Second Analysis:** Powered by high-speed multimodal LLM reasoning (`gemini-3.5-flash-lite` / `claude-sonnet-4`).
- 🔄 **GitHub Actions Ready:** Drop-in `.github/workflows/pr-review.yml` for automated CI/CD code reviews on every opened/updated PR.

---

## 🚀 Quick Start (Setup in 4 Steps)

### Step 1: Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Configure Environment
Copy or add your API keys to `.env` or export to your shell:
```bash
# Required for LLM reasoning:
export GEMINI_API_KEY="your-gemini-or-claude-api-key"

# Optional (required only for private repos or posting comments):
export GITHUB_TOKEN="ghp_your_github_token"
```

### Step 3: Run via CLI

#### Option A: Review a Live GitHub Pull Request
```bash
python -m pr_reviewer.cli --pr https://github.com/owner/repo/pull/123
```

#### Option B: Review a Local Diff File
```bash
git diff main > changes.diff
python -m pr_reviewer.cli --diff changes.diff --output review.md
```

#### Option C: Review & Automatically Post Comment to PR
```bash
python -m pr_reviewer.cli \
  --pr https://github.com/owner/repo/pull/123 \
  --post-comment \
  --token "$GITHUB_TOKEN"
```

### Step 4: Add to GitHub Actions CI/CD
Copy [`.github/workflows/claude-pr-review.yml`](.github/workflows/claude-pr-review.yml) into your target repository's `.github/workflows/` directory and configure `GEMINI_API_KEY` in your GitHub repository secrets.

---

## 🧪 Tested Deliverables on Real GitHub Pull Requests

Real review outputs generated against live pull requests on `claude-builders-bounty/claude-builders-bounty` are committed in the `samples/` directory:
- 📄 [Sample 1 Review (PR #4555)](samples/sample_pr1_output.md): Review of *Claude PR Review Agent TypeScript CLI submission*.
- 📄 [Sample 2 Review (PR #4554)](samples/sample_pr2_output.md): Review of *Automated Weekly Dev Summary n8n workflow submission*.

---

## 📋 Sample Markdown Output Structure
```markdown
## 🤖 Claude PR Review

### 📋 Summary of Changes
This pull request modifies the core authentication pipeline, adding OAuth2 bearer token verification and updating database connection pooling settings.

---

### ⚠️ Identified Risks
- Unhandled exception when token expires during long-running background tasks.
- In-memory session dictionary is not synchronized across horizontal worker instances.

---

### 💡 Improvement Suggestions
- Wrap token verification in a try/except block that returns HTTP 401 with standard error format.
- Replace local in-memory session cache with Redis or database-backed session table.

---

### 🎯 Review Metadata
- **Confidence Score:** 🟢 **High** (Diff is clean, contains unit tests, and isolated to auth module)
- **Code Quality Rating:** **8 / 10**
- **Changes Analyzed:** +124 / -18 lines across 3 file(s)
```

---

## ⚖️ License
MIT License. Built for the open-source developer community.
