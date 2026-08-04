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


## ADR-005: Monorepo structure — single repo with backend/ and frontend/ as siblings

**Date:** Week 1, Day 2
**Decision:** Keep backend (Django) and frontend (Next.js) in one git repository, as sibling folders (`backend/`, `frontend/`), rather than two independent repos.
**Options considered:**

- **Separate repos** (`tusupport-backend`, `tusupport-frontend`) — rejected for now. Solves a team-coordination problem (independent release cadences, separate CI/ownership) that doesn't exist for a solo developer. Would also complicate the single-VPS Docker Compose deployment target: one `docker-compose.yml` orchestrating both services is straightforward with sibling folders in one repo, awkward across repos (git submodules, or a third orchestration repo, or manual path coordination on the deploy server).
- **Monorepo (chosen)** — matches the deployment model (one `docker-compose.yml` at the repo root, referencing `./backend` and `./frontend` as sibling build contexts) and keeps end-to-end feature tracing (UI → API call → DRF view → model) within one `git log`, one editor window — directly supports the project's learning goal of seeing system seams clearly.
**Consequence:** Existing backend content (previously flat at repo root) was restructured into `backend/`, as a sub-step of the `feature/frontend-bootstrap` branch (per ADR-003's branch-granularity rule — this restructure only exists in service of adding the frontend, not as its own capability). `docker-compose.yml` stays at repo root, not inside either service folder, since it must "see" all sibling services to orchestrate them.
**Tradeoff accepted:** Frontend and backend dependency installs, version history, and (later) CI runs are entangled in one repo. Not a real cost at solo-developer, pre-production scale; would need revisiting if the project ever had separate frontend/backend teams with independent release cadences.


## ADR-006: Mentorship/build model — AI-implemented, human-reviewed (security-first) over hand-written-by-learner

**Date:** Week 1, Day 2
**Decision:** Shift the project's working model. Claude writes implementation-level code (syntax, boilerplate, component/view logic); James owns architecture decisions, security reasoning, and failure-mode analysis, and reviews every piece of generated code through an attacker-mindset lens before it's accepted. This supersedes the original "mentor, don't generate — have James write and debug everything himself" approach the project started with.
**Reasoning:** James's actual goal for this project is not hand-coding fluency. His career direction is web application security (analysis/pentesting) with AI-assisted ("vibe coded") application building as a secondary, income-oriented track — not full-time hand-implementation engineering. Given that, time spent manually typing JSX/boilerplate has a low return relative to time spent learning to read, question, and security-audit code — frontend or backend — regardless of who/what wrote it. The project remains valuable under this model specifically because it requires James to make every real judgment call (trust boundaries, what's deferred vs. fixed now, branch/commit discipline, what an attacker would try first) while offloading syntax-level typing, which is the part most likely to be commoditized by AI tooling regardless.
**Options considered:**

- **Hand-write everything (original model)** — rejected going forward. Optimizes for a skill (implementation fluency) James has deliberately decided not to prioritize, given his stated career direction.
- **AI writes, no review discipline ("pure vibe coding")** — rejected. Produces working-looking output with no guarantee of security or correctness; directly contradicts scope.md §10's engineering mindset checklist and the project's own audit-grade requirements (financial/payment data, multi-tenancy). Also fails to build the actual skill James wants (judging whether a system is secure/correct), since nothing gets questioned.
- **AI writes, human reviews with explicit security/architecture framing (chosen)** — matches James's stated target skill (diagnosing correctness/security/scalability in systems he didn't necessarily write line-by-line) and mirrors the real shape of his intended income path: reviewing and directing AI-generated builds for clients, not hand-typing them.
**Consequence:** From this point forward, code-level explanations in this project are framed around trust boundaries, attacker capability, and what could go wrong — not generic "best practice" narration. James is expected to interrogate generated code (e.g., "why is client-side validation insufficient here," "what would an attacker try first against this endpoint") rather than retype it. Judgment calls (branch strategy, what's deferred, what's in/out of scope per session) remain entirely James's to make and articulate.
**Tradeoff accepted:** This only stays safe if the review step is actually rigorous every time, not skipped when tired or rushed — an unreviewed AI-written endpoint is exactly the failure mode scope.md's "fail loud, not silent" principle exists to prevent. If review discipline slips, this model degrades into the rejected "pure vibe coding" option above. Also accepted: James's hand-implementation fluency (Django views, React syntax) will stay shallow relative to a traditional full-stack learner — a deliberate bet that this is the correct skill allocation given his stated 2026+ market read on AI and coding, not a guaranteed-correct one.


## ADR-007: No CAPTCHA on `/api/v1/leads/` — rate limiting alone is sufficient

