**Last updated:** Week 7, Day 1 — Backend

## Current state

36 tests passing. Branch feature/fundraiser-beneficiary-m2m in progress.

---

## What was shipped today

- `FundraiserBeneficiary` explicit junction model added to `fundraisers/models.py`
  - `fundraiser` FK — `on_delete=PROTECT` (audit-grade; blocks fundraiser deletion while links exist)
  - `beneficiary` FK — `on_delete=PROTECT` (blocks beneficiary deletion while linked to any campaign)
  - `created_by` FK — `on_delete=PROTECT`, `null=True` (system actions may have no user)
  - `organization` — denormalized intentionally; avoids JOIN in tenant-scoped queries (see ADR-010)
  - `notes` — optional text; captures committee context for why beneficiary was attached
  - `created_at` — auto-stamped audit trail
  - `UniqueConstraint` on `(fundraiser, beneficiary)` — prevents duplicate links
- Migration `0007_fundraiserbeneficiary` applied cleanly
- `FundraiserBeneficiarySerializer` added to `fundraisers/serializers.py`
  - `beneficiary` — write field (accepts ID on POST)
  - `beneficiary_name` — read-only nested field (returns human-readable name via `source`)
  - `created_by`, `created_at` — read-only audit fields; never client-writable
- `FundraiserBeneficiaryListCreateView` added to `fundraisers/views.py`
  - Membership-based tenant isolation — consistent with all existing views
  - Dual IDOR check: fundraiser AND beneficiary both verified against same tenant before write
  - `fundraiser` injected from URL kwargs in `perform_create()` — client cannot override
- Nested URL registered: `organizations/<org_id>/fundraisers/<fundraiser_pk>/beneficiaries/`
- `get_object_or_404` import added to `fundraisers/views.py` (was missing — caused 500)

## What was verified today

- `GET /api/v1/organizations/1/fundraisers/1/beneficiaries/` — returns `[]` on empty, 200 OK
- `POST /api/v1/organizations/1/fundraisers/1/beneficiaries/` — creates junction record,
  returns `id`, `beneficiary`, `beneficiary_name`, `notes`, `created_at`, `created_by`
- `GET` after POST — returns the created record correctly
- Full suite: 36/36 passing

## Decisions made

- Explicit `through` model chosen over Django's implicit `ManyToManyField` — implicit M2M
  gives the relationship but discards audit context (who linked it, when, why)
- `organization` denormalized onto junction table — intentional, not a normalization error;
  avoids JOIN overhead in tenant-scoped `get_queryset()` calls (logged in ADR-010)
- `status` field (ACTIVE/REMOVED) deferred to Phase 2 — soft-disassociation implies a
  workflow (who can remove, what happens to past contributions) that doesn't exist yet;
  an unenforced field implies a guarantee the system doesn't give
- Allocation amounts deferred to Phase 2 — harambee pot is collected first, distributed
  by committee later; enforcing per-beneficiary allocation requires disbursement logic
  that doesn't exist yet
- URL pattern: nested under fundraiser (`organizations/<org_id>/fundraisers/<pk>/beneficiaries/`)
  not flat (`/fundraiser-beneficiaries/`) — frontend always has fundraiser context when
  managing beneficiaries; nested URL makes `fundraiser_id` implicit in path, not payload

## Security notes

- Dual IDOR protection confirmed: both `fundraiser` and `beneficiary` resolved against
  `membership.organization` before any write — attacker from Org B cannot slip in a
  Org B beneficiary ID into Org A's fundraiser
- **Known gap:** POST is currently open to any authenticated member — attaching a
  beneficiary to a campaign is a committee/admin decision; permission check needed.
  Flagged for Thursday security day.

## Known gaps — carried forward

- [ ] Admin-only permission on `FundraiserBeneficiaryListCreateView` POST —
      any member can currently attach beneficiaries; Thursday security day
- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] public_description on Beneficiary: Week 7
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs;
      no central auth state — flagged, not blocking
- [ ] /api/v1/leads/ rate limit test: deferred — pure DB write, no external
      side effects; revisit if endpoint gains integrations
- [ ] status field on FundraiserBeneficiary: deferred to Phase 2
- [ ] allocation amounts on FundraiserBeneficiary: deferred to Phase 2

## Week 7 summary (in progress)

| Day | Concern     | Shipped                                                        |
|-----|-------------|----------------------------------------------------------------|
| 1   | Backend     | FundraiserBeneficiary M2M; serializer; view; nested URL       |
| 2   | Frontend    | —                                                              |
| 3   | Integration | —                                                              |
| 4   | Security    | —                                                              |
| 5   | Review      | —                                                              |

---

## Project structure

.
├── backend
│   ├── core
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── **init**.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── throttles.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── fundraisers
│   │   ├── migrations
│   │   │   └── 0007_fundraiserbeneficiary.py
│   │   ├── tests
│   │   │   ├── **init**.py
│   │   │   ├── test_contributions.py
│   │   │   └── test_fundraiser_state_machine.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── **init**.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── leads
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── **init**.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── tusupport
│   │   ├── asgi.py
│   │   ├── **init**.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── cookies.txt
│   ├── manage.py
│   └── requirements.txt
├── docs
│   ├── architecture.md
│   ├── decisions.md
│   ├── progress.md
│   ├── roadmap.md
│   └── scope.md
├── frontend
│   ├── public
│   │   ├── file.svg
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── src
│   │   ├── app
│   │   │   ├── dashboard
│   │   │   │   └── organizations
│   │   │   │       └── [orgId]
│   │   │   │           ├── beneficiaries
│   │   │   │           │   └── page.tsx
│   │   │   │           └── fundraisers
│   │   │   │               ├── [fundraiserId]
│   │   │   │               │   └── contributions
│   │   │   │               │       └── page.tsx
│   │   │   │               └── page.tsx
│   │   │   ├── login
│   │   │   │   └── page.tsx
│   │   │   ├── pick-org
│   │   │   │   └── page.tsx
│   │   │   ├── favicon.ico
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   ├── not-found.tsx
│   │   │   └── page.tsx
│   │   ├── components
│   │   │   ├── EmailSignup.tsx
│   │   │   └── LandingHero.tsx
│   │   └── lib
│   │       └── axios.ts
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── next-env.d.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.mjs
│   ├── README.md
│   └── tsconfig.json
├── docker-compose.yml
├── LICENSE
└── README.md
