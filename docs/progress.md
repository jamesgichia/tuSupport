**Last updated:** Week 1, Day 5 — closed
**Active branch:** `main` (no new branches opened this session — audit/review only, no code changes)

## Completed — Week 1, Day 5 (closed)

- Day 5 reframed as an orientation + guided walkthrough session (James's first Friday Review), rather than an independent audit. From Week 2's Friday onward, James owns the scope.md §10 audit unsupervised.
- Full scope.md §10 mindset checklist walked across all Week 1 components (TenantManager/TenantScopedModel, Lead model+view, CORS, rate limiting, ADR-007). Verdict: passes, with two known gaps (already logged: per-process throttle counter, Celery org-context) plus one newly surfaced soft spot below.
- Resolved the standing open question from Day 4: **does TenantManager protect against IDOR via URL parameters (e.g. `/api/v1/fundraisers/42/`)?** Answer: yes, *conditionally* — Django routes `.get()`/`.filter()`/`.all()` through `get_queryset()` by default, so the custom manager's filtering applies. Protection breaks only if a developer bypasses the manager entirely (raw SQL, `._base_manager`). Action item: once `Fundraiser` exists in Week 2+, write an explicit cross-org test (login as Org A, request Org B's object ID, assert 404) rather than trusting this reasoning alone.
- Reinforced and generalized the "fail loud, not silent" principle one level up: documentation (ADR log) is itself only a *convention*, not an enforcement mechanism — it protects future developers only if they read it before acting, which nothing in a normal coding workflow guarantees. Real enforcement requires the same loud-failure ladder applied to process: tests + CI gates that catch violations even if the docs are never opened.

## New soft spot identified (not yet fixed, low urgency)

- `Lead` model's tenancy-exclusion (no `organization` FK, doesn't inherit `TenantScopedModel`) is correct and documented in decisions.md, but only documented — nothing in the model file itself warns a future developer who adds an `organization` FK to `Lead` later that they'd also need to switch its manager. Low risk today (no FK exists yet), but cheap to close: a one-line code comment at the point of future modification, not just buried in the ADR log. Defer to whenever `Lead` is next touched — not urgent enough to action now.

## In progress / next up

- Week 2 begins: Phase 2 scope per scope.md §6 — Core Features (fundraiser management first, per natural dependency order).
- Standing reminder, unchanged: Celery org-context gap (Phase 3) — pass `organization` explicitly as a task argument, fail loud if missing.
- Standing reminder, unchanged: per-process rate-limit counter gap — revisit when multiple workers/containers are introduced.
- Standing reminder, new: write the cross-org object-access test (IDOR check) once `Fundraiser` model exists — don't treat today's reasoning as a substitute for an actual test.
- From next Friday: James runs the scope.md §10 audit independently; Claude's role shifts to pushing back on the reasoning, not demonstrating it first.
