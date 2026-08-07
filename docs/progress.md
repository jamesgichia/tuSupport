# tuSupport — Progress Log

**Last updated:** Week 7, Day 5 — Review & Freeze

## Current state

43 tests passing. Branch: main. Week 7 complete and frozen.

---

## What was shipped today

- Week 7 review: security posture audit, known gaps stress-tested
- `cookies.txt` credential incident resolved — removed from tracking, `backend/.gitignore` created
- Progress log updated, Week 7 closed

---

## Decisions made

- `get_membership_or_404()` duplication is a **structural security risk**, not just cleanliness — root cause is absence of a single enforcement point; extraction to shared module is Week 8 priority, not optional cleanup
- Accidental credential commits: dev tokens → note and move on; production credentials → rotate first, rewrite history second

---

## Gotchas

- `cookies.txt` was committed in the ADR-008 commit (July 10) — curl cookie jars must be in `.gitignore` before first test session, not after
- `git add <deleted-file>` fails if `git rm --cached` already staged the deletion — this is expected, not an error

---

## Known gaps — carried forward to Week 8

- [ ] `get_membership_or_404()` duplicated across view classes — extract to module-level helper (Week 8 priority #1)
- [ ] `Secure=True` on refresh cookie: pending HTTPS setup
- [ ] `contributor` FK nullable: blocks anonymous cash contributions at model level
- [ ] `submitted_by` audit principal field: no record of who entered a manual contribution
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs
- [ ] `/api/v1/leads/` rate limit test: deferred
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] `status` field on FundraiserBeneficiary: deferred to Phase 2
- [ ] Allocation amounts on FundraiserBeneficiary: deferred to Phase 2

---

## Week 7 summary

| Day | Concern     | Shipped                                                                                 |
|-----|-------------|-----------------------------------------------------------------------------------------|
| 1   | Backend     | FundraiserBeneficiary M2M; serializer; view; nested URL                                |
| 2   | Frontend    | public_description field; FundraiserReadSerializer; detail page; admin manage page     |
| 3   | Integration | Contributions flow verified; contributor name field hidden from members                 |
| 4   | Security    | IsOrgAdmin permission class; 7 new tests; current_amount on FundraiserReadSerializer   |
| 5   | Review      | Security audit; credential incident resolved; Week 7 frozen                            |

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
24 directories, 72 files
```
