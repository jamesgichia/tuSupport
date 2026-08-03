**Last updated:** Week 6, Day 5 — Friday Review & Stabilization

## Current state

36 tests passing. Branch feature/beneficiary-integration merged to main.

## What was shipped today

- `LoginThrottleTest` — confirms `429` after 3 consecutive login attempts
- `TokenRefreshThrottleTest` — confirms `429` after 3 consecutive refresh attempts
- `throttle_classes = [LoginRateThrottle]` added to `CookieTokenRefreshView`
  — this view was previously completely unthrottled, a silent security gap
- `LoginRateThrottle` import added to `core/tests.py`
- `core/tests.py` consolidated — removed stacked duplicate `@override_settings`
  decorators on `LoginResponseTest`; extracted shared `THROTTLE_DISABLED` constant
  to eliminate repeated throttle bypass dicts across test classes

## What was verified today

- `test_login_throttle_returns_429_after_limit` — `429` fires on 4th attempt
- `test_refresh_throttle_returns_429_after_limit` — `429` fires on 4th attempt
  after a real login session (valid cookie required — fake cookie dies at 401
  before throttle is evaluated)
- Full suite: 36/36 passing across all apps

## Decisions made

- `patch.object(LoginRateThrottle, 'THROTTLE_RATES', {'login': '3/minute'})`
  is the correct pattern for throttle rate tests — `override_settings` on
  `REST_FRAMEWORK` fails because DRF evaluates `throttle_classes` at class
  definition time, not at request time; the class attribute wins regardless
  of what `override_settings` does to the settings dict
- `cache.clear()` in both `setUp` and `tearDown` — mandatory for throttle tests;
  dirty cache causes counters to start mid-count from previous runs
- `/api/v1/leads/` rate limit test deferred — endpoint confirmed as pure DB write
  with no external side effects (no email, no SMS, no webhooks); deferral is
  justified; revisit if leads endpoint gains external integrations

## Security finding closed this session

`CookieTokenRefreshView` had no `throttle_classes` defined. An attacker with
a stolen refresh token could hammer `/api/v1/auth/token/refresh/` indefinitely
to rotate tokens and maintain persistent access. Now closed — throttle fires
at 3 attempts/minute.

## Known gaps — carried to Week 7

- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] public_description on Beneficiary: Week 7
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Fundraiser <-> Beneficiary M2M: Week 7
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs;
      no central auth state — flagged, not blocking
- [ ] /api/v1/leads/ rate limit test: deferred — pure DB write, no external
      side effects; revisit if endpoint gains integrations

## Week 6 summary

| Day | Concern    | Shipped                                              |
|-----|------------|------------------------------------------------------|
| 1   | Backend    | Beneficiary module; dual serializer; NULL constraint |
| 2   | Frontend   | Beneficiary admin page; UniqueConstraint fix         |
| 3   | Integration| Beneficiary list/detail/create endpoints wired       |
| 4   | Security   | Token blacklisting; LogoutView; cookie path fix      |
| 5   | Review     | Throttle tests; CookieTokenRefreshView gap closed    |


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
23 directories, 71 files
