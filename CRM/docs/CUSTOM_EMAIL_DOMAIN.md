# Custom Email Domain Configuration

This document describes how practice owners can configure their own email domain to send emails to clients, instead of using the default CRM email domain.

## Overview

By default, all emails are sent from the CRM's email domain (e.g., `noreply@accountantcrm.com`). With custom email domain setup, each practice can send emails from their own domain:

- `notifications@abcaccounting.com.au`
- `invoices@smithtax.com`
- `support@yourtaxpartner.com.au`

---

## Options for Custom Email

### Option 1: SMTP Credentials (Recommended)
Practice provides their own SMTP server credentials.

### Option 2: Microsoft 365 Integration
Connect to practice's Microsoft 365 account via OAuth.

### Option 3: Google Workspace Integration
Connect to practice's Google Workspace via OAuth.

### Option 4: SendGrid/Mailgun Subuser
Practice creates their own SendGrid/Mailgun account.

---

## Database Schema

```sql
CREATE TABLE company_email_settings (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id) UNIQUE,

    -- Email provider type
    provider VARCHAR(50) NOT NULL DEFAULT 'default',
    -- Options: 'default', 'smtp', 'microsoft365', 'google', 'sendgrid', 'mailgun'

    -- Sender details
    sender_email VARCHAR(200),
    sender_name VARCHAR(200),
    reply_to_email VARCHAR(200),

    -- SMTP Settings (encrypted)
    smtp_host VARCHAR(200),
    smtp_port INTEGER,
    smtp_username VARCHAR(200),
    smtp_password_encrypted TEXT,  -- Encrypted at rest
    smtp_use_tls BOOLEAN DEFAULT TRUE,

    -- OAuth Settings (for Microsoft 365 / Google)
    oauth_client_id VARCHAR(200),
    oauth_client_secret_encrypted TEXT,
    oauth_tenant_id VARCHAR(200),  -- For Microsoft 365
    oauth_refresh_token_encrypted TEXT,
    oauth_token_expires_at TIMESTAMP,

    -- SendGrid/Mailgun Settings
    api_key_encrypted TEXT,
    domain VARCHAR(200),  -- For Mailgun

    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    last_error TEXT,
    last_error_at TIMESTAMP,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    configured_by_id VARCHAR(36) REFERENCES users(id)
);

-- Email sending logs per company
CREATE TABLE email_logs (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(36) REFERENCES companies(id),
    recipient_email VARCHAR(200) NOT NULL,
    sender_email VARCHAR(200),
    subject VARCHAR(500),
    template_name VARCHAR(100),
    status VARCHAR(50),  -- 'sent', 'failed', 'bounced', 'delivered'
    provider_message_id VARCHAR(200),
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP
);
```

---

## Option 1: SMTP Configuration

### Admin UI Settings

```
┌─────────────────────────────────────────────────────────────────┐
│  Email Settings                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Email Provider                                                  │
│  ○ Use Default (noreply@accountantcrm.com)                      │
│  ● Custom SMTP Server                                           │
│  ○ Microsoft 365                                                │
│  ○ Google Workspace                                             │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  SMTP Configuration                                              │
│                                                                  │
│  SMTP Host      [mail.abcaccounting.com.au___]                  │
│  SMTP Port      [587_]  ☑ Use TLS                               │
│  Username       [notifications@abcaccounting.com.au]            │
│  Password       [••••••••••••]                                  │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Sender Details                                                  │
│                                                                  │
│  From Email     [notifications@abcaccounting.com.au]            │
│  From Name      [ABC Accounting_________________]               │
│  Reply-To       [support@abcaccounting.com.au___]  (optional)   │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Status: ✓ Verified (Last tested: 5 mins ago)                   │
│                                                                  │
│           [Send Test Email]  [Save Settings]                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Implementation

```python
# backend/app/modules/notifications/email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
from flask import current_app

