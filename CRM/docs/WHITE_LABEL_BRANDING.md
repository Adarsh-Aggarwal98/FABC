# White-Label Branding Feature

This document describes the multi-tenant branding feature where each practice (company) can customize their own logo, colors, and branding that all their users see.

## Overview

Each practice owner can configure:
- Company logo
- Primary brand color
- Company name (displayed in header)
- Favicon (optional)
- Email branding

All users under that practice (accountants and clients) will see this custom branding instead of the default CRM branding.

---

## Database Schema

The `companies` table already has these fields:

```sql
-- Existing fields in companies table
logo_url VARCHAR(500),      -- Company logo URL
primary_color VARCHAR(20),  -- Brand color (hex code)
name VARCHAR(200),          -- Company name
trading_name VARCHAR(200),  -- Optional trading name
```

Add additional branding fields:

```sql
ALTER TABLE companies ADD COLUMN favicon_url VARCHAR(500);
ALTER TABLE companies ADD COLUMN secondary_color VARCHAR(20);
ALTER TABLE companies ADD COLUMN email_logo_url VARCHAR(500);
ALTER TABLE companies ADD COLUMN login_background_url VARCHAR(500);
ALTER TABLE companies ADD COLUMN tagline VARCHAR(200);
```

---

## API Endpoints

### Get Company Branding (Public)
```
GET /api/companies/{id}/branding
```
Returns public branding info (no auth required for login page).

**Response:**
```json
{
  "success": true,
  "data": {
    "company_name": "ABC Accounting",
    "trading_name": "ABC Tax Services",
    "logo_url": "https://storage.../abc-logo.png",
    "favicon_url": "https://storage.../abc-favicon.ico",
    "primary_color": "#1E40AF",
    "secondary_color": "#3B82F6",
    "tagline": "Your Trusted Tax Partner"
  }
}
```

### Update Company Branding (Admin Only)
```
PATCH /api/companies/{id}/branding
```

**Request:**
```json
{
  "primary_color": "#1E40AF",
  "secondary_color": "#3B82F6",
  "tagline": "Your Trusted Tax Partner"
}
```

### Upload Company Logo
```
POST /api/companies/{id}/logo
Content-Type: multipart/form-data
```

**Form Data:**
- `logo` - Image file (PNG, JPG, SVG)
- `type` - "main" | "favicon" | "email"

---

## Frontend Implementation

### 1. Branding Context (`src/context/BrandingContext.jsx`)

```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from '../store/authStore';

const BrandingContext = createContext();

export function BrandingProvider({ children }) {
  const { user } = useAuth();
  const [branding, setBranding] = useState({
    companyName: 'Accountant CRM',
    logoUrl: '/logo.svg',
    primaryColor: '#1E40AF',
    secondaryColor: '#3B82F6',
    faviconUrl: '/favicon.ico',
  });

  useEffect(() => {
    if (user?.company_id) {
      fetchBranding(user.company_id);
    }
  }, [user?.company_id]);

  const fetchBranding = async (companyId) => {
    try {
      const response = await fetch(`/api/companies/${companyId}/branding`);
      const data = await response.json();
      if (data.success) {
        setBranding({
          companyName: data.data.trading_name || data.data.company_name,
          logoUrl: data.data.logo_url || '/logo.svg',
          primaryColor: data.data.primary_color || '#1E40AF',
          secondaryColor: data.data.secondary_color || '#3B82F6',
          faviconUrl: data.data.favicon_url || '/favicon.ico',
          tagline: data.data.tagline,
        });

        // Update CSS variables
        document.documentElement.style.setProperty('--color-primary', data.data.primary_color);
        document.documentElement.style.setProperty('--color-secondary', data.data.secondary_color);

        // Update favicon
        if (data.data.favicon_url) {
          const link = document.querySelector("link[rel~='icon']");
          if (link) link.href = data.data.favicon_url;
        }

        // Update page title
        document.title = data.data.trading_name || data.data.company_name;
      }
    } catch (error) {
      console.error('Failed to fetch branding:', error);
    }
  };

  return (
    <BrandingContext.Provider value={{ branding, setBranding, fetchBranding }}>
      {children}
    </BrandingContext.Provider>
  );
}

export const useBranding = () => useContext(BrandingContext);
```

### 2. Update Header Component

```jsx
// src/components/layout/Header.jsx
import { useBranding } from '../../context/BrandingContext';

function Header() {
  const { branding } = useBranding();

  return (
    <header className="bg-white shadow">
      <div className="flex items-center">
        <img
          src={branding.logoUrl}
          alt={branding.companyName}
          className="h-10 w-auto"
        />
        <span className="ml-3 text-xl font-semibold" style={{ color: branding.primaryColor }}>
          {branding.companyName}
        </span>
      </div>
    </header>
  );
}
```

