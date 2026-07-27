**Last updated:** Week 6, Day 1 — Backend Day

## Current state

32 tests passing (30 existing + 2 new migrations verified clean).
Three Monday deliverables complete and committed to main.

## What shipped today

- contributor_name spoofing closed: perform_create() now derives name
  server-side; admins may supply third-party names, members cannot
- NULL/NULL CHECK constraint added to Contribution model — audit-grade
  identity requirement enforced at DB level
- Beneficiary module: model (org-scoped, UniqueConstraint on national_id
  per org), dual serializers (public/admin), admin-gated list+create view

## Architecture decisions made

- contributor_name derivation lives in perform_create() not validate() —
  data derivation is a view concern, validation is a serializer concern
- Beneficiary scoped to Organization not Fundraiser — supports
  longitudinal tracking across multiple campaigns
- Fundraiser <-> Beneficiary M2M link deferred to Week 7

## Gaps logged today

- contributor FK on Contribution has no null=True — anonymous cash
  contributions currently impossible at model level; deferred
- submitted_by audit principal on contributions — deferred to Week 8
  hardening

## Known gaps — carried forward

- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] Rate limit test coverage: Week 6 Thursday
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Fundraiser <-> Beneficiary M2M: Week 7