class EmailService:
    def __init__(self, company_id=None):
        self.company_id = company_id
        self.settings = self._get_email_settings()

    def _get_email_settings(self):
        """Get email settings for company or use default."""
        if self.company_id:
            from app.modules.company.models import CompanyEmailSettings
            settings = CompanyEmailSettings.query.filter_by(
                company_id=self.company_id,
                is_verified=True
            ).first()
            if settings:
                return settings
        return None  # Use default

    def send_email(self, to_email, subject, html_content, reply_to=None):
        """Send email using company's configured provider or default."""
        if self.settings:
            return self._send_custom_email(to_email, subject, html_content, reply_to)
        else:
            return self._send_default_email(to_email, subject, html_content, reply_to)

    def _send_custom_email(self, to_email, subject, html_content, reply_to):
        """Send via company's custom email configuration."""
        provider = self.settings.provider

        if provider == 'smtp':
            return self._send_smtp(to_email, subject, html_content, reply_to)
        elif provider == 'microsoft365':
            return self._send_microsoft365(to_email, subject, html_content, reply_to)
        elif provider == 'google':
            return self._send_google(to_email, subject, html_content, reply_to)
        elif provider == 'sendgrid':
            return self._send_sendgrid(to_email, subject, html_content, reply_to)
        elif provider == 'mailgun':
            return self._send_mailgun(to_email, subject, html_content, reply_to)

    def _send_smtp(self, to_email, subject, html_content, reply_to):
        """Send email via custom SMTP server."""
        try:
            # Decrypt password
            password = self._decrypt(self.settings.smtp_password_encrypted)

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.settings.sender_name} <{self.settings.sender_email}>"
            msg['To'] = to_email
            if reply_to or self.settings.reply_to_email:
                msg['Reply-To'] = reply_to or self.settings.reply_to_email

            msg.attach(MIMEText(html_content, 'html'))

            # Connect and send
            if self.settings.smtp_use_tls:
                server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port)

            server.login(self.settings.smtp_username, password)
            server.sendmail(
                self.settings.sender_email,
                to_email,
                msg.as_string()
            )
            server.quit()

            self._log_email(to_email, subject, 'sent')
            return True

        except Exception as e:
            self._log_email(to_email, subject, 'failed', str(e))
            self._update_error(str(e))
            raise

    def _send_microsoft365(self, to_email, subject, html_content, reply_to):
        """Send email via Microsoft Graph API."""
        import requests

        # Get valid access token (refresh if needed)
        access_token = self._get_ms365_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        email_data = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'HTML',
                    'content': html_content
                },
                'toRecipients': [{'emailAddress': {'address': to_email}}],
                'from': {
                    'emailAddress': {
                        'address': self.settings.sender_email,
                        'name': self.settings.sender_name
                    }
                }
            }
        }

        if reply_to or self.settings.reply_to_email:
            email_data['message']['replyTo'] = [{
                'emailAddress': {'address': reply_to or self.settings.reply_to_email}
            }]

        response = requests.post(
            f'https://graph.microsoft.com/v1.0/users/{self.settings.sender_email}/sendMail',
            headers=headers,
            json=email_data
        )

        if response.status_code == 202:
            self._log_email(to_email, subject, 'sent')
            return True
        else:
            error = response.json().get('error', {}).get('message', response.text)
            self._log_email(to_email, subject, 'failed', error)
            raise Exception(f"Microsoft 365 error: {error}")

    def _decrypt(self, encrypted_value):
        """Decrypt sensitive value."""
        key = current_app.config['ENCRYPTION_KEY']
        f = Fernet(key)
        return f.decrypt(encrypted_value.encode()).decode()

    def _log_email(self, to_email, subject, status, error=None):
        """Log email sending attempt."""
        from app.modules.notifications.models import EmailLog
        log = EmailLog(
            company_id=self.company_id,
            recipient_email=to_email,
            sender_email=self.settings.sender_email if self.settings else None,
            subject=subject,
            status=status,
            error_message=error
        )
        db.session.add(log)
        db.session.commit()

    def test_connection(self):
        """Test email configuration by sending test email."""
        test_email = self.settings.sender_email
        subject = "Email Configuration Test"
        html = "<p>This is a test email to verify your email configuration.</p>"

        try:
            self.send_email(test_email, subject, html)
            self.settings.is_verified = True
            self.settings.verified_at = datetime.utcnow()
            self.settings.last_error = None
            db.session.commit()
            return True, "Test email sent successfully"
        except Exception as e:
            self.settings.is_verified = False
            self.settings.last_error = str(e)
            self.settings.last_error_at = datetime.utcnow()
            db.session.commit()
            return False, str(e)
