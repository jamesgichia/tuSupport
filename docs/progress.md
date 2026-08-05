# tuSupport — Progress Log

**Last updated:** Week 7, Day 3 — Integration

## Current state

36 tests passing. Branch: main. Contributions flow verified end-to-end.

---

## What was shipped today

- Contributor name field hidden from non-admin users in `contributions/page.tsx`
- Role `useEffect` added — reads `current_role` from sessionStorage on mount

---

## What was verified today

- `GET /api/v1/organizations/1/fundraisers/1/contributions/` — returns list correctly
- `POST /api/v1/organizations/1/fundraisers/1/contributions/` — 201, list refreshes
- `ValidationError` on unpublished fundraiser surfaces via `err.response?.data?.detail`
- Trust boundary confirmed: member `contributor_name` override ignored in `perform_create`
- Contributor name field hidden for members, visible for admins — verified in browser

---

## Decisions made

- Members can record their own contributions — form intentionally open to all; backend enforces trust boundaries, not the UI
- Contributor name field is admin-only concern — hiding it is a UX decision, not a security control; backend ignores it regardless

---

## Gotchas

- Role `useEffect` was correct but changes weren't saved — field appeared to not work; always save before debugging
- Full login flow must be completed before sessionStorage keys exist — `current_role` only written after org selection on pick-org page

---

## Known gaps — carried forward

- [ ] Admin-only permission on `FundraiserBeneficiaryListCreateView` POST — Thursday security day
- [ ] `current_amount` missing from `FundraiserReadSerializer` — progress bar shows 0%
- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs
- [ ] /api/v1/leads/ rate limit test: deferred
- [ ] status field on FundraiserBeneficiary: deferred to Phase 2
- [ ] allocation amounts on FundraiserBeneficiary: deferred to Phase 2

---

## Week 7 summary (in progress)

| Day | Concern     | Shipped                                                                             |
|-----|-------------|-------------------------------------------------------------------------------------|
| 1   | Backend     | FundraiserBeneficiary M2M; serializer; view; nested URL                            |
| 2   | Frontend    | public_description field; FundraiserReadSerializer; detail page; admin manage page |
| 3   | Integration | Contributions flow verified; contributor name field hidden from members             |
| 4   | Security    | —                                                                                   |
| 5   | Review      | —                                                                                   |

---

## Project structure

```
.
├── backend
│   ├── core
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── throttles.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── fundraisers
│   │   ├── migrations
│   │   │   ├── 0007_fundraiserbeneficiary.py
│   │   │   └── 0008_beneficiary_public_description.py
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── test_contributions.py
│   │   │   └── test_fundraiser_state_machine.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── leads
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── tusupport
│   │   ├── asgi.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── requirements.txt
├── docs
│   ├── architecture.md
│   ├── decisions.md
│   ├── progress.md
│   ├── roadmap.md
│   └── scope.md
├── frontend
│   ├── src
│   │   ├── app
│   │   │   ├── dashboard
│   │   │   │   └── organizations
│   │   │   │       └── [orgId]
│   │   │   │           ├── beneficiaries
│   │   │   │           │   └── page.tsx
│   │   │   │           └── fundraisers
│   │   │   │               ├── [fundraiserId]
│   │   │   │               │   ├── contributions
│   │   │   │               │   │   └── page.tsx
│   │   │   │               │   ├── manage
│   │   │   │               │   │   └── page.tsx
│   │   │   │               │   └── page.tsx
│   │   │   │               └── page.tsx
│   │   │   ├── login
│   │   │   │   └── page.tsx
│   │   │   ├── pick-org
│   │   │   │   └── page.tsx
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   ├── not-found.tsx
│   │   │   └── page.tsx
│   │   ├── components
│   │   │   ├── EmailSignup.tsx
│   │   │   └── LandingHero.tsx
│   │   └── lib
│   │       └── axios.ts
│   ├── next.config.ts
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```
