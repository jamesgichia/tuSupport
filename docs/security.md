# Security Model

## Authentication

- JWT-based auth
- Secure token storage
- Refresh token rotation

---

## Authorization

- Role-based access control (RBAC)
- Organization-level isolation

---

## Threat Model

### Risks

- Unauthorized access across tenants
- Payment fraud
- API abuse
- Data leakage

---

## Mitigations

- Strict organization_id filtering
- Input validation on all endpoints
- Rate limiting (future)
- Audit logging for all financial actions

---

## OWASP Focus Areas

- Injection attacks
- Broken authentication
- Sensitive data exposure
- Security misconfiguration
