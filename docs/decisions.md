# tuSupport — Architecture Decisions Log

> Append a new entry only when a real architectural fork-in-the-road decision gets made — not every session. Most sessions should add nothing here.

## ADR-001: Dockerized PostgreSQL over a local systemd cluster

**Date:** Week 1, Day 1
**Decision:** Run PostgreSQL via Docker Compose rather than the host's systemd-managed cluster.
**Reasoning:** Mirrors the project's stated production infrastructure (Docker is already the deployment tool in scope.md), gives a disposable/reproducible dev database for fast iteration during schema design, and matches existing Docker fluency.
**Tradeoff accepted:** no automatic start on boot — `docker compose up -d` must be run manually each session.

## ADR-002: Postgres image version pinning

**Date:** Week 1, Day 1
**Decision:** Pin to `postgres:18-alpine`, never `latest`.
**Reasoning:** Guarantees the dev environment matches whatever gets deployed to production months from now; `-alpine` minimizes attack surface and image size.

## ADR-003: Git workflow — GitHub Flow with feature-scoped branches

**Date:** Week 1, Day 1
**Decision:** Adopt GitHub Flow: `main` stays always in a known-good, deployable state. All active work happens on short-lived branches, merged back once complete. No `develop` branch, no release branches, no feature flags.
**Branch naming:** `feature/<short-description>` for new capability, `fix/<short-description>` for bug fixes — named after the capability being built, not the calendar day/week it was built on (curriculum pacing is tracked in PROGRESS.md, not in branch names).
**Branch granularity:** One branch = one cohesive capability that makes sense to merge as a single unit, not one work session. Sequentially-dependent sub-steps of a single foundation (e.g. tenancy decision → Django bootstrap → DB config) share one branch; genuinely separable capabilities get their own.
**Merge trigger:** A branch merges to `main` only once it (a) actually runs and has been verified working, not just "looks correct," and (b) doesn't violate scope.md §10's mindset checklist in a way that can be articulated (security, scalability, maintainability, multi-tenancy, fail-safety).
**Reasoning:** Solo-developer project, so team-coordination features (PR gates, parallel long-lived branches, release branches) solve a problem that doesn't exist yet. The real risk GitHub Flow addresses is temporal, not interpersonal: incomplete/unsafe work (e.g. a half-wired M-Pesa callback with no signature validation) must never sit on the branch that's assumed production-ready.
**Tradeoff accepted:** Requires slightly more discipline than committing straight to `main` — must remember to branch before starting new capability work, and must consciously decide when something is "merge-ready" rather than just committing as you go.


## ADR-004: Multi-tenancy enforcement — model-level (abstract base + custom manager) over convention-only or database-level RLS

**Date:** Week 1, Day 1
**Decision:** Enforce tenant isolation at the Django application layer: an abstract base model carrying an `organization` FK, paired with a custom manager whose `get_queryset()` automatically filters by the "current organization," read from a thread-local/context variable set by middleware at the start of every HTTP request.
**Options considered:**

- **Convention-only** (manual `.filter(organization=...)` on every queryset) — rejected. Fails silently: a single forgotten filter call leaks cross-tenant data with no error, no log entry, nothing to catch it. Unacceptable for financial/welfare-sensitive records.
- **Database-level (Postgres Row-Level Security)** — deferred, not rejected. Enforced by Postgres itself regardless of application code, making it the most bulletproof option in principle. Not adopted now because it requires Postgres-specific policy/session-variable setup that's a separate skill investment, disproportionate to where the project is today (no models exist yet). Worth revisiting as a defense-in-depth layer during a future Security & Hardening phase, on top of — not instead of — the model-level approach below.
- **Model-level + thread-local context (chosen)** — strong for the HTTP request/response cycle, which is currently 100% of the system's traffic. Standard, idiomatic pattern for Django multi-tenant SaaS apps. Makes the safe path the *default* path: a developer has to actively bypass the manager to leak data, rather than actively remember to add a filter.
**Known gap, deliberately deferred:** thread-local context is set by Django middleware, which only runs during the HTTP request/response cycle. Celery background workers (planned for Phase 3 — async M-Pesa callback handling) never go through Django middleware and will have no value in that thread-local. If unaddressed, this risks either a crash (acceptable — loud, recoverable) or, worse, a silent no-op (unacceptable — e.g. a payment confirmation silently matching zero rows, with no record that money was received). **This is not solved today.** The anticipated fix, to be revisited when Celery is actually introduced: pass the organization explicitly as a task argument rather than relying on thread-local context inside Celery tasks. Flagging now so it isn't a surprise in Phase 3.
**Reasoning:** Matches scope.md §10's "can it fail safely?" test better than convention-only, at a setup cost appropriate to the project's current stage. RLS remains the stronger long-term option and is not discarded, only sequenced later.


## Environment notes (non-architectural, but worth remembering)

- PostgreSQL 18+ Docker images require the data volume mounted at the parent directory `/var/lib/postgresql`, not the old-style `/var/lib/postgresql/data` — this supports version-namespaced data directories for future `pg_upgrade` operations.
