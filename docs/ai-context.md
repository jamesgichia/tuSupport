# AI Context for tuSupport

## Project

Multi-tenant SaaS fundraiser system (Kenya-focused)

## Stack

- Django + DRF
- Next.js + TypeScript
- PostgreSQL

## Key Features

- M-Pesa payments
- Manual contributions
- WhatsApp notifications
- Audit logging
- Multi-tenant organizations

## Architecture

Shared database multi-tenant model using organization_id isolation

## Current Phase

Week 1 - Setup

## Rules

- Security is mandatory, not optional
- All data must be tenant-isolated
- All financial actions must be auditable
