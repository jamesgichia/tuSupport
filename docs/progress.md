**Last updated:** Week 3, Day 5 — Friday Review closed

---

## Completed — Week 3, Day 5

**Structured audit across all five layers — no regressions, two actionable gaps identified**

**Database/Schema**
- Tables confirmed: Organization, Membership (User ↔ Org join), Fundraiser, Leads
- `unique_together` on Membership correctly prevents duplicate rows but does NOT prevent role field mutation by unprivileged users — Privilege Escalation (OWASP API6) remains open

**Models/Multi-tenancy**
- TenantManager fail-loud enforcement confirmed correct
- Celery thread-local gap remains deferred per ADR-004

**API Views/Serializers**
- Http404 (not Http403) on tenancy mismatch confirmed — prevents org existence enumeration
- Flat `/api/v1/fundraisers/` route confirmed deleted (not just disabled) — attack surface removed
- Detail endpoint `GET .../fundraisers/<id>/` not yet built — IDOR risk; test must be written before implementation

**Auth/Authorization**
- 15-min access token + HttpOnly refresh cookie confirmed correct
- LoginRateThrottle covers single-IP brute force; distributed credential stuffing remains unmitigated (acceptable at current stage)
- `secure=False` on refresh cookie confirmed — production blocker; requires HTTPS + `secure=True` before deployment

**Tests**
- 6/6 passing, confirmed clean
- Gap 1: No role/permission tests — member attempting admin actions is untested
- Gap 2: Detail endpoint IDOR test missing — must precede implementation (Week 4)

---

## Open items carried into Week 4

- [ ] Privilege Escalation: protect Membership role field from unprivileged writes
- [ ] Role/permission tests: member denied on admin-only actions
- [ ] Detail endpoint: write failing IDOR test first, then implement
- [ ] `secure=True` on refresh cookie before any production deployment

---

## Week 3 complete
