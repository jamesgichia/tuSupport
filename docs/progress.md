**Last updated:** Week 3, Day 4 — Thursday Security & Hardening closed

---

## Completed — Week 3, Day 4

**ADR-008 implemented — Refresh token moved to HttpOnly cookie**

- `ThrottledTokenObtainPairView` updated — strips `refresh` from JSON response body and sets it as an `HttpOnly; SameSite=Strict` cookie scoped to `Path=/api/v1/auth/token/refresh/` only
- `CookieTokenRefreshView` added — reads refresh token from `request.COOKIES` instead of request body; frontend sends an empty POST, browser attaches the cookie automatically
- Token rotation (`ROTATE_REFRESH_TOKENS=True`) handled correctly — rotated refresh token updates the cookie on every successful refresh call; old token replaced, never left dangling
- `CORS_ALLOW_CREDENTIALS = True` added to `settings.py` — required for the browser to accept `Set-Cookie` headers on cross-origin requests (frontend port 3000 → backend port 8000)
- Login page (`/login/page.tsx`) — removed `sessionStorage.setItem("refresh_token", ...)` entirely; frontend never sees the refresh token again
- `credentials: "include"` added to the login `fetch()` call — tells the browser to accept and store the cookie Django sets in the login response
- `frontend/src/lib/axios.ts` updated — refresh call now sends empty POST body with `withCredentials: true`; browser handles the cookie transparently

**Tests**

- `test_login_sets_httponly_refresh_cookie` — verifies `refresh` absent from JSON, cookie present, `HttpOnly` flag set, `SameSite=Strict` set, `Path` scoped to refresh endpoint only
- `test_refresh_endpoint_reads_cookie_and_returns_new_access_token` — verifies full refresh flow: cookie planted on login, empty POST to refresh endpoint returns new access token, rotated cookie set, `refresh` absent from JSON
- Total passing tests: **6/6**

**Verified live**

- `curl` login confirmed: `Set-Cookie` header present, `refresh` absent from JSON body, `access` and `organizations` returned correctly
- `curl` refresh confirmed: new `access` token returned, new `refresh_token` cookie set (rotation working), `refresh` absent from JSON body

---

## Key principles reinforced today

- `HttpOnly` makes the refresh token invisible to JavaScript entirely — XSS cannot steal what JS cannot read
- `SameSite=Strict` closes the CSRF vector that HttpOnly cookies introduce — browser refuses to send the cookie on any cross-origin request
- Scoping the cookie to `Path=/api/v1/auth/token/refresh/` means the cookie is not sent on every API request — minimises exposure surface
- `secure=False` is deliberately set for dev only — this must flip to `True` before any production deployment (requires HTTPS)
- `CORS_ALLOW_CREDENTIALS=True` is a required pairing with `withCredentials: true` on the frontend — either side alone is not enough; both must be set

---

## Deferred

- `secure=True` on the refresh cookie — requires HTTPS; must be set before production deployment
- CSRF middleware wiring for any future state-mutating cookie-based flows
- Detail endpoint `GET /api/v1/organizations/<org_id>/fundraisers/<id>/` — carries same IDOR risk as list endpoint; write the failing test first, then implement

---

## Completed this week (Week 3 summary)

| Day | Focus | Status |
|---|---|---|
| Monday | Backend — login response returns org list with roles | ✅ Done |
| Tuesday | Frontend — org picker flow (`/login`, `/pick-org`, `/dashboard/[orgId]`) | ✅ Done |
| Wednesday | Integration — Axios interceptor, token refresh, live flow verified | ✅ Done |
| Thursday | Security — ADR-008 HttpOnly cookie, 2 new tests, 6/6 passing | ✅ Done |

---

## Next up — Week 3, Day 5 (Friday Review)

- Structured audit across all five layers: Database/Schema, Models/Multi-tenancy, API Views/Serializers, Auth/Authorization, Tests
- Confirm no remaining scope.md §10 violations before Week 4
- Identify anything that must land before Week 4 begins
