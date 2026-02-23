# Accountant CRM - API Quick Reference

## Base URL
```
Production: https://api.accountantcrm.com/api
Development: http://localhost:5000/api
```

## Authentication

All API requests require JWT authentication (except auth endpoints).

```bash
# Login to get token
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "success": true,
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": { ... }
}

# Use token in subsequent requests
Authorization: Bearer <access_token>
```

---

## API Endpoints Summary

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Login with email/password |
| POST | `/verify-otp` | Verify 2FA OTP code |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Invalidate tokens |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password with OTP |

### Users (`/api/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me` | Get current user profile |
| PATCH | `/me` | Update current user profile |
| GET | `/` | List users (admin only) |
| POST | `/invite` | Invite new user |
| GET | `/:id` | Get user by ID |
| PATCH | `/:id` | Update user |
| DELETE | `/:id` | Deactivate user |

### Companies (`/api/companies`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create company (Super Admin) |
| GET | `/` | List companies (Super Admin) |
| GET | `/my-company` | Get current user's company |
| GET | `/:id` | Get company details |
| PUT | `/:id` | Update company |
| DELETE | `/:id` | Deactivate company |
| GET | `/:id/users` | List company users |
| POST | `/:id/users` | Add user to company |
| GET | `/my-company/usage` | Get plan usage stats |
| PATCH | `/:id/plan` | Update company plan |
| GET | `/plans` | List available plans |

### Services (`/api/services`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List services |
| POST | `/` | Create service |
| GET | `/:id` | Get service details |
| PUT | `/:id` | Update service |
| DELETE | `/:id` | Delete service |
| GET | `/defaults` | List default services |
| POST | `/defaults/:id/activate` | Activate default service |
| GET | `/company-settings` | Get company service settings |
| PUT | `/company-settings/:id` | Update company service settings |

### Service Requests (`/api/requests`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List requests |
| POST | `/` | Create request |
| GET | `/:id` | Get request details |
| PUT | `/:id/assign` | Assign to accountant |
| PUT | `/:id/status` | Update status |
| PUT | `/:id/invoice` | Update invoice details |
| POST | `/:id/notes` | Add internal note |
| GET | `/:id/queries` | Get queries |
| POST | `/:id/queries` | Create query |

### Forms (`/api/forms`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List forms |
| POST | `/` | Create form |
| GET | `/:id` | Get form details |
| PUT | `/:id` | Update form |
| DELETE | `/:id` | Delete form |
| POST | `/:id/clone` | Clone form |
| GET | `/defaults` | List default forms |
| POST | `/company` | Create company form |
| GET | `/company` | List company forms |
| POST | `/:id/responses` | Submit form response |
| GET | `/:id/responses` | List form responses |

### Documents (`/api/documents`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List documents |
| POST | `/` | Upload document |
| GET | `/:id` | Get document details |
| GET | `/:id/download` | Get download URL |
| DELETE | `/:id` | Delete document |
| GET | `/user/:id` | Get user's documents |

### Invoices (`/api/services/invoices`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List invoices |
| POST | `/` | Create invoice |
| GET | `/:id` | Get invoice details |
| PATCH | `/:id` | Update invoice |
| POST | `/:id/send` | Send invoice to client |
| POST | `/:id/payments` | Add payment |
| POST | `/:id/cancel` | Cancel invoice |

### Payments (`/api/payments`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/config` | Get Stripe public key |
| POST | `/invoices/:id/checkout` | Create Stripe checkout |
| POST | `/invoices/:id/payment-intent` | Create payment intent |
| POST | `/invoices/:id/payment-link` | Generate payment link |
| GET | `/checkout-session/:id` | Get checkout session |
| GET | `/invoices/:id/payments` | Get invoice payments |
| POST | `/webhooks/stripe` | Stripe webhook handler |

### Notifications (`/api/notifications`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List notifications |
| GET | `/unread-count` | Get unread count |
| PATCH | `/:id/read` | Mark as read |
| POST | `/mark-all-read` | Mark all as read |
| GET | `/email-templates` | List templates |
| POST | `/email-templates` | Create template |
| POST | `/bulk-email` | Send bulk email |
| GET | `/bulk-email/filters` | Get filter options |
| POST | `/bulk-email/preview` | Preview recipients |
| POST | `/bulk-email/filtered` | Send filtered email |
| GET | `/scheduled-emails` | List scheduled |
| POST | `/scheduled-emails` | Create scheduled |
| GET | `/automations` | List automations |
| POST | `/automations` | Create automation |
| GET | `/automations/triggers` | List trigger types |

### Tags (`/api/tags`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List tags |
| POST | `/` | Create tag |
| PATCH | `/:id` | Update tag |
| DELETE | `/:id` | Delete tag |
| GET | `/users/:id/tags` | Get user's tags |
| POST | `/users/:id/tags` | Assign tag to user |
| DELETE | `/users/:id/tags/:tagId` | Remove tag from user |

### Analytics (`/api/analytics`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Dashboard metrics |
| GET | `/revenue` | Revenue stats |
| GET | `/requests` | Request statistics |
| GET | `/workload` | Team workload |
| GET | `/bottlenecks` | Bottleneck analysis |

### Audit (`/api/activity`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List activity logs |
| GET | `/user/:id` | User activity |
| GET | `/entity/:type/:id` | Entity history |
| POST | `/impersonate/:id` | Start impersonation |
| POST | `/impersonate/stop` | Stop impersonation |
| GET | `/impersonate/history` | Impersonation history |

---

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "errors": { "field": ["error1", "error2"] }
}
```

### Pagination
```json
{
  "success": true,
  "items": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Server Error |

---

## Rate Limits

| Plan | Requests/Minute |
|------|-----------------|
| Starter | 60 |
| Standard | 120 |
| Premium | 300 |
| Enterprise | Custom |

---

## Webhooks (Stripe)

Configure webhook endpoint: `POST /api/payments/webhooks/stripe`

Events to subscribe:
- `checkout.session.completed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `charge.refunded`
