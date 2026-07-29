**Last updated:** Week 6, Day 3 — Integration Day

## Current state

30 tests passing. On branch feature/beneficiary-integration.

## What was verified today

- Beneficiary list endpoint confirmed hitting real backend (not mock data)
- CORS configured correctly — credentials passing through
- Dual serializer security verification via direct curl simulation:
  - Admin token: returns full fields including national_id, phone_number,
    internal_notes
  - Member token: returns stripped public fields only (display_name,
    category, verification_status, created_at)
  - Backend enforces field-level privacy independently of frontend redirect
- Identified logout gap: no token blacklist, refresh token stays valid
  after logout

## Decisions made

- public_description field on Beneficiary deferred to Week 7 — member-facing
  display context belongs alongside Fundraiser<->Beneficiary junction build
- Token blacklisting deferred to Thursday Security Day — backend auth
  changes grouped together for cohesion

## Known gaps — carried forward

- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] Token blacklisting: logout endpoint + simplejwt blacklist app — Thursday
- [ ] public_description on Beneficiary: Week 7
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] Rate limit test coverage: Week 6 Thursday
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Fundraiser <-> Beneficiary M2M: Week 7
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs;
      no central auth state — flagged, not blocking
