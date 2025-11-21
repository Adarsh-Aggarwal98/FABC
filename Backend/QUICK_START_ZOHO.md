# Quick Start - Zoho Mail Setup (5 Minutes)

## Step 1: Get Your Zoho App Password (2 min)

### If you DON'T have 2FA enabled:
- Just use your regular Zoho password
- Skip to Step 2

### If you HAVE 2FA enabled:
1. Go to https://mail.zoho.com
2. Login → Profile Icon → My Account → Security
3. Scroll to **"Application-Specific Passwords"**
4. Click **"Generate New Password"**
5. Name it: `Contact Form`
6. **Copy the password** (looks like: `abcd efgh ijkl mnop`)

## Step 2: Configure .env file (2 min)

```bash
cd Backend
copy .env.example .env
notepad .env
```

**Edit and save:**

```env
# Email Configuration
MAIL_SERVER=smtp.zoho.com.au
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Zoho credentials - Sending account
MAIL_USERNAME=addi@aussupersource.com.au
MAIL_PASSWORD=your-app-password-here

# Email settings
MAIL_DEFAULT_SENDER=addi@aussupersource.com.au
ADMIN_EMAIL=sam@aussupersource.com.au
SEND_CONFIRMATION_EMAIL=True
```

**Configuration explained:**
- `MAIL_USERNAME` - The Zoho account to send emails FROM
- `MAIL_PASSWORD` - App Password (if 2FA enabled) or regular password
- `ADMIN_EMAIL` - Where contact form submissions are sent TO

## Step 3: Test Configuration (1 min)

```bash
python test_email.py
```

**Expected output:**
```
✅ SUCCESS!
Test email sent successfully to: info@aussupersource.com.au
```

**Check your email inbox!** (and spam folder)

## Step 4: Run the Server (30 sec)

```bash
run.bat
```

Or:

```bash
python app.py
```

**Server runs at:** http://localhost:5000

## Done! 🎉

Test your contact form on the website.

---

## Troubleshooting

### "Authentication Failed"
→ You have 2FA enabled. Use App Password instead of regular password

### "Connection Refused"
→ Try port 465: Set `MAIL_PORT=465`, `MAIL_USE_SSL=True`, `MAIL_USE_TLS=False`

### "SMTP Server Not Found"
→ Australia: Use `smtp.zoho.com.au`
→ Others: Check your region in ZOHO_MAIL_SETUP.md

---

## Quick Links

- **Full Zoho Setup**: `ZOHO_MAIL_SETUP.md`
- **2FA Guide**: `ZOHO_2FA_SETUP.md`
- **Full Documentation**: `README.md`

---

**Need help?** Check the detailed guides above.