### 3. Update Sidebar Component

```jsx
// src/components/layout/Sidebar.jsx
import { useBranding } from '../../context/BrandingContext';

function Sidebar() {
  const { branding } = useBranding();

  return (
    <aside
      className="w-64 min-h-screen"
      style={{ backgroundColor: branding.primaryColor }}
    >
      <div className="p-4">
        <img
          src={branding.logoUrl}
          alt={branding.companyName}
          className="h-12 w-auto mx-auto"
        />
        <p className="text-white text-center mt-2 text-sm">
          {branding.tagline}
        </p>
      </div>
      {/* Navigation items */}
    </aside>
  );
}
```

### 4. CSS Variables (`src/index.css`)

```css
:root {
  --color-primary: #1E40AF;
  --color-secondary: #3B82F6;
  --color-primary-light: #3B82F6;
  --color-primary-dark: #1E3A8A;
}

/* Use variables throughout */
.btn-primary {
  background-color: var(--color-primary);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.text-primary {
  color: var(--color-primary);
}

.border-primary {
  border-color: var(--color-primary);
}

.sidebar {
  background-color: var(--color-primary);
}
```

---

## Admin Settings UI

### Branding Settings Page (`/settings/branding`)

```
┌─────────────────────────────────────────────────────────────────┐
│  Company Branding Settings                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Company Logo                                                    │
│  ┌─────────────┐                                                │
│  │   [Logo]    │  [Upload New Logo]                             │
│  │   Preview   │  Recommended: 200x60px, PNG or SVG             │
│  └─────────────┘                                                │
│                                                                  │
│  Favicon                                                         │
│  ┌────┐                                                         │
│  │ 🔖 │  [Upload Favicon]                                       │
│  └────┘  Recommended: 32x32px, ICO or PNG                       │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Company Name        [ABC Accounting____________]                │
│  Trading Name        [ABC Tax Services__________]  (optional)   │
│  Tagline             [Your Trusted Tax Partner__]  (optional)   │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Brand Colors                                                    │
│                                                                  │
│  Primary Color    [■] #1E40AF    [Color Picker]                 │
│  Secondary Color  [■] #3B82F6    [Color Picker]                 │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Preview                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [Logo] ABC Tax Services                    [User Menu] │   │
│  │  ─────────────────────────────────────────────────────  │   │
│  │  │ Dashboard  │                                          │   │
│  │  │ Requests   │   Welcome to your portal                │   │
│  │  │ Documents  │                                          │   │
│  │  │ Invoices   │   [Primary Button] [Secondary Button]   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│                              [Cancel]  [Save Changes]            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backend Implementation

### Update Company Model

```python
# backend/app/modules/company/models.py

class Company(db.Model):
    # ... existing fields ...

    # Branding fields
    logo_url = db.Column(db.String(500))
    favicon_url = db.Column(db.String(500))
    email_logo_url = db.Column(db.String(500))
    login_background_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(20), default='#1E40AF')
    secondary_color = db.Column(db.String(20), default='#3B82F6')
    tagline = db.Column(db.String(200))

    def get_branding(self):
        """Return branding info for frontend."""
        return {
            'company_name': self.name,
            'trading_name': self.trading_name,
            'logo_url': self.logo_url,
            'favicon_url': self.favicon_url,
            'primary_color': self.primary_color or '#1E40AF',
            'secondary_color': self.secondary_color or '#3B82F6',
            'tagline': self.tagline,
        }
```

### Branding Routes

```python
# backend/app/modules/company/routes.py

@company_bp.route('/<company_id>/branding', methods=['GET'])
def get_branding(company_id):
    """Get company branding (public endpoint for login page)."""
    company = Company.query.get_or_404(company_id)
    return success_response(company.get_branding())


@company_bp.route('/<company_id>/branding', methods=['PATCH'])
@jwt_required()
@admin_required
def update_branding(company_id):
    """Update company branding settings."""
    company = Company.query.get_or_404(company_id)

    # Verify user is admin of this company
    current_user = get_current_user()
    if current_user.company_id != company_id and current_user.role.name != 'super_admin':
        return error_response("Not authorized", 403)

    data = request.get_json()

    if 'primary_color' in data:
        company.primary_color = data['primary_color']
    if 'secondary_color' in data:
        company.secondary_color = data['secondary_color']
    if 'tagline' in data:
        company.tagline = data['tagline']
    if 'trading_name' in data:
        company.trading_name = data['trading_name']

    db.session.commit()
    return success_response(company.get_branding())


