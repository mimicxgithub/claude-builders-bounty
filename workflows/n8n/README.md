# n8n + Claude Automated Weekly Dev Summary Workflow

> **Bounty Deliverable for [claude-builders-bounty #5](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/5)** ($200 USD Bounty)

A production-ready [n8n](https://n8n.io) workflow that automatically compiles a repository's weekly activity (commits, closed issues, merged pull requests) via the GitHub REST API, generates an executive narrative developer digest using **Claude** (`claude-sonnet-4-20250514`), and dispatches the formatted report via Discord or Slack webhooks.

---

## Architecture Overview

```text
[Schedule Trigger] (Friday 5:00 PM UTC)
        │
        ▼
[Workflow Configuration] (Owner, Repo, Language, Webhook)
        │
        ▼
[Calculate Date Range] (Generates 7-day ISO window)
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
[Fetch Commits]       [Fetch Closed Issues]   [Fetch Merged PRs]
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               ▼
                    [Aggregate Activity Data]
                               ▼
               [Claude API Narrative Synthesis]
             (Model: claude-sonnet-4-20250514)
                               ▼
                   [Format Webhook Payload]
                               ▼
                [Dispatch to Discord / Slack]
```

---

## Setup in 5 Steps or Fewer

### Step 1: Import Workflow into n8n
- Open your n8n web instance (cloud or self-hosted: `http://localhost:5678`).
- In the top navigation, click **Workflows** → **Add Workflow** → **Import from File...**
- Select [`workflow.json`](workflow.json).

### Step 2: Configure Environment Credentials
Set your Anthropic / Claude API key in your n8n environment variables (or `.env` file):
```bash
ANTHROPIC_API_KEY="sk-ant-api03-..."
```
*(Alternatively, you can supply your API key directly in the HTTP Request node headers).*

### Step 3: Configure Target Repository & Webhook
Double-click the **Workflow Configuration** node and set:
- `github_owner`: e.g. `claude-builders-bounty`
- `github_repo`: e.g. `claude-builders-bounty`
- `destination_webhook`: Your Discord or Slack incoming webhook URL
- `language`: `EN` for English, or `FR` for French
- `days_back`: `7` (default)

### Step 4: Test Run the Workflow
Click **Test step** on the *Schedule Trigger* node or click **Execute Workflow** at the bottom of the canvas. The workflow will query GitHub, synthesize the activity with Claude, and post the narrative report to your webhook channel.

### Step 5: Activate Schedule
Toggle the **Active** switch in the top-right corner to `Active`. The workflow will automatically fire every Friday at 17:00 UTC!

---

## Sample Outputs

- 📄 **English Digest:** [`samples/sample_weekly_summary_en.md`](samples/sample_weekly_summary_en.md)
- 📄 **French Digest:** [`samples/sample_weekly_summary_fr.md`](samples/sample_weekly_summary_fr.md)

---

## Automated Validation

Run the automated validation test suite:
```bash
python workflows/n8n/test_workflow.py
```
