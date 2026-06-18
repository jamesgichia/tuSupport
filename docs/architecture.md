# tuSupport Architecture

## Overview

tuSupport is a multi-tenant SaaS platform for managing harambee-style fundraisers. It supports M-Pesa payments, manual contributions, WhatsApp notifications, and audit-grade financial tracking.

---

## High-Level Architecture

Frontend:

- Next.js (App Router)
- TypeScript
- Tailwind CSS

Backend:

- Django + Django REST Framework
- PostgreSQL

Async Layer (future):

- Celery + Redis

External Integrations:

- Safaricom M-Pesa Daraja API
- WhatsApp Business API

---

## Multi-Tenant Model

- Shared database
- All core tables include `organization_id`
- Strict tenant isolation enforced at API layer

---

## Core System Layers

1. Presentation Layer (Next.js)
2. API Layer (Django REST Framework)
3. Service Layer (Business logic)
4. Data Layer (PostgreSQL)

---

## Key Design Principles

- Security by default
- Auditability of financial actions
- Stateless API design
- Strict tenant isolation
- Event-driven extensibility
