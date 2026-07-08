**Last updated:** Week 3, Day 3 — Wednesday Integration day closed

---

## Completed — Week 3, Day 3

**Frontend — Axios interceptor and token refresh flow**

- Created `frontend/src/lib/axios.ts` — single configured Axios instance for the entire frontend; all components import this, never raw axios or fetch
- Request interceptor attaches Bearer token from `sessionStorage` automatically on every outgoing request — no component handles tokens manually
- Response interceptor catches `401` → silently calls `/api/v1/auth/token/refresh/` → retries original request with new access token → redirects to `/login` only if refresh itself fails
- `_retry` flag on original request prevents infinite loop if the refresh endpoint itself returns `401`
- Plain `axios.post()` used for the refresh call (not `apiClient`) — prevents the interceptor triggering itself recursively

**Token storage standardised**

- Login page was storing tokens in `localStorage` — moved to `sessionStorage` to match what the interceptor reads
- All three writes (`access_token`, `refresh_token`, `organizations`) now consistently use `sessionStorage` across all pages

**Dashboard cleaned up**

- Replaced raw `fetch()` and manually attached Bearer header with `apiClient.get()` — token handling fully delegated to interceptor
- No component in the app now touches tokens directly

**Dead code removed**

- Deleted `FundraiserList.tsx` — was hitting the deleted flat `/api/v1/fundraisers/` route, a multi-tenancy violation on a public page
- Removed import from landing page (`page.tsx`)

**Build fixed**

- Root cause: `NODE_ENV=development` set in shell environment triggered a confirmed Next.js bug — Pages Router runtime loaded during static 404 generation even in a pure App Router project
- Fix: hardcoded `NODE_ENV=production next build` in `package.json` build script so shell environment can never interfere
- Added `not-found.tsx` as explicit App Router 404 handler to prevent Next.js falling back to Pages Router default

**Integration test — verified live**

- Full flow tested manually in browser against live dev servers
- Login → org picker → dashboard loads fundraisers correctly end to end
- No console errors, no network failures

---

## Key principles reinforced today

- One place handles tokens — the interceptor. Components are consumers of data, not managers of auth state. Scattering token logic across components is how you get inconsistencies and security gaps.
- `_retry` flag is the guard against infinite refresh loops — without it, a failed refresh returns `401`, which triggers another refresh, indefinitely
- Dead routes are attack surface — deleting `FundraiserList` wasn't just cleanup, it removed a component pointing at a deliberately deleted endpoint
- Shell environment variables can silently break build tooling — always verify `NODE_ENV` before blaming your code
- A passing build is not the same as a working system — manual end-to-end verification is mandatory before closing a session

---

## Deferred

- Refresh token → `HttpOnly; Secure; SameSite=Strict` cookie (ADR-008) — requires Django to set `Set-Cookie` on login and read cookie on refresh; must land before Phase 3 (payment integration)
- CSRF middleware wiring for the HttpOnly cookie flow
- Detail endpoint `GET /api/v1/organizations/<org_id>/fundraisers/<id>/` — carries same IDOR risk as list endpoint; write the failing test first, then implement

---

## Completed this week (Week 3 summary so far)

| Day | Focus | Status |
|---|---|---|
| Monday | Backend — login response returns org list with roles | ✅ Done |
| Tuesday | Frontend — org picker flow (`/login`, `/pick-org`, `/dashboard/[orgId]`) | ✅ Done |
| Wednesday | Integration — Axios interceptor, token refresh, live flow verified | ✅ Done |

---

## Next up — Week 3, Day 4 (Thursday Security & Hardening)

- Review the Axios interceptor through an attacker-mindset lens — what could an attacker do against the current auth flow?
- Identify gaps remaining before Phase 3
- Security hardening pass on the full auth flow (login → token storage → refresh → dashboard)
- Write integration tests for token expiry and refresh scenarios
