**Last updated:** Week 2, Day 5 — Friday Review closed
**Active branch:** main (stable, no new features added today)

## Completed — Week 2, Day 5

Five-layer Friday audit conducted across:
- Database & Schema
- Models & Multi-tenancy
- API Views & Serializers
- Authentication & Authorization
- Tests

## Findings — Gaps Identified (not bugs, not emergencies)

### Layer 1: Database & Schema
- `unique_together` on Membership prevents duplicate memberships only
- Does NOT prevent role escalation — a member self-promoting to admin
  is unblocked at the database level; must be enforced at the API view layer
- This is a Privilege Escalation risk (OWASP API Top 10)
- No fix needed today — membership management endpoints not built yet
- Fix lands when those endpoints are built: only an existing org admin
  can change another user's role

### Layer 2: Models & Multi-tenancy
- `abstract = True` on `TenantScopedModel` confirmed correct —
  no real table, just a blueprint donating fields to child models
- `NotImplementedError` on `get_queryset()` confirmed correct —
  Celery gap (Phase 3) remains the known consequence, deliberately deferred
- No action needed — Layer 2 is solid

### Layer 3: API Views & Serializers
- `perform_create()` uses `.first()` to get user's org membership —
  silent wrong-org selection if user belongs to multiple orgs
- Root cause: URL structure `/api/v1/fundraisers/` carries no org context
- Fix: URL must become `/api/v1/organizations/{id}/fundraisers/`
  so org is declared explicitly on every request
- Server then verifies: JWT (identity) + URL org ID (intent)
  + Membership (authorization) — all three must align
- After login, frontend must fetch org list, show org picker,
  store chosen org, inject org ID into every subsequent request URL
- Backend remains stateless — frontend carries active org context
- This is a URL redesign — deferred to Week 3 frontend auth wiring session

### Layer 4: Authentication & Authorization
- JWT config solid: 15-min access (small blast radius),
  7-day refresh, ROTATE_REFRESH_TOKENS=True (replay attack protection)
- LoginRateThrottle gap confirmed: in-memory throttle multiplies
  by Gunicorn worker count in production — known, deferred to Phase 3 Redis
- No new findings — Layer 4 holds

### Layer 5: Tests
- Existing IDOR read test: solid, adversarial, written correctly
- Three missing tests identified — become Week 3 merge blockers:
  1. POST cross-org IDOR test (can user_a create in org_b?)
  2. LoginRateThrottle enforcement test (does 6th attempt return 429?)
  3. Role-based create permission test (can a plain member create?)

## Week 3 Merge Blockers (nothing merges until these exist)

1. Missing IDOR write test
2. Missing throttle enforcement test
3. Missing role permission test
4. URL restructure: `/api/v1/organizations/{id}/fundraisers/`

## Next up — Week 3

- Monday: Write the three missing security tests first (test-first rule)
- Monday: Fix `perform_create()` — org from URL, not `.first()`
- Tuesday: Frontend auth wiring — JWT storage, org picker flow
  (access token in JS memory, refresh token in HttpOnly cookie)
- CSRF tradeoff discussion when HttpOnly cookies are introduced
