**Last updated:** Week 5, Day 1 — Fundraiser state machine

---

## Current state — end of Week 5, Day 1

All Week 4 work remains stable on main.
Backend: 30/30 tests passing.
Fundraiser state machine implemented and tested.

---

## Completed — Week 5, Day 1

**Fundraiser state machine — draft → published → closed**

- Added PublishFundraiserView and CloseFundraiserView (admin-only)
- Transition validation: illegal moves return 400 (e.g. publish a closed
  fundraiser, close a draft)
- Contribution guard added to perform_create() — rejects contributions
  against non-published fundraisers with 400
- FundraiserListCreateView queryset fixed: admins see all statuses,
  members see published only
- tests.py converted to tests/ package (test_contributions.py,
  test_fundraiser_state_machine.py)
- Two existing contribution tests updated: setUp fundraisers moved from
  draft → published to reflect real pre-conditions
- Branch: feature/fundraiser-state-machine (not yet merged)

---

## Known gaps — carried forward

- [ ] contributor_name gap: no mechanism to record cash contributions from
      unregistered community members — still unaddressed
- [ ] Secure=True on refresh cookie: pending HTTPS; must resolve before Phase 3
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Rate limiting on authenticated endpoints: must resolve before M-Pesa
      goes live (Phase 3)

---

## Up next — Week 5, Day 2

- Fundraiser management UI (Next.js)
- Admin controls: publish and close buttons wired to the new endpoints
- Member view: only published fundraisers visible in the list