```

---

## Option 2: Microsoft 365 Integration

### Setup Steps

1. **Register App in Azure AD**
   - Go to https://portal.azure.com
   - Azure Active Directory → App registrations → New
   - Add redirect URI: `https://yourcrm.com/api/email/microsoft365/callback`
   - API Permissions: `Mail.Send` (Delegated)
   - Create client secret

2. **Connect in CRM**
   - Admin goes to Settings → Email
   - Select "Microsoft 365"
   - Click "Connect Microsoft 365"
   - Authorize with Microsoft account
   - Select mailbox to send from

### OAuth Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CRM UI    │     │  CRM API    │     │ Microsoft   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │ Click Connect     │                   │
       │──────────────────>│                   │
       │                   │                   │
       │                   │ Redirect to OAuth │
       │<──────────────────│──────────────────>│
       │                   │                   │
       │                   │  User authorizes  │
       │                   │<──────────────────│
       │                   │                   │
       │                   │ Exchange code     │
       │                   │──────────────────>│
       │                   │                   │
       │                   │ Access + Refresh  │
       │                   │<──────────────────│
       │                   │                   │
       │  Success          │ Store tokens      │
       │<──────────────────│                   │
       │                   │                   │
```

---

## Option 3: Google Workspace

### Setup Steps

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Create new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Add redirect URI

2. **Connect in CRM**
   - Admin goes to Settings → Email
   - Select "Google Workspace"
   - Click "Connect Google"
   - Sign in with Google account
   - Grant Gmail send permission

---

## Option 4: SendGrid Integration

### Setup Steps

1. **Create SendGrid Account**
   - Sign up at https://sendgrid.com
   - Verify your sending domain (DNS records)
   - Create API key with Mail Send permission

2. **Configure in CRM**
   - Admin goes to Settings → Email
   - Select "SendGrid"
   - Enter API key
   - Enter verified sender email

### Domain Verification

SendGrid requires domain verification:

```
DNS Records to Add:
─────────────────────────────────────────────────────────
Type    Host                         Value
─────────────────────────────────────────────────────────
CNAME   em1234.yourdomain.com        u1234.wl.sendgrid.net
CNAME   s1._domainkey.yourdomain.com s1.domainkey.u1234.wl.sendgrid.net
CNAME   s2._domainkey.yourdomain.com s2.domainkey.u1234.wl.sendgrid.net
─────────────────────────────────────────────────────────
```

---

## API Endpoints

### Get Email Settings
```
GET /api/companies/{id}/email-settings
Authorization: Bearer {admin_token}
```

### Update Email Settings
```
PATCH /api/companies/{id}/email-settings
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "provider": "smtp",
  "sender_email": "notifications@abcaccounting.com.au",
  "sender_name": "ABC Accounting",
  "smtp_host": "mail.abcaccounting.com.au",
  "smtp_port": 587,
  "smtp_username": "notifications@abcaccounting.com.au",
  "smtp_password": "your-password",
  "smtp_use_tls": true
}
```

### Test Email Configuration
```
POST /api/companies/{id}/email-settings/test
Authorization: Bearer {admin_token}
```

### Microsoft 365 OAuth Connect
```
GET /api/email/microsoft365/connect?company_id={id}
```
Redirects to Microsoft OAuth page.

### Microsoft 365 OAuth Callback
```
GET /api/email/microsoft365/callback?code=xxx&state=xxx
```

### Disconnect Email Provider
```
POST /api/companies/{id}/email-settings/disconnect
Authorization: Bearer {admin_token}
```

---

## Email Logs & Analytics

### View Email Logs
```
GET /api/companies/{id}/email-logs?page=1&per_page=50
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "emails": [
      {
        "id": 1,
        "recipient_email": "client@example.com",
        "sender_email": "notifications@abcaccounting.com.au",
        "subject": "Your Invoice is Ready",
        "status": "delivered",
        "sent_at": "2025-01-18T10:30:00Z",
        "delivered_at": "2025-01-18T10:30:05Z",
        "opened_at": "2025-01-18T11:15:00Z"
      }
    ],
    "stats": {
      "total_sent": 150,
      "delivered": 145,
      "failed": 3,
      "bounced": 2,
      "open_rate": "68%"
    }
  }
}
```

---

## Security Considerations

### 1. Credential Encryption
All sensitive credentials are encrypted at rest:

```python
from cryptography.fernet import Fernet

