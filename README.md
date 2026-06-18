# tuSupport

A multi-tenant SaaS platform for managing community-based fundraising (harambee) systems with integrated M-Pesa payments, manual contribution tracking, WhatsApp notifications, and audit-grade financial transparency.

---

## Overview

tuSupport is a full-stack SaaS application designed to digitize informal fundraising structures commonly used in community welfare systems, churches, chamas, and local organizations.

The platform provides a structured, secure, and scalable way to:

- Create and manage fundraising campaigns
- Accept contributions via M-Pesa and manual methods
- Track financial inflows and outflows
- Manage beneficiaries and welfare cases
- Send automated WhatsApp notifications
- Maintain full audit trails for financial accountability

---

## Problem Statement

Informal fundraising systems (harambees) often suffer from:

- Lack of transparency in fund usage
- Manual tracking errors
- No centralized record of contributions
- Difficulty in auditing financial flows
- Limited visibility for contributors

tuSupport solves this by introducing a structured SaaS layer over community fundraising.

---

## Core Features

### Fundraising System

- Create and manage fundraising campaigns
- Campaign lifecycle management (draft, active, closed)
- Goal tracking and progress monitoring

### Contributions Management

- M-Pesa STK Push integration
- Manual contribution entry (cash, bank transfer, etc.)
- Transaction tracking and reconciliation
- Contribution history per user and fundraiser

### Multi-Tenant Architecture

- Organization-based isolation
- Each organization operates independently
- Shared database with strict data separation

### Financial Tracking

- Ledger-style transaction recording
- Expense tracking
- Balance computation per fundraiser
- Audit-ready financial history

### Communication System

- WhatsApp notifications (integration-ready)
- Contribution confirmations
- Campaign updates
- System alerts

### Audit & Logging

- Full activity logging system
- Financial event tracking
- Admin-level audit visibility

---

## Tech Stack

### Backend

- Django
- Django REST Framework
- PostgreSQL

### Frontend

- Next.js (App Router)
- TypeScript
- Tailwind CSS

### Infrastructure (Planned)

- Docker
- Nginx
- Linux VPS deployment

### External Integrations

- Safaricom M-Pesa Daraja API
- WhatsApp Business API

### Background Processing (Planned)

- Celery
- Redis

---

## Architecture Overview

tuSupport follows a modular monolithic architecture:

- Frontend (Next.js) handles UI and client logic
- Backend (Django REST API) handles business logic
- PostgreSQL stores structured relational data
- External services handle payments and messaging

### Multi-Tenant Model

- Shared database architecture
- All core tables include `organization_id`
- Strict tenant isolation enforced at API level

---

## Security Principles

Security is a first-class concern in tuSupport.

- JWT-based authentication
- Role-based access control (RBAC)
- Strict input validation
- Organization-level data isolation
- Audit logging for sensitive operations
- Secure handling of financial transactions

---

## API Design (v1)

All endpoints are versioned:


### Authentication

- POST `/auth/register/`
- POST `/auth/login/`
- POST `/auth/logout/`
- POST `/auth/refresh/`

### Fundraisers

- GET `/fundraisers/`
- POST `/fundraisers/`
- GET `/fundraisers/{id}/`
- PATCH `/fundraisers/{id}/`
- DELETE `/fundraisers/{id}/`

### Contributions

- POST `/contributions/manual/`
- POST `/contributions/mpesa/initiate/`
- POST `/contributions/mpesa/callback/`
- GET `/contributions/`

---

## Development Philosophy

This project follows a production-first engineering approach:

- Security by design, not as an afterthought
- Explicit multi-tenant isolation
- API-first backend design
- Component-based frontend architecture
- Event-driven integration for payments and notifications
- Auditability of all financial actions

---

## Project Structure (Planned)
backend/
accounts/
fundraisers/
contributions/
core/

frontend/
app/
components/
features/
lib/
hooks/

docs/
architecture.md
api-spec.md
database-design.md
security.md
system-state.md
---

## Roadmap

### Phase 1: Foundation (Weeks 1–3)

- Project setup
- Authentication system
- Multi-tenant architecture
- Database design

### Phase 2: Core Features (Weeks 4–8)

- Fundraiser management
- Contributions system
- Beneficiary tracking
- Audit system
- Notifications

### Phase 3: Integrations (Weeks 9–10)

- M-Pesa integration
- WhatsApp integration
- Background job processing

### Phase 4: Production (Weeks 11–12)

- Testing and QA
- Security hardening
- Performance optimization
- Deployment

---

## Success Criteria

The system is considered successful if:

- Organizations can independently manage fundraisers
- Contributions are reliably tracked via M-Pesa and manual entry
- Financial records are auditable and consistent
- Data is strictly isolated between organizations
- System can be deployed to production environment
- Security risks are mitigated according to OWASP principles

---

## Status

> 🚧 Active Development — Week 1 (Foundation Phase)

---

## Author

Built as part of a 12-week full-stack SaaS engineering program focused on:

- Django backend engineering
- Next.js frontend systems
- Secure API design
- Payment integration (M-Pesa)
- Production-grade system architecture
