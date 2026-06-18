# Database Design

## Core Tables

### users

- id
- email
- password
- role
- organization_id
- created_at

---

### organizations

- id
- name
- type (church, chama, NGO, etc)

---

### fundraisers

- id
- organization_id
- title
- description
- goal_amount
- status
- created_at

---

### contributions

- id
- fundraiser_id
- organization_id
- amount
- method (mpesa/manual)
- status
- transaction_reference
- created_at

---

### audit_logs

- id
- organization_id
- action
- actor_id
- metadata
- created_at