**Date:** Week 1, Day 4
**Decision:** Do not add CAPTCHA to the lead-capture endpoint. Rate limiting (DRF `AnonRateThrottle`, 20/hour) is the complete control set for this endpoint's current risk profile.
**Reasoning:** Every security control has a cost (paid by all legitimate users, with certainty) and a benefit (threat prevented, weighted by its probability and impact). CAPTCHA's cost — friction and possible accessibility/UX failure on every single real visitor — is paid 100% of the time. The threat it would close beyond what rate limiting already covers (distributed, multi-IP bot submission) has a low-value payoff for an attacker: junk rows in an anonymous, pre-tenancy waitlist table, no money, no auth bypass. The cost is certain and continuous; the benefit is marginal and low-stakes. The asymmetry does not justify the control here.
**Options considered:**

- **Rate limiting + CAPTCHA** — rejected. Solves a threat (distributed bot abuse) whose worst case is low-value junk data, at a cost paid by every genuine visitor.
- **Rate limiting alone (chosen)** — matches blast radius; friction proportional to actual stakes.
**Consequence:** This verdict is endpoint-specific, not a blanket rule. Revisit explicitly if `/leads/` ever gains value to an attacker (e.g., signup grants a scarce resource), or for higher-stakes endpoints later in the project (auth/login, M-Pesa callback) — different blast radius, different verdict, same framework.


## ADR-008: Refresh token storage — HttpOnly cookie over localStorage

**Date:** Week 3, Day 2
**Decision:** Store the refresh token in an `HttpOnly; Secure; SameSite=Strict` cookie set by the backend, not in localStorage. The access token stays in localStorage temporarily — acceptable because it is short-lived (minutes).
**Reasoning:** localStorage is readable by any JavaScript on the page. A single XSS vulnerability anywhere on the frontend gives an attacker access to whatever is stored there. The refresh token is the high-value target — it is long-lived (days/weeks) and can be used to mint fresh access tokens indefinitely. An HttpOnly cookie is invisible to JavaScript entirely, closing the XSS theft vector. SameSite=Strict closes the CSRF vector that HttpOnly cookies introduce — the browser will not send the cookie on cross-origin requests.
**Options considered:**

- **localStorage for both tokens** — rejected for refresh token. XSS risk is unacceptable for a long-lived credential in a financial/welfare-data system.
- **HttpOnly cookie for refresh token (chosen)** — eliminates XSS theft. CSRF mitigated by SameSite=Strict. Requires backend to set the cookie via Set-Cookie header on login response.
**Why deferred:** Requires a backend change — Django must set the cookie on login and read it on token refresh, instead of passing it in JSON. This is a backend-day concern, not a frontend-day one.
**Consequence:** Current localStorage implementation for the refresh token is explicitly temporary. Must be replaced before any production deployment or payment integration begins (Phase 3 at the latest).
**Tradeoff accepted:** Until the backend change is made, the refresh token remains exposed to XSS. Acceptable at current stage — no real user data, no payment integration yet. Not acceptable past Phase 2.


## ADR-009: UI theming — CSS custom properties token system over

hardcoded Tailwind values

**Date:** Week 5, Day 2
**Decision:** Define all colours as CSS custom properties (variables)
in globals.css, extended into Tailwind via the theme config. Brand
colours are declared once and never repeated. Surface and text colours
are declared twice — once under :root (light mode) and once under
[data-theme="dark"] (dark mode).
**Options considered:**

- **Hardcoded Tailwind classes** (e.g. `bg-teal-600` directly in
  components) — rejected. Changing the brand colour later requires
  hunting every component. No single source of truth. Dark mode
  requires per-component overrides via `dark:` prefix, which scales
  poorly.
- **CSS custom properties token system (chosen)** — one edit in
  globals.css propagates to every component. Dark mode is a single
  `[data-theme="dark"]` attribute on the `<html>` tag. Brand colours
  never change between modes; only surfaces and text colours flip.

**Consequence:** All components must reference token classes
(`text-brand-primary`, `bg-surface-card`) not raw colour classes
(`text-teal-600`, `bg-white`). Raw colour classes are permitted only
inside globals.css itself where the tokens are defined.
**Tradeoff accepted:** Requires upfront wiring of tailwind.config.ts
and globals.css before components can use the token system. Until that
wiring is done (Week 5, Day 3), components use interim hardcoded
classes — a known temporary state, not a pattern to replicate.


## ADR-010: Explicit through model for Fundraiser↔Beneficiary M2M

**Date:** Week 7, Day 1
**Decision:** Use an explicit through model (FundraiserBeneficiary)
rather than Django's implicit ManyToManyField.
**Reasoning:** Implicit M2M gives the relationship but discards context
around it — who linked it, when, and why. Audit-grade systems need that
metadata.
**organization denormalized intentionally** — avoids JOIN overhead in
tenant-scoped queries; logged here so future schema auditors don't
treat it as an accidental normalization violation.
**status field deferred** — soft-disassociation implies a workflow
(who can remove, what happens to past contributions) that doesn't
exist yet. An unenforced field implies a guarantee the system doesn't give.


## Environment notes (non-architectural, but worth remembering)

- PostgreSQL 18+ Docker images require the data volume mounted at the parent directory `/var/lib/postgresql`, not the old-style `/var/lib/postgresql/data` — this supports version-namespaced data directories for future `pg_upgrade` operations.
