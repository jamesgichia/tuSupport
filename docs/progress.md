**Last updated:** Week 4, Day 4 — Security & Hardening Day closed

---

## Current state — end of Week 4

All four weeks of foundation and core contribution work are complete.
Backend is fully tested (20/20). Frontend contribution flow is integrated and verified.
The full OWASP API Security Top 10 has been audited against the current surface.

---

## Completed — Week 4, Day 4

**OWASP API Security Top 10 — full surface audit**

- Mapped all 8 active endpoints against OWASP API Top 10
- API1 — IDOR: clean across all endpoints; membership update, fundraiser detail,
  and contributions are all tenant-scoped with 404-not-403 enforcement
- API2 — Authentication: clean; JWT + HttpOnly cookie in place;
  `Secure` flag deferred pending HTTPS (known gap, logged)
- API3 — Property-level auth: clean; `contributor` and `fundraiser` are both
  server-injected in perform_create(), not client-controlled
- API5 — Function-level auth: bug found and fixed — `PermissionDenied` was not
  imported in fundraisers/views.py; member-blocks-fundraiser-creation was raising
  NameError (500 error) instead of returning 403; import added, control now works
- API6 — Business flow abuse: duplicate manual contributions logged as known gap;
  database-level constraint rejected (breaks legitimate repeat contributions);
  deferred to Phase 2
- API7 — SSRF: N/A currently; revisit during M-Pesa callback integration
- API8 — Misconfiguration: fixed — DEBUG was hardcoded True; changed to
  env.bool('DEBUG', default=False) so production defaults to safe state
- API9 — Inventory: clean; all routes versioned under /api/v1/, no shadow endpoints
- API10 — Unsafe API consumption: N/A currently; revisit during M-Pesa integration

**Tests — 15 → 20 (five new tests added)**

- test_fundraiser_injection_in_body_is_ignored — proves perform_create() hardening
- test_non_member_cannot_post_contribution — proves tenancy gate on POST
- test_non_member_cannot_list_contributions — proves tenancy gate on GET
- test_admin_can_create_fundraiser — proves admin role permitted to create
- test_member_cannot_create_fundraiser — this test found the PermissionDenied bug

**Commits this session**

- test: verify fundraiser injection hardening and non-member contribution access
- harden: make DEBUG env-controlled, default False
- fix: import PermissionDenied in fundraisers views — member role block was raising
  NameError; add role enforcement tests

**feature/week4-security-hardening merged to main**

---

## Completed — Week 4, Day 3

**Backend hardening — perform_create() fundraiser injection**

- fundraiser now read from URL kwargs in perform_create(), never from POST body
- fundraiser field moved to read_only_fields in ContributionSerializer
- validate_fundraiser() removed — protection now lives at the trust boundary
  (the view), not the serializer
- Verified via curl: POST without fundraiser in body returns correct fundraiser
  in response

**Frontend integration — complete**

- Fundraiser list page: /dashboard/organizations/[orgId]/fundraisers/
- Fetches published fundraisers for the org; each card links to contributions page
- Org picker navigation fixed: routes to /dashboard/organizations/[orgId]/fundraisers
- Contributions page: fundraiser removed from POST body (backend ignores it)
- Full flow verified manually: login → pick org → fundraiser list → contributions

**feature/contribution-ui merged to main**

---

## Known gaps — carried into Week 5

- [ ] contributor_name gap: no mechanism to record cash contributions from
      unregistered community members — core harambee use case, Phase 2 design needed
- [ ] Secure=True on refresh cookie: pending HTTPS setup; must be resolved before
      Phase 3 (payment integration)
- [ ] Duplicate manual contributions: no idempotency guard; time-window soft check
      in serializer is the planned approach; deferred to Phase 2
- [ ] Rate limiting on authenticated endpoints: low risk now; deferred to Phase 3
      when M-Pesa goes live and abuse becomes financially motivated
