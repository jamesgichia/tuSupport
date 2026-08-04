# tuSupport — Progress Log

**Last updated:** Week 7, Day 2 — Frontend

## Current state

36 tests passing. Branch: main. Fundraiser detail and admin manage pages shipped and verified end-to-end.

---

## What was shipped today

### Backend additions

- `public_description` field added to `Beneficiary` model — `TextField`, `blank=True`, `default=''`; closes Week 7 gap from Day 1 log
- Migration `0008_beneficiary_public_description` applied cleanly
- `public_description` added to `BeneficiaryPublicSerializer.Meta.fields`
- `FundraiserReadSerializer` added to `fundraisers/serializers.py`
  - `beneficiaries` via `SerializerMethodField` — traverses `FundraiserBeneficiary` junction, returns `BeneficiaryPublicSerializer` representation per linked beneficiary
  - `select_related('beneficiary')` on junction queryset — prevents N+1 database queries
- `FundraiserDetailView` swapped from `FundraiserSerializer` to `FundraiserReadSerializer`

### Frontend additions

- `dashboard/organizations/[orgId]/fundraisers/[fundraiserId]/page.tsx` — member-facing fundraiser detail page
  - Single payload fetch; beneficiaries inline, no secondary request
  - Progress bar, beneficiary cards (`display_name`, `category`, `public_description`, `verification_status`)
  - Graceful fallback for missing `current_amount` (`?? '0'`) — progress bar shows 0% honestly
  - Contribute button routes to contributions sub-page
- `dashboard/organizations/[orgId]/fundraisers/[fundraiserId]/manage/page.tsx` — admin-only beneficiary management page
  - Role gate reads `current_role` from sessionStorage (set by pick-org page); non-admins silently redirected to member detail page — UX gate only, backend enforces on POST
  - `Promise.all` parallel fetch — linked beneficiaries and org beneficiary pool load simultaneously
  - Dropdown filtered to unlinked beneficiaries only — already-linked IDs excluded client-side
  - Attach flow with optional committee notes; POST 201 confirmed
  - `fetchData` re-fires after successful POST — both lists refresh, attached beneficiary disappears from dropdown immediately
  - Back navigation to member detail page

---

## What was verified today

- `GET /api/v1/organizations/1/fundraisers/1/` — returns `beneficiaries` array inline, correct fields
- Member page renders beneficiary cards from nested payload
- `GET /api/v1/organizations/1/fundraisers/1/beneficiaries/` — returns linked beneficiaries correctly
- `GET /api/v1/organizations/1/beneficiaries/` — returns org pool for dropdown
- `POST /api/v1/organizations/1/fundraisers/1/beneficiaries/` — 201, list refreshes, linked count incremented correctly (1 → 2 → 3 verified)
- Full suite: 36/36 passing

---

## Decisions made

- Separate `/manage/` page over extending member page — different data contracts; admin logic stays out of public JS bundle; different role mental model (what donors see vs. committee workspace)
- `SerializerMethodField` over direct nested serializer — M2M goes through junction table; method field traverses it cleanly without exposing junction metadata to public response
- Read/write serializer split introduced — `FundraiserReadSerializer` for GET detail; `FundraiserSerializer` retained for POST/create; prevents `beneficiaries` field appearing on write requests

---

## Gotchas

- Role gate initially used `sessionStorage.getItem('role')` — key does not exist; correct key is `current_role`, written only after org selection on pick-org page; silent redirect fired until full login flow was completed in browser
- Frontend API calls missing `/api/v1/` prefix on new pages — `baseURL` in `axios.ts` is bare host (`http://localhost:8000`); all pages prefix `/api/v1/` manually in each call; new pages must follow same pattern

---

## Known gaps — carried forward

- [ ] Admin-only permission on `FundraiserBeneficiaryListCreateView` POST — any authenticated member can currently attach beneficiaries; Thursday security day
- [ ] `current_amount` missing from `FundraiserReadSerializer` — progress bar shows 0%; needs contribution aggregation logic
- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs; no central auth state — flagged, not blocking
- [ ] /api/v1/leads/ rate limit test: deferred — pure DB write, no external side effects; revisit if endpoint gains integrations
- [ ] status field on FundraiserBeneficiary: deferred to Phase 2
- [ ] allocation amounts on FundraiserBeneficiary: deferred to Phase 2

---

## Week 7 summary (in progress)

| Day | Concern     | Shipped                                                                             |
|-----|-------------|-------------------------------------------------------------------------------------|
| 1   | Backend     | FundraiserBeneficiary M2M; serializer; view; nested URL                            |
| 2   | Frontend    | public_description field; FundraiserReadSerializer; detail page; admin manage page |
| 3   | Integration | —                                                                                   |
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
