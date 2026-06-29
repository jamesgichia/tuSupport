**Last updated:** Week 2, Day 1 — closed
**Active branch:** `feature/fundraiser-model` (not yet merged to main)

## Completed — Week 2, Day 1

- New `fundraisers` Django app created and registered in `tusupport.settings.INSTALLED_APPS`.
- `Fundraiser` model built on `fundraisers/models.py`, inheriting `TenantScopedModel` (core.models) — confirmed via `\d fundraisers_fundraiser` in psql: `organization_id` is `bigint NOT NULL` with a working FK constraint to `core_organization`, auto-indexed.
- Field decisions reasoned through explicitly, not defaulted:
  - `organization` — FK via TenantScopedModel inheritance. One-to-many (Organization → Fundraiser) confirmed as the correct shape: supports both long-lived orgs running many fundraisers (e.g. a church) and one-off orgs auto-created for a single campaign (e.g. a funeral contribution) without changing the relationship type.
  - **No `current_amount` field.** Deliberately rejected a stored running total after tracing a concrete failure mode: a corrected/refunded contribution would desync a hand-maintained total with no error or trace. "Amount raised" will be calculated on demand from the future `Contribution` table once it exists — single source of truth, audit-grade per scope.md §2.1.
  - `goal_amount` — `DecimalField(max_digits=12, decimal_places=2)`, confirmed in Postgres as `numeric(12,2)` — never float, for financial precision.
  - `status` — `CharField` constrained via `TextChoices` (`draft`/`published`/`closed`), not free text. Prevents invalid/inconsistent state strings (e.g. `"Published"` vs `"published"`) from silently breaking status checks.
- Migration `fundraisers.0001_initial` generated, SQL reviewed before applying, applied successfully. Verified directly in `psql` via `\d fundraisers_fundraiser` — not just trusted on Django's say-so.
- Branch discipline (ADR-003) confirmed: all work done on `feature/fundraiser-model`, `main` untouched.
- Bug fixed along the way: `leads/views.py` was missing `from rest_framework.throttling import AnonRateThrottle`, causing a `NameError` on server start. Likely a regression from an incomplete commit/merge — worth a `git log -- leads/views.py` check to confirm how it happened, not yet done.

## Open items carried forward (unchanged from Week 1)

- Celery org-context gap (Phase 3) — pass `organization` explicitly as task argument.
- Per-process rate-limit counter — revisit when multiple workers/containers exist.
- Cross-org IDOR test for `Fundraiser` — **now unblocked**, since `Fundraiser` exists. Not written yet.
- Bug fixed along the way: `leads/views.py` was missing `from rest_framework.throttling import AnonRateThrottle`, causing a `NameError` on server start. Root cause confirmed by James — closed, not carried forward.

## Next up — Week 2, Day 2 (per scope.md weekly cycle: Frontend Client)

- Likely: Next.js UI work against the new `Fundraiser` model — but no API endpoint exists yet for `Fundraiser` (today was schema-only, by design). Confirm with James whether Day 2 needs a minimal `FundraiserListView`/serializer first, or whether frontend work this cycle targets something else entirely.
