# API Specification (v1)

## Base URL

/api/v1/

---

## Authentication

POST /auth/register/
POST /auth/login/
POST /auth/logout/
POST /auth/refresh/

---

## Organizations

GET /organizations/
POST /organizations/

---

## Fundraisers

GET /fundraisers/
POST /fundraisers/
GET /fundraisers/{id}/
PATCH /fundraisers/{id}/
DELETE /fundraisers/{id}/

---

## Contributions

POST /contributions/manual/
POST /contributions/mpesa/initiate/
POST /contributions/mpesa/callback/
GET /contributions/

---

## Response Format

Success:
{
  "success": true,
  "data": {}
}

Error:
{
  "success": false,
  "message": ""
}
