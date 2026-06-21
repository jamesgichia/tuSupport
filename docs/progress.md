# tuSupport — Current Progress

> Snapshot of where the project stands right now. Overwrite this each session — do not append. History of *how* we got here lives in `DECISIONS.md` (architectural) or your own git log (everything else).

**Phase:** Foundation (Week 1 of 12)
**Last updated:** Week 1, Day 1

## Stack status

- **Backend:** Django + DRF — not yet bootstrapped
- **Database:** PostgreSQL 18, running via Docker Compose as `tusupport_postgres` — confirmed reachable
- **Frontend:** Next.js / TypeScript — not started

## Environment

- Kali Linux, Python 3.13.12, Docker confirmed working
- DB credentials live in a git-ignored `.env`; app connects as a dedicated user `tusupport_admin` (not the `postgres` superuser)

## Completed

- Dockerized PostgreSQL 18 set up, validated, and verified reachable
- `docker-compose.yml` + `.gitignore` committed to git

## In progress / next up

- Django project bootstrap: virtual environment, `startproject`, app layout
- Environment-variable-based DB config in Django settings
- Multi-tenancy schema decision: how `organization_id` gets enforced across models
