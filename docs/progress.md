**Last updated:** Week 2, Day 3 — closed
**Active branch:** `feature/fundraiser-model` (not yet merged to main)

## Completed — Week 2, Day 3

- `djangorestframework-simplejwt` installed, added to `requirements.txt`
- `DEFAULT_AUTHENTICATION_CLASSES` set to `JWTAuthentication` in DRF settings
- Token lifetimes configured in `SIMPLE_JWT`:
  - Access token: 15 minutes
  - Refresh token: 7 days
  - `ROTATE_REFRESH_TOKENS = True` — each refresh retires the old token, issues a new pair
- `POST /api/v1/auth/token/` — login endpoint, issues access + refresh token pair
- `POST /api/v1/auth/token/refresh/` — refresh endpoint, rotates token pair
- `LoginRateThrottle` built in `core/throttles.py` — scope: `login`, limit: 5/minute
- `ThrottledTokenObtainPairView` in `core/views.py` wraps simplejwt's default
  login view with the login throttle
- URLs wired in `tusupport/urls.py` for both auth endpoints

## Verified at HTTP layer

- Wrong password → `401 No active account found`
- No token on protected endpoint → `401 Authentication credentials were not provided`
- Valid token + org membership → `201 Created` (fundraiser created successfully)
- Brute force test (7 rapid attempts) → `401` × 5, then `429 Too Many Requests`
- Refresh endpoint → returns new `access` + new `refresh` token (rotation confirmed)
- Seeded `Membership` for user `james` via Django shell to unblock POST testing

## Security reasoning established this session

- JWT payload is base64-readable by anyone — not encrypted, only signed
- Signature is HMAC-SHA256 keyed on Django's `SECRET_KEY` — payload
  tampering invalidates the signature; forgery is impossible without the key
- `SECRET_KEY` is the cryptographic root of the entire auth system — leaking
  it means every token ever issued is forgeable
- Refresh token is the higher-value attack target: stolen refresh token =
  ability to mint new access tokens for up to 7 days
- `localStorage` is wrong for refresh tokens — readable by any JavaScript,
  including XSS payloads
- Correct storage model (to implement when frontend auth is wired):
  - Access token → JavaScript memory only (lost on page refresh, by design)
  - Refresh token → `HttpOnly` cookie (browser enforces: no JS can read it)
- `HttpOnly` cookies introduce CSRF risk — mitigated by CSRF tokens
  (deferred to frontend auth wiring session)
- `ROTATE_REFRESH_TOKENS = True` acts as a trip-wire: a stolen refresh token
  used by an attacker invalidates the legitimate user's copy on next refresh

## Open items carried forward

- **IDOR cross-org test — merge blocker.** Must be written and passing
  before `feature/fundraiser-model` merges to main. This is Day 4's
  primary deliverable.
- Frontend auth flow not yet wired (access token in memory + refresh token
  in HttpOnly cookie) — deferred to frontend integration session
- `TenantManager` real filtering logic + middleware (ADR-004) — still
  bypassed via `_base_manager` (GET) and direct `.save()` (POST)
- No user registration endpoint — new users must be seeded manually
  via Django shell
- Celery org-context gap — Phase 3, unchanged
- Per-process rate-limit counter (Redis needed for production) — unchanged

## Next up — Week 2, Day 4 (Security & Hardening)

- Write and run the IDOR cross-org test:
  - Create two organizations, two users, two fundraisers
  - Confirm user A cannot read or write user B's fundraisers
  - This test must pass before any merge to main
- IDOR test passing = `feature/fundraiser-model` is merge-ready
