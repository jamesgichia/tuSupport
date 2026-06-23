# tuSupport — Current Progress

> Snapshot of where the project stands right now. Overwrite this each session — do not append.

**Phase:** Foundation (Week 1 of 12)
**Last updated:** Week 1, Day 2 — closed, all stated scope.md goals met
**Active branch:** `feature/frontend-bootstrap`

## Stack status

- **Backend:** Django 5.2 LTS + django-environ, living in `backend/`. Connected to Postgres, verified via `migrate`. Unchanged functionally since Day 1 close.
- **Database:** PostgreSQL 18, Docker Compose (`tusupport_postgres`), reachable at `localhost:5432`
- **Frontend:** Next.js 16.2.9 + TypeScript + Tailwind + App Router, in `frontend/`, `src/` layout. Two components live: `LandingHero` (Server Component, static) and `EmailSignup` (Client Component, stateful form). Both rendered from `src/app/page.tsx`. `layout.tsx` metadata corrected to reflect tuSupport, not scaffold defaults.

## Completed — Week 1, Day 2 (closed)

- Repo restructured into monorepo layout (`backend/`, `frontend/` siblings); see ADR-005.
- Next.js scaffolded, `src/` layout corrected after scaffolder defaults skipped it.
- `tsconfig.json` path-alias bug (`@/*` pointing at repo-relative root instead of `src/`) diagnosed and fixed — root cause: Next.js auto-detects `src/`, TypeScript path aliasing does not.
- `npm audit`: 2 moderate transitive `postcss` vulnerabilities, deliberately deferred (fix requires a 7-major-version `next` downgrade; project has no untrusted-CSS exposure).
- `LandingHero.tsx` created — first component, Server Component by default (no interactivity needed).
- `layout.tsx` metadata fixed (title/description now describe tuSupport, not `create-next-app` defaults). Nav and footer deliberately deferred — both judged premature with a single page and nothing concrete to put in either yet; same reasoning applied to both rather than treated as separate calls.
- `EmailSignup.tsx` created — first Client Component (`"use client"`), first real `useState` usage (`email`, `submitted`, `error`). Built with explicit security framing: client-side regex validation is UX-only, not a security control; backend must independently re-validate any future submission, since requests can bypass the form entirely (e.g., via Burp/dev tools replay). `TODO` comment marks the unwired submission endpoint as a known, deliberate gap — not yet connected to a backend, by design (endpoint work belongs to Day 3 — Integration Layer — not Day 2).
- **Mentorship model shift, mid-session:** moved from "James hand-writes all code" to "Claude implements, James owns architecture/security judgment and reviews all generated code through an attacker-mindset lens." See ADR-006. Reflects James's actual goal (security/pentesting skill + AI-assisted app-building for income) rather than hand-coding fluency.

## Day 2 scope.md checklist — final status

- Next.js UI development — ✅ done
- Component architecture — ✅ done (Server/Client Component split is the real architectural line, not cosmetic)
- State management — ✅ done (`useState`, trust-boundary reasoning attached)

## In progress / next up

- Day 3 (Integration Layer, per scope.md): wiring `EmailSignup`'s submission to a real Django endpoint — this is where the deferred backend validation gap gets closed, not before.
- Standing reminder for Phase 3 (unchanged since Day 1): Celery org-context gap — pass `organization` explicitly as a task argument, fail loud if missing.
- Going forward, expect every new piece of code (frontend or backend) to come with an explicit attacker-mindset pass as part of its introduction, per ADR-006 — not appended afterward as an extra step.