# Generate key (store in environment)
ENCRYPTION_KEY = Fernet.generate_key()

# Encrypt
def encrypt_credential(value):
    f = Fernet(current_app.config['ENCRYPTION_KEY'])
    return f.encrypt(value.encode()).decode()

# Decrypt
def decrypt_credential(encrypted_value):
    f = Fernet(current_app.config['ENCRYPTION_KEY'])
    return f.decrypt(encrypted_value.encode()).decode()
```

### 2. Rate Limiting
Prevent email abuse:

```python
# Max 100 emails per hour per company
# Max 1000 emails per day per company

from flask_limiter import Limiter

limiter = Limiter(key_func=get_company_id)

@limiter.limit("100/hour;1000/day")
def send_email():
    ...
```

### 3. SPF/DKIM/DMARC
Recommend practices configure:

```
SPF Record:
v=spf1 include:_spf.google.com include:sendgrid.net ~all

DKIM: (Provider specific)

DMARC Record:
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
```

---

## Fallback Behavior

If custom email fails, system can fallback to default:

```python
def send_email_with_fallback(company_id, to_email, subject, html):
    """Try custom email, fallback to default on failure."""
    try:
        # Try company's custom email
        service = EmailService(company_id)
        return service.send_email(to_email, subject, html)
    except Exception as e:
        logger.error(f"Custom email failed: {e}")

        # Fallback to default
        if current_app.config.get('EMAIL_FALLBACK_ENABLED'):
            default_service = EmailService()  # No company_id = default
            return default_service.send_email(to_email, subject, html)
        else:
            raise
```

---

## Common SMTP Settings

| Provider | Host | Port | TLS |
|----------|------|------|-----|
| Office 365 | smtp.office365.com | 587 | Yes |
| Gmail | smtp.gmail.com | 587 | Yes |
| Outlook.com | smtp-mail.outlook.com | 587 | Yes |
| Yahoo | smtp.mail.yahoo.com | 587 | Yes |
| Zoho | smtp.zoho.com | 587 | Yes |
| Amazon SES | email-smtp.region.amazonaws.com | 587 | Yes |

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Authentication failed | Wrong credentials | Verify username/password |
| Connection refused | Wrong host/port | Check SMTP settings |
| Certificate error | TLS issue | Enable/disable TLS |
| Sender not allowed | SPF/domain issue | Verify domain ownership |
| Rate limited | Too many emails | Reduce sending frequency |
| Bounced emails | Invalid recipient | Clean email list |

---

## Implementation Checklist

- [ ] Create `company_email_settings` table
- [ ] Create `email_logs` table
- [ ] Implement EmailService class
- [ ] Add SMTP sending logic
- [ ] Add Microsoft 365 OAuth flow
- [ ] Add Google OAuth flow
- [ ] Add SendGrid integration
- [ ] Create admin settings UI
- [ ] Implement credential encryption
- [ ] Add email logging
- [ ] Add test email endpoint
- [ ] Add rate limiting
- [ ] Create fallback mechanism
- [ ] Add email analytics dashboard
