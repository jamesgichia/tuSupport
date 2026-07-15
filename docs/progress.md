**Last updated:** Week 4, Day 2 — Frontend Day closed

---

## Completed — Week 4, Day 2

**Contribution UI — complete**

- Route: /dashboard/organizations/[orgId]/fundraisers/[fundraiserId]/contributions
- Both IDs explicit in URL — org context not reliant on session state (IDOR protection)
- Next.js 15 params unwrapped via React use() — params is now a Promise in Next.js 15
- Contribution form: amount, payment method, transaction ID
- contributor_name field removed — backend links contributor to authenticated user ID
- fundraiser injected into POST body from URL param (frontend workaround — see hardening item)
- Contribution list renders in reverse chronological order
- Axios interceptor handles auth transparently — unauthenticated users redirected to login

**Known gaps logged:**

- Backend perform_create() should inject fundraiser from URL rather than requiring it
  in POST body — currently a frontend workaround, creates minor inconsistency risk
- contributor_name gap: no mechanism to record cash contributions from unregistered
  community members — core harambee use case, needs Phase 2 solution
- secure=True on refresh cookie still pending HTTPS setup

---

## Open items carried into Week 4, Day 3 (Integration Day)

- [ ] Wire org picker to pass orgId into dashboard navigation
- [ ] Backend hardening: perform_create() injecting fundraiser from URL
- [ ] Fundraiser list page so users can navigate to contributions naturally
