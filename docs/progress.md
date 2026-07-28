**Last updated:** Week 6, Day 2 — Frontend Day

## Current state

30 tests passing. Two commits on main.

## What shipped today

- Beneficiary management page — admin-only, silent redirect for non-admins
- UniqueConstraint on national_id per org — was documented as done in Week 6
  Day 1 but never existed in model or migrations; caught and fixed today
- Duplicate beneficiary record cleaned up from dev data

## Architecture decisions made

- Option B on beneficiary visibility: dual serializer approach retained —
  members will see limited public fields through fundraiser pages (Week 7),
  not blocked entirely. Backend already made this decision correctly.
- Frontend category values aligned to backend model choices:
  funeral/disaster not bereavement/emergency

## Audit findings

- UniqueConstraint gap: progress.md documented constraint as shipped;
  Beneficiary._meta.constraints was []. Documentation outpaced implementation.
- Missing import 500: Beneficiary model/serializer not imported in views.py
  caused unhandled 500 on POST — same failure class as Week 4 PermissionDenied
  gap. Broken control, loud failure, invisible to user.

## Known gaps — carried forward

- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] Rate limit test coverage: Week 6 Thursday
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Fundraiser <-> Beneficiary M2M: Week 7
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs;
      no central auth state — flagged, not blocking
