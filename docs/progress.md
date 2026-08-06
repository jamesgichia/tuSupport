# tuSupport — Progress Log

**Last updated:** Week 7, Day 4 — Security

## Current state

43 tests passing. Branch: main. Admin-only gate on FundraiserBeneficiary POST enforced and proven. current_amount live on fundraiser detail page.

---

## What was shipped today

- `IsOrgAdmin` permission class — gates unsafe methods on `FundraiserBeneficiaryListCreateView` to admin role only
- `FundraiserBeneficiaryListCreateView` updated — `IsOrgAdmin` added to `permission_classes`; inline membership lookups replaced with `get_membership_or_404()` pattern
- 7 new permission tests — covers unauthenticated, foreign user (cross-tenant), member, and admin actors across GET and POST
- `current_amount` added to `FundraiserReadSerializer` via `SerializerMethodField` — calculates live sum from contributions table; verified in browser (KES 18,100 / 100% funded)

---

## What was verified today

- Unauthenticated GET/POST → 401
- Foreign user (Org B member) GET/POST to Org A → 404 (tenant isolation holds)
- Regular member POST → 403
- Regular member GET → 200
- Admin POST → 201
- Progress bar on fundraiser detail page shows correct funded amount

---

## Decisions made

- `IsOrgAdmin` raises `Http404` for non-members (cross-tenant probe prevention) and returns `False` for authenticated members without admin role (yields `403`)
- `current_amount` derived on demand — never stored; no `status` filter since manual contributions have no payment status field (M-Pesa status tracking deferred to Phase 3)
- `get_membership_or_404()` remains an instance method per view class — refactor to shared module-level function flagged as tech debt, deferred to Week 8 hardening

---

## Gotchas

- `IsOrgAdmin` sketch in session used `fundraiser_pk` kwarg — actual URL uses `org_id`; always read the URL config before writing permission logic
- `Contribution` model has no `status` field — filtering by `status='completed'` crashed at runtime; removed filter, all recorded contributions count
- `Beneficiary` model uses `display_name` + `full_name`, not `name` — test fixtures must match actual model fields

---

## Known gaps — carried forward

- [ ] `get_membership_or_404()` duplicated across view classes — extract to module-level helper (Week 8)
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

| Day | Concern     | Shipped                                                                                      |
|-----|-------------|----------------------------------------------------------------------------------------------|
| 1   | Backend     | FundraiserBeneficiary M2M; serializer; view; nested URL                                     |
| 2   | Frontend    | public_description field; FundraiserReadSerializer; detail page; admin manage page          |
| 3   | Integration | Contributions flow verified; contributor name field hidden from members                      |
| 4   | Security    | IsOrgAdmin permission class; 7 new tests; current_amount on FundraiserReadSerializer        |
| 5   | Review      | —                                                                                            |

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
