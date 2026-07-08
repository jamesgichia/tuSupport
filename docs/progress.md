**Last updated:** Week 3, Day 1 — Monday Backend day closed

## Completed today

**URL restructure**

- Flat `/api/v1/fundraisers/` deleted (attack surface reduction)
- Replaced with `/api/v1/organizations/<int:org_id>/fundraisers/`
- `org_id` now explicitly declared on every request

**IDOR fix — both read and write paths**

- `get_membership_or_404()` introduced as single enforcement point
- Reads `org_id` from URL, verifies against Membership table
- Returns 404 on mismatch — never 403 (no information leakage)
- Both `get_queryset()` and `create()` now go through this gate

**Role-based permission**

- `create()` now checks `membership.role == ADMIN` before proceeding
- Plain members blocked with 403 — they can read, not write
- Role check lives in `create()` only, not in `get_membership_or_404()`
  (members must still be able to list fundraisers)

**All three Week 3 merge blockers closed**

- Write-IDOR test: passing
- LoginRateThrottle enforcement test: passing
- Role permission test: passing

**Test pollution fix**

- LoginRateThrottle was bleeding across test classes
- Fixed via `unittest.mock.patch` on `allow_request` in RolePermissionTest
- `tearDown()` guarantees patcher stops regardless of test outcome

## Key principles reinforced today

- Attack surface reduction ≠ fail-loud — different principles, different audit line items
- 404 vs 403: existence of a resource must not be confirmed to non-members (information disclosure)
- Single point of enforcement: one gate, not two inline copies
- Test-first loop: write test → confirm failure → fix → confirm pass
- Test pollution: throttle state persists across tests unless explicitly patched

## Next up — Week 3, Day 2 (Tuesday Frontend)

- Org picker flow: login returns JWT + org list
- Frontend stores active org as UI state (not in JWT)
- Every request declares org via URL
- CSRF tradeoff discussion when HttpOnly cookie for refresh token introduced
