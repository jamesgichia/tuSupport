**Last updated:** Week 3, Day 2 — Tuesday Frontend day closed

## Completed today

**Backend — login response extended**

- `ThrottledTokenObtainPairView.post()` overridden to append org list after JWT generation
- Returns `access`, `refresh`, and `organizations` (id, name, role) in one response
- User looked up by username after `status 200` confirmed — not from `request.user` (which is AnonymousUser post-JWT-auth)
- Test written and passing: `test_login_returns_org_list`

**Frontend — org picker flow**

- `/login` — collects credentials, calls `/api/v1/auth/token/`, stores tokens and org list
- `/pick-org` — reads org list from sessionStorage, renders selectable org buttons with role labels
- `/dashboard/[orgId]` — verifies orgId against sessionStorage, fetches fundraisers from `/api/v1/organizations/<orgId>/fundraisers/` using Bearer token, renders empty state correctly

**Security discussion — HttpOnly cookie tradeoff**

- Documented why refresh token in localStorage is a temporary, acceptable risk at current stage
- Documented why HttpOnly + Secure + SameSite=Strict is the correct final state
- ADR-008 written and appended to decisions.md

## Key principles reinforced today

- Authentication (who are you) and authorization context (which org are you acting as) change at different rates — never bundle them in the same token
- sessionStorage org check is a UX control, not a security control — security lives on the server (`get_membership_or_404()`)
- Client-side validation is UX-only — an attacker using curl never touches the browser
- HttpOnly closes XSS theft vector; SameSite=Strict closes the CSRF vector HttpOnly introduces
- 400 = malformed request (nothing to check yet); 404 = valid request, existence denied (information hiding)

## Deferred

- Refresh token HttpOnly cookie — requires backend to set `Set-Cookie` header on login and read cookie on refresh (ADR-008, must land before Phase 3)
- CSRF middleware wiring for the HttpOnly cookie flow

## Next up — Week 3, Day 3 (Wednesday Integration)

- Wire frontend login flow to handle token expiry and refresh
- Ensure every authenticated request uses the access token correctly
- Begin integration testing of the full login → org picker → dashboard flow
