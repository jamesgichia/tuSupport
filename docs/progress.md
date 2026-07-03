**Last updated:** Week 2, Day 4 — closed
**Active branch:** main (feature/fundraiser-model merged)

## Completed — Week 2, Day 4

- Wrote IDOR cross-org test in `fundraisers/tests.py`
- Test failed first — confirmed live cross-tenant data leak via `_base_manager`
- Fixed `TenantManager` in `core/models.py`:
  - `get_queryset()` still raises `NotImplementedError` (ADR-004 alarm preserved)
  - Added `for_org(organization)` — explicit, opt-in tenant filtering
- Fixed `FundraiserListCreateView.get_queryset()`:
  - Replaced `_base_manager` bypass with `Fundraiser.objects.for_org(org)`
  - Returns `.none()` if user has no membership (safe default)
- IDOR test passes — merge blocker cleared
- `feature/fundraiser-model` merged to main

## Security reasoning established this session

- IDOR = authenticated but not authorized — the system knew who you were,
  not what you were allowed to see
- `404` is correct for cross-tenant access, not `403` — `403` leaks that
  the resource exists, enabling ID enumeration by attackers
- `_base_manager` bypasses all custom manager logic — raw unfiltered DB access
- `for_org()` as a named method keeps filtering opt-in — `get_queryset()`
  auto-fires in admin/shell/Celery where no org context exists
- Test-first security: write the test → confirm the bug → fix the code →
  confirm the fix. Never the other way around.

## Open items carried forward

- Frontend auth flow not yet wired (access token in memory +
  refresh token in HttpOnly cookie)
- TenantManager middleware (thread-local org context) — still not built;
  for_org() is the current explicit alternative
- No user registration endpoint — new users seeded via Django shell
- Celery org-context gap — Phase 3, unchanged
- Redis shared rate-limit backend — production concern, unchanged

## Next up — Week 3

- Frontend auth wiring: connect JWT flow to Next.js
  (access token in JS memory, refresh token in HttpOnly cookie)
- CSRF tradeoff discussion when HttpOnly cookies are introduced
