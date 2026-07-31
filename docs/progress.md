**Last updated:** Week 6, Day 4 — Security Day

## Current state

34 tests passing. On branch feature/beneficiary-integration.

## What was shipped today

- Token blacklisting enabled via `rest_framework_simplejwt.token_blacklist`
- `ROTATE_REFRESH_TOKENS=True` + `BLACKLIST_AFTER_ROTATION=True` configured
- `LogoutView` built in `core/views.py` — reads refresh token from HttpOnly
  cookie, blacklists it, clears cookie from browser
- Cookie path updated from `/api/v1/auth/token/refresh/` to `/api/v1/auth/`
  to cover logout endpoint
- `auth/logout/` registered in `core/urls.py`
- 4 logout tests added to `core/tests.py`
- Throttle interference fixed in `IDORFundraiserTest` and `LogoutTest`
  using `unittest.mock.patch` on `allow_request`

## What was verified today

- Blacklist tables created and migrated cleanly
- `test_logout_blacklists_refresh_token` — token is dead after logout;
  refresh attempt returns 401
- `test_logout_clears_cookie` — browser cookie wiped on logout response
- `test_logout_requires_authentication` — unauthenticated logout returns 401
- `test_logout_without_cookie_returns_400` — graceful handling when cookie absent
- Cookie path change verified against existing `test_login_sets_httponly_refresh_cookie`

## Decisions made

- `patch('core.throttles.LoginRateThrottle.allow_request')` adopted as
  standard pattern for bypassing throttle in non-throttle tests — surgical,
  doesn't touch settings, consistent with existing `RolePermissionTest`
- Cookie path broadened from `/api/v1/auth/token/refresh/` to `/api/v1/auth/`
  — covers both refresh and logout endpoints under one auth namespace

## Known gaps — carried forward

- [ ] Secure=True on refresh cookie: pending HTTPS setup
- [ ] public_description on Beneficiary: Week 7
- [ ] Duplicate manual contributions: deferred to Phase 2
- [ ] Dark mode manual toggle: CSS wired, no UI toggle yet
- [ ] Per-IP rate limiting: deferred to Week 8
- [ ] Rate limit test coverage: login throttle tested; leads + token refresh
      endpoints need coverage — carry to Friday Review
- [ ] contributor FK nullable: deferred (anonymous cash contributions)
- [ ] submitted_by audit principal: deferred to Week 8
- [ ] Fundraiser <-> Beneficiary M2M: Week 7
- [ ] Auth context refactor: sessionStorage pattern is brittle across tabs;
      no central auth state — flagged, not blocking

## Friday carry-forward question

Which unauthenticated endpoints need rate limit tests and why?
Candidates: `/api/v1/leads/`, `/api/v1/auth/token/`, `/api/v1/auth/token/refresh/`
Reason through: is each currently throttled, what's the attack if not,
does it need a test?

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
