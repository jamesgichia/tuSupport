# Engineering Log

This file records all major architectural decisions.

---

## 2026-06-18

### Decision

Use shared database multi-tenant architecture with `organization_id`.

### Reason

- Simplifies scaling
- Standard SaaS pattern
- Easier Django implementation
- Avoids schema complexity

### Alternatives Considered

- Schema-per-tenant (rejected due to complexity)

---

## Rule

All future major decisions must be logged here.
