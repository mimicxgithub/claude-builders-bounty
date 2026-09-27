# CLAUDE.md — Next.js 15 (App Router) + SQLite SaaS Project Guide

> **Core Philosophy:** Minimal abstraction, maximum type safety, sub-millisecond local SQLite queries, and strict React Server Component boundaries.

---

## 1. Stack & Pinned Versions

- **Framework:** Next.js `15.2.x` (App Router only, React 19.x)
- **Language:** TypeScript `5.7.x` (`strict: true`, `noImplicitAny: true`)
- **Database Engine:** SQLite via `@libsql/client` (Turso edge-ready) or `better-sqlite3` (local fast runtime)
- **ORM & Query Builder:** Drizzle ORM `0.39.x` + `drizzle-kit` (zero-overhead type safety, direct SQL execution)
- **Styling:** Tailwind CSS `v4.x` with CSS variables & `@tailwindcss/postcss`
- **Validation:** Zod `3.24.x` for all Server Action inputs, route params, and environment variables
- **Icons & UI:** Lucide React + Radix UI primitives (headless, zero unnecessary JS)
- **Auth (Optional):** Lucia Auth or Auth.js v5 (database-backed sessions in SQLite)

---

## 2. Opinionated Folder Structure

```text
├── app/                          # Next.js App Router root
│   ├── (auth)/                   # Route group: Authentication (login, register, reset)
│   │   ├── login/page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/              # Route group: Protected SaaS workspace
│   │   ├── dashboard/page.tsx
│   │   ├── settings/page.tsx
│   │   └── layout.tsx
│   ├── api/                      # Minimal edge webhooks (e.g. Stripe, Lemon Squeezy)
│   │   └── webhooks/stripe/route.ts
│   ├── layout.tsx                # Root layout with fonts & metadata
│   ├── page.tsx                  # Landing / marketing page (pure Server Component)
│   ├── globals.css               # Tailwind v4 theme variables
│   └── error.tsx                 # Client error boundary
├── actions/                      # Next.js Server Actions (all mutations live here)
│   ├── auth.actions.ts
│   └── project.actions.ts
├── components/
│   ├── ui/                       # Reusable dumb primitives (Button, Input, Card, Modal)
│   └── features/                 # Domain-specific composite components (ProjectList, MetricCard)
├── db/
│   ├── schema/                   # Drizzle table schemas (modular per domain)
│   │   ├── index.ts              # Schema aggregator
│   │   ├── users.ts              # Users, sessions, accounts
│   │   └── projects.ts           # Business domain tables
│   ├── migrations/               # Auto-generated SQL migration files from drizzle-kit
│   ├── client.ts                 # SQLite connection singleton (enforces PRAGMA foreign_keys = ON)
│   └── seed.ts                   # Local development seed script
├── lib/
│   ├── env.ts                    # Type-safe validated process.env via Zod
│   ├── safe-action.ts            # Type-safe Server Action wrapper with auth & validation
│   └── utils.ts                  # Pure utility functions (cn, formatCurrency, formatDate)
├── types/                        # Global ambient and cross-module TypeScript types
├── drizzle.config.ts             # Drizzle Kit migration configuration
└── tsconfig.json                 # Path aliases: @/* -> ./*
```

---

## 3. SQLite & Migration Conventions

### 3.1 Database Connection Singleton
SQLite in serverless or hot-reloading dev environments can exhaust file locks. Always use a global singleton:
```typescript
// db/client.ts
import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import * as schema from "./schema";

const globalForDb = globalThis as unknown as { sqlite: Database.Database | undefined };

const sqlite = globalForDb.sqlite ?? new Database(process.env.DATABASE_URL ?? "local.db");
sqlite.pragma("journal_mode = WAL");          // Write-Ahead Logging for high concurrency
sqlite.pragma("foreign_keys = ON");             // SQLite disables FKs by default; mandatory ON
sqlite.pragma("synchronous = NORMAL");         // Balanced durability and throughput

if (process.env.NODE_ENV !== "production") globalForDb.sqlite = sqlite;

export const db = drizzle(sqlite, { schema });
```

### 3.2 Schema Definition Rules
- Use `text("id").primaryKey().$defaultFn(() => crypto.randomUUID())` or NanoID for IDs (never auto-incrementing integers for public IDs).
- Timestamps: Always store as integer epoch milliseconds (`integer("created_at", { mode: "timestamp_ms" })`) or ISO-8601 strings.
- Foreign Keys: Always define `.references(() => otherTable.id, { onDelete: "cascade" })`.
- Indexes: Add explicit indexes on every foreign key column and query filter column.

