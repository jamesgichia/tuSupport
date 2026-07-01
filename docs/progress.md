**Last updated:** Week 2, Day 2 — closed
**Active branch:** `feature/fundraiser-model` (not yet merged to main)

## Completed — Week 2, Day 2

- `fundraisers/serializers.py` built with explicit field allow-list.
  `organization` deliberately excluded — never client-writable.
  `status`, `id`, `created_at` marked read-only.

- `FundraiserListCreateView` built in `fundraisers/views.py`:
  - GET: public, unauthenticated, filtered to `status='published'` only
  - POST: requires authentication, org-scoped via `Membership`
  - Overrides `create()` entirely — not just `perform_create()` — to
    bypass DRF's default `serializer.save()` which routes through
    `TenantManager` and raises `NotImplementedError`

- URL wired at `/api/v1/fundraisers/` via `tusupport/urls.py`
  → `fundraisers/urls.py`

- `Membership` model built in `core/models.py`:
  - Join table: `User` ↔ `Organization`
  - `role` field: `TextChoices` (admin/member)
  - `unique_together` on `(user, organization)` — database-enforced,
    prevents duplicate memberships
  - References `settings.AUTH_USER_MODEL` not a hardcoded import —
    survives a future custom User model
  - Migration reviewed via `sqlmigrate` before applying — FK constraints
    and unique constraint confirmed in raw SQL

- `FundraiserList` Server Component built in
  `src/components/FundraiserList.tsx`:
  - Fetches `GET /api/v1/fundraisers/` at render time (server-side)
  - Handles empty state cleanly
  - Wired into `src/app/page.tsx` alongside `LandingHero`/`EmailSignup`
  - Verified live in browser — correctly shows "No fundraisers available
    yet." (only fundraiser in DB is `draft`, correctly hidden)

## Real gaps surfaced today (by running the system, not guessing)

- `TenantManager.get_queryset()` is a deliberate unimplemented stub.
  Any feature needing real tenant-scoped queries will hit the same
  `NotImplementedError` until middleware + real filtering logic is built.
  Today's endpoints bypass it deliberately via `_base_manager` (GET)
  and `Fundraiser(...).save()` (POST).

- No authentication system exists at all — no login endpoint, no JWT,
  no token issuance. POST was tested via Django's `Client.force_login()`
  (valid for logic testing, not a substitute for real auth).

- No signup/onboarding flow — nothing creates `Membership` rows
  organically. Today's test membership was manually seeded via shell.

- No custom `User` model exists. Django's default `auth.User` is in use
  with no `organization` field — the `Membership` table is the only
  User↔Organization link.

## Open items carried forward

- Identity & Access Management not built yet — JWT auth, login endpoint,
  registration flow — this is the most pressing foundational gap
- Real `TenantManager` filtering logic + middleware (ADR-004 implementation)
- IDOR test for `Fundraiser` — unblocked now, not yet written
- Celery org-context gap (Phase 3) — unchanged
- Per-process rate-limit counter — unchanged

## Next up — Week 2, Day 3 (Integration Layer)

- Build JWT authentication: login endpoint, token issuance
- This unblocks: real POST testing via curl/Postman, frontend auth flow,
  and every future feature that assumes a logged-in user exists
