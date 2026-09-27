# Opinionated Next.js 15 + SQLite SaaS Template (`CLAUDE.md`)

> **Bounty Deliverable for [claude-builders-bounty #2](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/2)** ($75 USD Bounty)

This directory provides a battle-tested, highly opinionated `CLAUDE.md` configuration designed for greenfield SaaS applications built with **Next.js 15 (App Router)** and **SQLite** (Turso / better-sqlite3 + Drizzle ORM).

---

## Why This Template?

Most `CLAUDE.md` files are too vague or generic. This template is **strictly opinionated with explicit rationales**:
1. **Next.js 15 App Router & React 19:** Enforces React Server Components (RSC) by default and pushes `'use client'` strictly to interactive leaves.
2. **SQLite Performance:** Enforces `WAL` journal mode and `PRAGMA foreign_keys = ON`. SQLite queries execute in sub-millisecond local latency (<0.5ms).
3. **Drizzle ORM over Prisma:** Zero-overhead type safety, instant cold starts, and zero heavy Rust engine binaries.
4. **Server Actions with Zod:** End-to-end type safety for mutations without REST boilerplate.
5. **Clear Anti-Patterns Table:** Explicitly tells Claude what **NOT** to do (e.g. no `useEffect` for data fetching, no unindexed foreign keys, no `any`).

---

## Quickstart (Greenfield Project)

### Step 1: Copy `CLAUDE.md`
Copy `CLAUDE.md` directly into the root directory of your new Next.js 15 project:
```bash
cp templates/nextjs-sqlite/CLAUDE.md /path/to/your-saas-project/CLAUDE.md
```

### Step 2: Initialize Your Stack
```bash
npx create-next-app@latest my-saas --typescript --tailwind --app --src-dir=false --import-alias="@/*"
cd my-saas
npm install drizzle-orm better-sqlite3 zod lucide-react
npm install -D drizzle-kit @types/better-sqlite3
```

### Step 3: Start Claude Code
Launch Claude Code in your project root:
```bash
claude
```
Claude Code will automatically detect `CLAUDE.md` and adhere to every architectural convention, schema migration workflow, and Server Component boundary without asking clarifying questions.

---

## Validation & Verification

Run the automated test suite to verify that `CLAUDE.md` satisfies all acceptance criteria:
```bash
python templates/nextjs-sqlite/test_claude_template.py
```
