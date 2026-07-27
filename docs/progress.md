**Last updated:** Week 5, Day 5 — Review & Stabilization

---

## Current state — end of Week 5, Day 5

All Week 5 work audited. 30/30 tests passing.
No new code committed today — audit and planning session.

---

## Friday audit findings — Week 5 additions

**Layer 1 — Database & Schema**
- contributor_name as free-text allows spoofing for registered users
- Fix: serializer should derive name from user account when authenticated

**Layer 2 — Models & Multi-tenancy**
- NULL/NULL contribution state possible — violates audit-grade requirement
- Fix: cross-field CHECK constraint at database level + serializer validation

**Layer 3 — API Views & Serializers**
- ChoiceField on payment_method correctly stops invalid values at serializer
- No action required

**Layer 4 — Auth & Authorization**
- Per-user rate limiting does not stop distributed account abuse
- Deferred to Week 8 hardening — not public-facing yet

**Layer 5 — Tests**
- Rate limiting has no test coverage
- Fix: add test file with cache.clear() in setUp — Week 6 Thursday

---

## Week 6 plan

Monday    — Beneficiary module (backend: model, serializer, endpoints)
            + contributor_name spoofing fix
            + NULL/NULL CHECK constraint + migration
Tuesday   — Beneficiary UI (list + create) + dark mode toggle
Wednesday — Wire beneficiary frontend to API, end-to-end flow test
Thursday  — Security pass on beneficiary endpoints + rate limit tests
Friday    — 5-layer audit + Week 7 planning + progress.md update

---

## Known gaps — carried forward

- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] Rate limit test coverage: Week 6 Thursday
- [ ] contributor_name spoofing fix: Week 6 Monday
- [ ] NULL/NULL CHECK constraint: Week 6 Monday