@company_bp.route('/<company_id>/logo', methods=['POST'])
@jwt_required()
@admin_required
def upload_logo(company_id):
    """Upload company logo."""
    company = Company.query.get_or_404(company_id)

    if 'logo' not in request.files:
        return error_response("No file provided", 400)

    file = request.files['logo']
    logo_type = request.form.get('type', 'main')  # main, favicon, email

    # Upload to storage (Azure Blob or local)
    from app.modules.documents.services import DocumentService
    doc_service = DocumentService()

    # Generate unique filename
    filename = f"branding/{company_id}/{logo_type}_{file.filename}"
    url = doc_service.upload_file(file, filename)

    # Update company record
    if logo_type == 'main':
        company.logo_url = url
    elif logo_type == 'favicon':
        company.favicon_url = url
    elif logo_type == 'email':
        company.email_logo_url = url

    db.session.commit()

    return success_response({
        'url': url,
        'type': logo_type
    })
```

---

## Email Branding

Emails sent to clients should include the practice's branding:

```python
# backend/app/modules/notifications/services.py

def send_branded_email(to_email, subject, template_name, context, company_id):
    """Send email with company branding."""
    company = Company.query.get(company_id)

    # Add branding to context
    context['company_name'] = company.trading_name or company.name
    context['company_logo'] = company.email_logo_url or company.logo_url
    context['primary_color'] = company.primary_color or '#1E40AF'

    # Render template with branding
    html_content = render_template(
        f'emails/{template_name}.html',
        **context
    )

    # Send email
    send_email(to_email, subject, html_content)
```

### Email Template Example

```html
<!-- templates/emails/base.html -->
<!DOCTYPE html>
<html>
<head>
  <style>
    .header { background-color: {{ primary_color }}; padding: 20px; }
    .logo { max-height: 50px; }
    .btn { background-color: {{ primary_color }}; color: white; padding: 12px 24px; }
  </style>
</head>
<body>
  <div class="header">
    {% if company_logo %}
    <img src="{{ company_logo }}" alt="{{ company_name }}" class="logo">
    {% else %}
    <h1 style="color: white;">{{ company_name }}</h1>
    {% endif %}
  </div>

  <div class="content">
    {% block content %}{% endblock %}
  </div>

  <div class="footer">
    <p>© {{ company_name }}</p>
  </div>
</body>
</html>
```

---

## Login Page Branding

For client portal login, show practice branding:

```jsx
// src/pages/auth/Login.jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function Login() {
  const { companySlug } = useParams();  // e.g., /login/abc-accounting
  const [branding, setBranding] = useState(null);

  useEffect(() => {
    if (companySlug) {
      fetchCompanyBranding(companySlug);
    }
  }, [companySlug]);

  const fetchCompanyBranding = async (slug) => {
    const response = await fetch(`/api/companies/by-slug/${slug}/branding`);
    const data = await response.json();
    if (data.success) {
      setBranding(data.data);
      document.documentElement.style.setProperty('--color-primary', data.data.primary_color);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{
        backgroundImage: branding?.login_background_url
          ? `url(${branding.login_background_url})`
          : 'none'
      }}
    >
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        {branding?.logo_url ? (
          <img
            src={branding.logo_url}
            alt={branding.company_name}
            className="h-16 mx-auto mb-6"
          />
        ) : (
          <h1 className="text-2xl font-bold text-center mb-6">
            {branding?.company_name || 'Client Portal'}
          </h1>
        )}

        {branding?.tagline && (
          <p className="text-gray-600 text-center mb-6">{branding.tagline}</p>
        )}

        {/* Login form */}
        <form>
          {/* ... */}
        </form>
      </div>
    </div>
  );
}
```

---

## URL Structure for Client Portals

Each practice can have a custom URL:

```
# Default login
https://app.yourcrm.com/login

# Practice-specific login (by slug)
https://app.yourcrm.com/login/abc-accounting

# Or subdomain (advanced)
https://abc-accounting.yourcrm.com/login
```

---

## Summary

| Feature | Who Can Configure | Who Sees It |
|---------|-------------------|-------------|
| Logo | Practice Admin | All practice users |
| Colors | Practice Admin | All practice users |
| Company Name | Practice Admin | All practice users |
| Tagline | Practice Admin | All practice users |
| Email Branding | Practice Admin | Email recipients |
| Login Page | Practice Admin | Anyone at login URL |

---

## Implementation Checklist

- [ ] Add branding fields to companies table
- [ ] Create branding API endpoints
- [ ] Implement BrandingContext in frontend
- [ ] Update Header/Sidebar components
- [ ] Create branding settings page
- [ ] Implement logo upload
- [ ] Add CSS variables support
- [ ] Update email templates
- [ ] Create practice-specific login URLs
- [ ] Add favicon update logic
