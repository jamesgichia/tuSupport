**Last updated:** Week 4, Day 3 — Integration Day closed

---

## Completed — Week 4, Day 3

**Backend hardening — perform_create() fundraiser injection**

- fundraiser now read from URL kwargs in perform_create(), never from POST body
- fundraiser field moved to read_only_fields in ContributionSerializer
- validate_fundraiser() removed — protection now lives at the trust boundary (the view), not the serializer
- Verified via curl: POST without fundraiser in body returns correct fundraiser in response

**Frontend integration — complete**

- Fundraiser list page created: /dashboard/organizations/[orgId]/fundraisers/
- Fetches published fundraisers for the org, each card links to contributions page
- Org picker navigation fixed: now routes to /dashboard/organizations/[orgId]/fundraisers
- Contributions page: removed fundraiser from POST body (backend no longer accepts it)
- Full flow verified manually: login → pick org → fundraiser list → contributions

**feature/contribution-ui merged to main**

---

## Open items carried into Week 4, Day 4 (Security & Hardening Day)

- [ ] contributor_name gap: no mechanism to record cash contributions from
      unregistered community members — core harambee use case, needs Phase 2 solution
- [ ] secure=True on refresh cookie still pending HTTPS setup
- [ ] Write tests covering the fundraiser injection hardening
- [ ] Review full OWASP checklist against current API surface
