**Last updated:** Week 1, Day 4 — closed
**Active branch:** `main` (feature/lead-capture merged and deleted, local + remote)

## Completed — Week 1, Day 4 (closed)

- CORS attacker-mindset pass completed: confirmed CORS is browser-enforced only and gives zero protection against direct attackers (curl, Burp Suite); existing `CORS_ALLOWED_ORIGINS` allow-list is correct as-is, no code change needed — only the reasoning was missing, now closed.
- Rate limiting implemented on `/api/v1/leads/`: DRF's built-in `AnonRateThrottle`, `'anon': '20/hour'` in `DEFAULT_THROTTLE_RATES`. Chosen over `django-ratelimit` (no new dependency needed) and over Nginx-level limiting (no reverse proxy in the stack yet — would be premature infrastructure work, out of scope for this branch).
- Threshold set loose (20/hour) deliberately: blast-radius reasoning — false positive on this endpoint costs a real lead permanently; false negative costs only low-value junk rows. Threshold is a function of per-endpoint blast radius, not a fixed default — will be revisited far stricter for the future M-Pesa callback endpoint, where the asymmetry flips.
- CAPTCHA evaluated and explicitly rejected for this endpoint (see decisions.md — new ADR).
- Verified end-to-end: 21 sequential POSTs to `/api/v1/leads/` returned 20× `201`, then `429` on request 21. Confirmed at the database layer too — row count and `created_at` timestamps matched expected (20 new rows, no `test21@example.com` present); 3 pre-existing rows from Day 3 testing accounted for separately.
- `feature/lead-capture` merged to `main` (fast-forward, no conflicts), deleted locally and on remote.

## Known gap, not yet fixed

- DRF's default throttle counter lives in Django's in-memory cache, which is per-process. This is correct and sufficient for today (single dev server process) but will silently under-throttle once multiple Gunicorn workers/containers run in production — each worker gets its own separate counter. Fix when that becomes real: move the cache backend to Redis (shared store all workers read/write), not before. Flagging now so it isn't a surprise later.

## In progress / next up

- Day 5 (Review): scope.md §10 mindset checklist review before Week 2.
- Standing reminder, unchanged: Celery org-context gap (Phase 3) — pass `organization` explicitly as a task argument, fail loud if missing.
- Standing reminder, new: per-process rate-limit counter gap (above) — revisit when multiple workers/containers are introduced.
