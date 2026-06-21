# tuSupport — Current Progress

> Snapshot of where the project stands right now. Overwrite this each session — do not append. History of *how* we got here lives in `DECISIONS.md` (architectural) or your own git log (everything else).

**Phase:** Foundation (Week 1 of 12)
**Last updated:** Week 1, Day 1 — CLOSED
**Active branch:** `feature/backend-foundation` (committed, not yet merged to `main`)

## Stack status

- **Backend:** Django 5.2 LTS + django-environ — bootstrapped, connected to Postgres, verified via `migrate`
- **Database:** PostgreSQL 18, Docker Compose (`tusupport_postgres`), reachable at `localhost:5432`, app connects as `tusupport_admin`
- **Frontend:** Next.js / TypeScript — not started (Day 2)

## Environment

- Kali Linux, Python 3.13, venv at `venv/` (gitignored)
- DB credentials in git-ignored `.env`; rotated once this session after a brief exposure incident — current values are clean
- `psycopg[binary]` installed as the Postgres driver (psycopg3, not psycopg2)

## Completed — Week 1, Day 1 (full closure)

- Dockerized PostgreSQL 18 set up, validated, reachable (carried from prior session)
- `.gitignore` fully rebuilt — replaced a leftover Dynamics 365 AL-language template with one accurate to Python/Django/Next.js/Docker
- Git workflow decided and adopted: GitHub Flow, `feature/<desc>` / `fix/<desc>` branches, `main` always deployable (ADR-003)
- `feature/backend-foundation` branch created and used for all Day 1 work
- Multi-tenancy enforcement mechanism decided: abstract base model + custom manager, thread-local context (ADR-004)
- Django 5.2 LTS project bootstrapped (`tusupport`), flat structure at repo root
- `SECRET_KEY` and `DATABASES` both wired through `django-environ`, reading from `.env` — no secrets hardcoded in tracked files
- `core` app created: `Organization` model (concrete, migrated) + `TenantManager` / `TenantScopedModel` (abstract base, no filtering logic yet — placeholder pending middleware)
- End-to-end connection verified: `python manage.py migrate` applied all built-in Django migrations + `core.0001_initial` successfully against real Postgres
- Day 1 work committed on `feature/backend-foundation` (not yet merged to `main`)

## In progress / next up — Week 1, Day 2

- Merge `feature/backend-foundation` → `main` (deliberately left for next session to start with full context)
- Day 2 = Frontend Client (per scope.md's weekly structure) — Next.js/TypeScript bootstrap
- Known deferred gap: `TenantManager.get_queryset()` has no real filtering yet — needs middleware (likely Day 3, Integration Layer) to set the thread-local "current organization" before this becomes functional
