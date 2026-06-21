# tuSupport — Current Progress

> Snapshot of where the project stands right now. Overwrite this each session — do not append.

**Phase:** Foundation (Week 1 of 12)
**Last updated:** Week 1, Day 2 — in progress, stopped at a clean verified checkpoint
**Active branch:** `feature/frontend-bootstrap`

## Stack status

- **Backend:** Django 5.2 LTS + django-environ, now living in `backend/` (moved from repo root). Connected to Postgres, verified via `migrate`. Unchanged functionally since Day 1 close.
- **Database:** PostgreSQL 18, Docker Compose (`tusupport_postgres`), reachable at `localhost:5432`
- **Frontend:** Next.js 16.2.9 + TypeScript + Tailwind + App Router, scaffolded into `frontend/`, restructured to use `src/` layout (scaffolder's "recommended defaults" skipped this — fixed manually before first commit). Dev server verified running (`npm run dev`, Turbopack, ready in ~500ms) and rendering correctly in browser.

## Completed — Week 1, Day 2 (so far)

- Repo restructured into monorepo layout: `backend/` and `frontend/` as siblings at repo root, `docs/` untouched at root. See ADR-005.
- `docker-compose.yml` confirmed staying at repo root (must see both service folders to orchestrate them).
- Next.js scaffolded via `create-next-app` (TypeScript, Tailwind, App Router, ESLint all confirmed present).
- Manually corrected `src/` layout after scaffolder defaults skipped it — moved `app/` into `src/app/`, verified dev server still resolved it correctly post-move.
- `npm audit`: 2 moderate vulnerabilities in transitive `postcss` dependency (via `next`). Reasoned, deliberate deferral — fix would downgrade `next` 7 major versions to a canary build; project doesn't process untrusted CSS input, so exposure is effectively nil. Revisit only if `npm audit` ever flags something with real exposure given how input is actually handled.
- First real component created: `src/components/LandingHero.tsx`, rendered from `src/app/page.tsx` via the `@/*` import alias.
- **Bug encountered and resolved:** `@/*` alias failed to resolve (`tsconfig.json`'s `paths` mapping still pointed at repo-root-relative paths from before the manual `src/` move, never updated). Fixed by changing `"@/*": ["./*"]` to `"@/*": ["./src/*"]`. Root cause understood: Next.js auto-detects `src/`, but TypeScript's path aliasing is explicit config, not auto-detected — moving folders doesn't update it for you.

## In progress / next up — Week 1, Day 2 continued (or Day 3)

- Component architecture and state management proper (scope.md's stated Day 2 goals) — only the first single component exists so far; no shared layout, no navigation, no real page structure yet.
- Commit just made: "Add LandingHero component, fix tsconfig path alias for src/ layout" — still on `feature/frontend-bootstrap`, not yet merged.
- Standing reminder for Phase 3 (unchanged from Day 1): Celery org-context gap — pass `organization` explicitly as a task argument, fail loud if missing.
