**Last updated:** Week 5, Day 4 — Security & Hardening

---

## Current state — end of Week 5, Day 4

All Week 5 Day 4 work committed to main.
Backend: 30/30 tests passing.
Frontend: contributions form updated.

---

## Completed — Week 5, Day 4

**Input validation hardening**

- FundraiserSerializer: explicit field declarations for title
  (min_length=5, trim_whitespace=True), description (max_length=5000),
  goal_amount (min=1.00, max=10,000,000.00)
- ContributionSerializer: ChoiceField on payment_method closes
  arbitrary string injection; amount bounded (min=0.01,
  max=999,999.99); notes capped at 2000 chars
- Cross-field validation: mpesa payment_method requires phone_number
  via object-level validate() method
- Key lesson: model choices constraints do not enforce at the API
  layer — DRF skips model.full_clean() by default; explicit
  ChoiceField required on the serializer

**Rate limiting**

- DEFAULT_THROTTLE_CLASSES added to REST_FRAMEWORK settings
- Anon: 20/hour, User: 200/hour
- Clears the authenticated endpoint rate limiting gap carried
  forward from Week 4

**contributor_name gap closed**

- Nullable CharField(max_length=100) added to Contribution model
- Migration applied cleanly
- ContributionSerializer updated to accept and return the field
- Contributions frontend form: contributor_name input added
- Contributions frontend form: phone_number field added,
  conditionally shown for mpesa only
- Contributions frontend form: bank transfer option removed —
  was never a valid backend choice
- Contribution list display: shows contributor_name when present,
  falls back to Contributor #ID

---

## Known gaps — carried forward

- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet

---

## Up next — Week 5, Day 5 (Review & Stabilization)

- Full Friday audit across all 5 layers
- Week 6 planning
- progress.md update before session close
