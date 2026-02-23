# SMSF FitForMe Admin Dashboard - Access Guide

## Quick Access

| What | URL |
|------|-----|
| **CRM Login** | `http://localhost:5173/login` (dev) or `https://your-domain.com/login` (prod) |
| **SMSF Questions Manager** | `http://localhost:5173/settings/smsf-questions` |
| **SMSF Submissions Viewer** | `http://localhost:5173/settings/smsf-submissions` |

---

## Step-by-Step Access Instructions

### Step 1: Login to CRM

**URL:** `http://localhost:5173/login`

**Credentials (from seed data):**
```
Email:    aggarwal.adarsh98@gmail.com
Password: Big@200650078296
Role:     super_admin
```

> **Note:** Only `super_admin` and `admin` roles can access SMSF management pages.

---

### Step 2: Navigate to SMSF Questions Manager

**Option A - Via Sidebar:**
1. After login, look at the left sidebar
2. Scroll down to find **"SMSF Questions"**
3. Click to open the Questions Manager

**Option B - Direct URL:**
```
http://localhost:5173/settings/smsf-questions
```

---

### Step 3: Manage Questions

On the Questions Manager page, you can:

| Action | How To |
|--------|--------|
| **View all questions** | Questions are grouped by category, displayed automatically |
| **Add new question** | Click **"Add Question"** button (top right) |
| **Edit question** | Click the **pencil icon** on any question row |
| **Change weight** | Edit the weight input directly on the question row |
| **Hide question** | Click the **eye icon** to toggle visibility |
| **Delete question** | Click the **trash icon** |
| **Reset to defaults** | Click **"Reset to Defaults"** button |

---

### Step 4: View Submissions

**URL:** `http://localhost:5173/settings/smsf-submissions`

Or click **"View Submissions"** button on the Questions Manager page.

| Action | How To |
|--------|--------|
| **View all submissions** | Table shows all submissions automatically |
| **View details** | Click the **eye icon** on any row |
| **Export data** | Click **"Export JSON"** button |
| **Delete submission** | Click the **trash icon** on any row |
| **Clear all** | Click **"Clear All"** button |

---

## Role Permissions

| Role | Can Access SMSF Admin? | Notes |
|------|------------------------|-------|
| `super_admin` | ✅ Yes | Full access |
| `admin` | ✅ Yes | Full access |
| `senior_accountant` | ❌ No | Cannot access |
| `accountant` | ❌ No | Cannot access |
| `user` (client) | ❌ No | Cannot access |

---

## Production URLs

Replace `localhost:5173` with your production domain:

| Environment | Base URL |
|-------------|----------|
| Development | `http://localhost:5173` |
| Production | `https://crm.pointersconsulting.com.au` (example) |

**Production URLs:**
```
Login:        https://your-domain.com/login
Questions:    https://your-domain.com/settings/smsf-questions
Submissions:  https://your-domain.com/settings/smsf-submissions
```

---

## Backend API Endpoints (For Developers)

If you need direct API access (e.g., via Postman):

**Base URL:** `http://localhost:5000/api` (dev) or `https://api.your-domain.com/api` (prod)

### Authentication

```bash
# 1. Get JWT Token
POST /api/auth/login
Content-Type: application/json

{
  "email": "aggarwal.adarsh98@gmail.com",
  "password": "Big@200650078296"
}

# Response contains: { "access_token": "eyJ..." }
```

### Questions API

```bash
# List all questions
GET /api/smsf/admin/questions
Authorization: Bearer YOUR_JWT_TOKEN

# Create question
POST /api/smsf/admin/questions
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
{
  "text": "Your question here?",
  "category": "Am I Right for SMSF?",
  "type": "Compliance",
  "weight": 0.05,
  "order": 26,
  "is_active": true
}

# Update question
PUT /api/smsf/admin/questions/{id}
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
{
  "weight": 0.08
}

# Delete question
DELETE /api/smsf/admin/questions/{id}
Authorization: Bearer YOUR_JWT_TOKEN

# Reset to defaults
POST /api/smsf/admin/questions/reset
Authorization: Bearer YOUR_JWT_TOKEN
```

### Submissions API

```bash
# List submissions
GET /api/smsf/admin/submissions?page=1&per_page=20
Authorization: Bearer YOUR_JWT_TOKEN

# Get single submission
GET /api/smsf/admin/submissions/{id}
Authorization: Bearer YOUR_JWT_TOKEN

# Delete submission
DELETE /api/smsf/admin/submissions/{id}
Authorization: Bearer YOUR_JWT_TOKEN

# Clear all submissions
DELETE /api/smsf/admin/submissions/clear
Authorization: Bearer YOUR_JWT_TOKEN

# Export all
GET /api/smsf/admin/submissions/export
Authorization: Bearer YOUR_JWT_TOKEN

# Get statistics
GET /api/smsf/admin/stats
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Troubleshooting

### "Access Denied" or Redirect to Dashboard
- **Cause:** Your user role is not `super_admin` or `admin`
- **Fix:** Login with an admin account

### "Failed to fetch questions"
- **Cause:** Backend server not running or API error
- **Fix:** Ensure backend is running on port 5000

### Page Not Found (404)
- **Cause:** Frontend not rebuilt after adding routes
- **Fix:** Restart the frontend dev server (`npm run dev`)

### Sidebar doesn't show "SMSF Questions"
- **Cause:** Not logged in as super_admin or admin
- **Fix:** Login with correct role

---

## Default Admin Credentials Reference

From `dbbackup/seed_system_data.sql`:

| Field | Value |
|-------|-------|
| Email | `aggarwal.adarsh98@gmail.com` |
| Password | `Big@200650078296` |
| Role | `super_admin` |
| Company | Pointers Consulting |

---

## Screenshots Reference

### Questions Manager Location in Sidebar
```
Sidebar Menu:
├── Dashboard
├── Users
├── Client Entities
├── Requests
├── Services
├── Workflows
├── Board Statuses
├── Forms
├── Job Analytics
├── Client Analytics
├── Company Settings
├── Invoice Settings
├── Email Templates
├── Branding
├── Data Import
└── SMSF Questions  <-- HERE
```

### Questions Manager Features
```
┌─────────────────────────────────────────────────────────────┐
│  SMSF FitForMe Questions                                    │
│  Manage assessment questions and weightages                 │
│                                                             │
│  [View Submissions]  [Reset to Defaults]  [+ Add Question]  │
├─────────────────────────────────────────────────────────────┤
│  Stats: 150 submissions | 72.5% avg | 45 high scorers       │
├─────────────────────────────────────────────────────────────┤
│  Total Weight: 1.00 (25 active / 25 total)                  │
├─────────────────────────────────────────────────────────────┤
│  Category: "Am I Right for SMSF?"                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 1  Do you understand that only licensed...  Weight: 0.05││
│  │    [Compliance]                           👁 ✏️ 🗑       ││
│  └─────────────────────────────────────────────────────────┘│
│  ... more questions ...                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Support

For technical issues, contact the development team or check:
- Backend logs: `backend/logs/`
- Frontend console: Browser DevTools > Console