### 3.3 Migration Workflow
- Never manually edit files in `db/migrations/`.
- Change schema in `db/schema/*.ts`.
- Run `npm run db:generate` to generate timestamped SQL migration file.
- Run `npm run db:migrate` to apply migrations locally.
- In production startup, run migrations programmatically or via CI before starting the container.

---

## 4. Component & Server Action Patterns

### 4.1 Server Components First
- Every component is a **Server Component** by default.
- Data fetching happens **directly in Server Components** by querying `db.query.*` or calling domain services.
- Never use `fetch('/api/...')` inside Server Components. Query the database directly — it's local SQLite, latency is <0.5ms.

### 4.2 Push `'use client'` to the Leaves
- Never mark an entire page or large container with `'use client'`.
- Wrap only the interactive controls (buttons, forms, dropdown toggles) with `'use client'`.
- Pass server-rendered JSX or server data as `children` / props into Client Components.

### 4.3 Server Actions for All Mutations
- Mutations must **never** be REST endpoints unless receiving external third-party webhooks (Stripe).
- Wrap actions in validation schemas using Zod:
```typescript
// actions/project.actions.ts
"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { db } from "@/db/client";
import { projects } from "@/db/schema";

const CreateProjectSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters").max(64),
  description: z.string().max(256).optional(),
});

export async function createProjectAction(formData: FormData) {
  const parsed = CreateProjectSchema.safeParse({
    name: formData.get("name"),
    description: formData.get("description"),
  });

  if (!parsed.success) {
    return { success: false, errors: parsed.error.flatten().fieldErrors };
  }

  const [created] = await db.insert(projects).values(parsed.data).returning();
  revalidatePath("/dashboard");
  return { success: true, data: created };
}
```

---

## 5. What We Don't Do (And Why)

| Anti-Pattern | Why We Forbid It | What We Do Instead |
|---|---|---|
| **No Prisma ORM** | Prisma's Rust engine binary introduces 100MB+ overhead, slow cold starts, and complex SQLite locking issues. | Use **Drizzle ORM**. It is pure TypeScript, lightweight (<50KB), outputs zero-abstraction SQL, and boots in <5ms. |
| **No `useEffect` data fetching** | Causes layout shift, network waterfalls, flash of unstyled loading states, and duplicate requests. | Fetch directly in **React Server Components** using `await db.query...`. |
| **No REST `/api` for internal mutations** | Adds redundant HTTP serialization, route boilerplate, and loses end-to-end type inference. | Use **Server Actions** (`"use server"`) with Zod schema validation. |
| **No raw SQL string concatenation** | Vulnerable to SQL injection attacks and breaks TypeScript compile-time type guarantees. | Use **Drizzle query builder** or parameterized `sql` template tags. |
| **No `any` or unchecked type assertions** | Defeats TypeScript's compiler and introduces silent runtime regressions. | Use strict types inferred directly from schema via `typeof schema.users.$inferSelect`. |
| **No unindexed foreign keys** | SQLite performs full table scans on `JOIN` and `CASCADE DELETE` without explicit indexes. | Always declare `index("fk_idx").on(table.userId)` on foreign key columns. |
| **No storing dates as locale strings** | Timezone ambiguity corrupts chronological sorting and range queries. | Store timestamps as UTC Unix epoch (`integer, { mode: "timestamp_ms" }`). |

---

## 6. Daily Developer Commands

```bash
# Development
npm run dev               # Start Next.js Turbopack dev server on http://localhost:3000
npm run build             # Build production bundle and check type errors
npm run start             # Run production server

# Database & Migrations
npm run db:generate       # Generate new SQL migration from schema updates
npm run db:migrate        # Apply pending SQL migrations to local SQLite database
npm run db:push           # Push schema directly to SQLite (rapid prototyping only)
npm run db:studio         # Launch Drizzle Studio GUI on http://localhost:4983
npm run db:seed           # Populate local SQLite with seed fixture data

# Quality & Testing
npm run lint              # Run Next.js ESLint / Biome checks
npm run typecheck         # Run tsc --noEmit to verify zero TypeScript errors
npm test                  # Run Vitest unit & integration test suite
```

---

## 7. Claude Code Operating Rules

When working in this repository:
1. **Always read schema first:** Before creating any UI or Action, inspect `db/schema/index.ts` to adhere to exact column names and relationships.
2. **Never install unvetted heavy packages:** Do not add Moment.js (use native `Intl`), Lodash (use native ES2024 methods), or Axios (use native `fetch`).
3. **Always validate inputs at the runtime boundary:** All Server Actions and API route handlers must validate input payloads with Zod before touching the database.
4. **Preserve Server Component boundaries:** If a component only renders UI from data, keep it as a Server Component. Do not add `"use client"` unless event listeners (`onClick`, `onChange`) or React client hooks (`useState`, `useRef`) are strictly required.
