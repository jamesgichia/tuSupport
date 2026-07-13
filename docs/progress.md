**Last updated:** Week 4, Day 1 — Backend Day closed

---

## Completed — Week 4, Day 1

**All Week 3 open gaps closed before new feature work began**

**Privilege Escalation (OWASP API6) — CLOSED**

- core/serializers.py created with MembershipSerializer
- validate_role() blocks non-admin role writes at serializer level
- Protection travels with the serializer, not tied to any single view
- MembershipUpdateView (PATCH only) added to core/views.py
- core/urls.py created and registered in tusupport/urls.py
- 2 tests: member escalation blocked, admin promotion confirmed

**Fundraiser Detail Endpoint — IDOR CLOSED**

- FundraiserDetailView added to fundraisers/views.py
- Two-step tenant check: membership verified first, fundraiser scoped to org
- 404 on all failure paths — never 403
- Tests written before implementation

**Contribution Management — backend complete**

- Contribution model extends TenantScopedModel — isolation inherited automatically
- on_delete=PROTECT on both FKs — financial records cannot be silently deleted
- transaction_id unique=True — idempotency protection against duplicate M-Pesa callbacks
- ContributionSerializer: validates amount > 0, fundraiser belongs to same org
- ContributionListCreateView: members see own contributions, admins see all
- URL: /api/v1/organizations/<org_id>/fundraisers/<fundraiser_id>/contributions/
- 5 contribution tests covering create, validation, scoped listing, auth

**Test suite: 15/15 passing**

---

## Open items carried into Week 4, Day 2 (Frontend)

- [ ] Contribution UI — form to record a contribution
- [ ] Contribution list view per fundraiser
- [ ] secure=True on refresh cookie before any production deployment

---
