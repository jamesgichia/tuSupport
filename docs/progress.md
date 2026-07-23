**Last updated:** Week 5, Day 3 — Integration & colour token system

---

## Current state — end of Week 5, Day 3

All Week 5 Day 3 work merged to main.
Backend: 30/30 tests passing.
Colour token system fully wired and dark mode verified.

---

## Completed — Week 5, Day 3

**Colour token system**

- globals.css rebuilt with brand tokens (unchanged across modes) and
  semantic surface/text tokens (flip per mode)
- Dark mode wired via both prefers-color-scheme media query and
  [data-theme="dark"] attribute — ready for manual toggle
- All components migrated off raw Tailwind colour classes
- Token bridge via @theme inline — Tailwind utility classes now
  reference CSS variables

**Create fundraiser form**

- Admin-only collapsible form on fundraisers page
- POST to /api/v1/organizations/<orgId>/fundraisers/
- List auto-refreshes on success
- Backend permission class enforces admin-only independently of UI

---

## Known gaps — carried forward

- [ ] contributor_name gap: unregistered cash contributors unaddressed
- [ ] Secure=True on refresh cookie: pending HTTPS
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Rate limiting on authenticated endpoints: must resolve before Phase 3
- [ ] Dark mode manual toggle: [data-theme="dark"] wired in CSS,
      no UI toggle yet

---

## Up next — Week 5, Day 4 (Security & Hardening)

- Input validation audit on contribution and fundraiser endpoints
- Rate limiting assessment
- Review contributor_name gap — decide defer or fix
