# tuSupport — Current Progress

> Snapshot of where the project stands right now. Overwrite this each session — do not append.

**Phase:** Foundation (Week 1 of 12)
**Last updated:** Week 1, Day 3 — closed
**Active branch:** `feature/lead-capture`

## Stack status

- **Backend:** Django 5.2.15 LTS, DRF, django-environ, django-cors-headers — in `backend/`, venv-isolated. `requirements.txt` now exists for the first time and is the dependency source of truth.
- **Database:** PostgreSQL 18, Docker Compose (`tusupport_postgres`). Volume was destroyed and recreated this session — fully re-migrated; `core`, `auth`, `admin`, `sessions`, `contenttypes`, and `leads` are all applied and consistent.
- **Frontend:** Next.js, in `frontend/`. `EmailSignup.tsx` now performs a real POST to `/api/v1/leads/`, replacing the Day 2 TODO mockup. Confirmed working end-to-end in browser.

## Completed — Week 1, Day 3 (closed)

- New `leads` app created — deliberately outside `core` and outside the `TenantScopedModel` hierarchy. A lead has no organization at the point of capture; forcing tenancy onto pre-tenancy data would be a category error.
- `Lead` model: `email` (`EmailField`, `unique=True`), `created_at` (`auto_now_add`). Migrated; `dependencies = []` confirmed — zero coupling to tenancy.
- `LeadSerializer` (`ModelSerializer`, `fields = ['email']`) — explicit allow-list; `id`/`created_at` are not client-writable, by construction.
- `LeadCreateView` (`generics.CreateAPIView`), routed at `/api/v1/leads/` — versioned per scope.md §4.1.
- `django-cors-headers` installed; `CORS_ALLOWED_ORIGINS` explicit allow-list (`localhost:3000`), not `CORS_ALLOW_ALL_ORIGINS`.
- `EmailSignup.tsx` wired to the real endpoint: async `fetch`, success state only set after a confirmed 2xx response, server-side validation errors (e.g. duplicate email) surfaced to the user instead of a generic message.
- Verified end-to-end: `curl` POST (success + duplicate-rejection) and a real browser submission via the running Next.js dev server.
- Branch hygiene: merged completed `feature/frontend-bootstrap` into `main`, deleted it (local + remote); started today's work on a correctly-scoped new branch, `feature/lead-capture`, off `main` — per ADR-003's one-branch-one-capability rule.
- **Environment recovery (unplanned, significant session time):** found and fixed (a) leftover gitignored `__pycache__`-only cruft in an abandoned `backend/` scaffold from a prior partial restructure attempt — confirmed harmless via `git ls-files`/`git check-ignore`, deleted; (b) `.env` located inside `backend/` but read by Compose from repo root — moved to root, `settings.py`'s `read_env()` repointed via `BASE_DIR.parent`; (c) an unquoted `SECRET_KEY` containing `$` characters being misparsed by Compose's variable interpolation — fixed via single-quoting; (d) a phantom venv (`$VIRTUAL_ENV` set to a path that didn't exist on disk) silently falling through to system Python 4.2 — rebuilt fresh inside `backend/venv` with Django 5.2.15, `requirements.txt` generated for the first time (previously didn't exist — closed a real reproducibility gap).
- Confirmed (after a false alarm) that `core`'s Day 1 migration is correctly tracked and present on `main` — git recorded it as a moved file during the earlier `backend/` restructure, which initially made its history look incomplete when checked under its new path alone.

## Day 3 scope.md checklist — final status

- API integration — ✅ done
- Authentication flow linking — N/A (lead capture has no auth; correctly out of scope)
- Data synchronization — ✅ done (frontend ↔ backend confirmed live)

## In progress / next up

- Day 4 (Security & Hardening): rate-limiting/CAPTCHA on `/api/v1/leads/` remains deferred (scope.md §4.2).
- Day 4: CORS configuration deserves an explicit attacker-mindset pass — settings are correct (explicit allow-list) but the underlying reasoning wasn't walked through this session, per ADR-006's standard.
- Standing reminder, unchanged: Celery org-context gap (Phase 3) — pass `organization` explicitly as a task argument, fail loud if missing.
- Process note: when checking whether a file is tracked/has history, verify from a consistent working directory and check both the current path *and* the possibility the path changed earlier (`git mv`/restructure) — several false alarms today came from path-relative confusion, not real gaps.
