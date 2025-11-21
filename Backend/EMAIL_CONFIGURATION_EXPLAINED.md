# Email Configuration Explained

## Overview

The contact form email system is configured with the following setup:

```
┌──────────────────────────────────────────────────┐
│                Contact Form Flow                 │
└──────────────────────────────────────────────────┘

User fills form → Website shows info@aussupersource.com.au
                           ↓
           Email sent FROM: addi@aussupersource.com.au
                           ↓
            Email sent TO: sam@aussupersource.com.au
                           ↓
              Sam receives the contact form submission
```

## Email Addresses Used

### 1. **Displayed to Users (UI Only)**
- **Email:** `info@aussupersource.com.au`
- **Location:** Contact page, footer, team bios
- **Purpose:** Public-facing contact email shown to visitors
- **Note:** This is ONLY for display - emails are NOT sent from or to this address

### 2. **Sending Account (FROM)**
- **Email:** `addi@aussupersource.com.au`
- **Configuration:** `MAIL_USERNAME` and `MAIL_DEFAULT_SENDER`
- **Purpose:** The Zoho account that actually sends the emails
- **Authentication:** Requires Zoho password or App Password
- **Visible in:** Email "From" field and email headers

### 3. **Receiving Account (TO)**
- **Email:** `sam@aussupersource.com.au`
- **Configuration:** `ADMIN_EMAIL`
- **Purpose:** Receives all contact form submissions
- **Location:** Inbox of this email will receive notifications

## Configuration in .env

```env
# Zoho Credentials - The account that SENDS emails
MAIL_USERNAME=addi@aussupersource.com.au
MAIL_PASSWORD=app-password-for-addi-account

# Where emails come FROM
MAIL_DEFAULT_SENDER=addi@aussupersource.com.au

# Where contact submissions are sent TO
ADMIN_EMAIL=sam@aussupersource.com.au
```

## Why This Setup?

### Advantages:
1. ✅ **Separation of concerns**: Display email (info@) vs operational email (addi@)
2. ✅ **Direct routing**: Submissions go directly to Sam
3. ✅ **Professional appearance**: Users see the general info@ address
4. ✅ **Centralized sending**: All automated emails come from one account (addi@)
5. ✅ **Easy tracking**: Sam can track all contact form submissions in one inbox

## Email Flow Examples

### Example 1: User submits contact form

**What the user sees:**
- Contact page shows: info@aussupersource.com.au
- User fills: Name, Email, Message

**What happens behind the scenes:**
1. Frontend sends data to Flask API
2. Flask API creates email
3. Email sent FROM: addi@aussupersource.com.au
4. Email sent TO: sam@aussupersource.com.au
5. Reply-To field: user's email address (so Sam can reply directly)

**Sam receives:**
```
From: addi@aussupersource.com.au
To: sam@aussupersource.com.au
Reply-To: user@example.com
Subject: [Contact Form] User's Subject

Contact Form Submission
Name: John Doe
Email: user@example.com
...
```

### Example 2: User confirmation email

**What happens:**
1. After successful submission, user receives confirmation
2. Email sent FROM: addi@aussupersource.com.au
3. Email sent TO: user@example.com (the person who filled the form)
4. Contains thank you message and copy of their inquiry

**User receives:**
```
From: addi@aussupersource.com.au
To: user@example.com
Subject: Thank you for contacting Australian Super Source

Dear John,
Thank you for reaching out...
```

## Setup Requirements

### For addi@aussupersource.com.au:

1. **Must have Zoho Mail account**
2. **If 2FA is enabled:**
   - Generate App Password in Zoho Mail
   - Use App Password in `.env`
3. **SMTP access must be enabled** (usually enabled by default)

### For sam@aussupersource.com.au:

1. **Must have a valid email inbox** (Zoho, Gmail, etc.)
2. **Can access emails** to receive contact form submissions
3. **No special configuration needed** - just receives emails

### For info@aussupersource.com.au:

1. **Can be ANY email or just for display**
2. **No configuration needed** in the Flask app
3. **Optional:** Can forward to sam@ or addi@ if you want it to be functional

## Testing the Configuration

### Step 1: Verify .env settings

```bash
cd Backend
notepad .env
```

Check:
- ✅ `MAIL_USERNAME=addi@aussupersource.com.au`
- ✅ `MAIL_DEFAULT_SENDER=addi@aussupersource.com.au`
- ✅ `ADMIN_EMAIL=sam@aussupersource.com.au`
- ✅ `MAIL_PASSWORD` is set (App Password or regular password)

### Step 2: Run test script

```bash
python test_email.py
```

Expected result:
- ✅ "Email sent successfully"
- ✅ Sam receives test email in sam@aussupersource.com.au inbox

### Step 3: Test via contact form

1. Start backend: `python app.py`
2. Start frontend: `cd ../client && npm run dev`
3. Fill out contact form
4. Check Sam's inbox (sam@aussupersource.com.au)

## Troubleshooting

### "Authentication failed"

**Problem:** Can't send emails

**Solution:**
- Verify addi@aussupersource.com.au credentials
- If 2FA enabled on addi@ account, use App Password
- Check SMTP settings (smtp.zoho.com.au, port 587)

### "Email not received by Sam"

**Problem:** Sam doesn't receive contact form submissions

**Solution:**
- Check Sam's spam/junk folder
- Verify `ADMIN_EMAIL=sam@aussupersource.com.au` in .env
- Check Flask console for errors
- Verify sam@aussupersource.com.au is a valid, active email

### "Want to change receiving email"

**Solution:**
Simply update `ADMIN_EMAIL` in .env:

```env
ADMIN_EMAIL=new-recipient@aussupersource.com.au
```

Restart Flask server: `python app.py`

### "Want to change sending email"

**Solution:**
Update both `MAIL_USERNAME` and `MAIL_DEFAULT_SENDER`:

```env
MAIL_USERNAME=new-sender@aussupersource.com.au
MAIL_PASSWORD=new-password-or-app-password
MAIL_DEFAULT_SENDER=new-sender@aussupersource.com.au
```

Restart Flask server: `python app.py`

## Advanced Configuration

### Send to multiple recipients

Edit `Backend/app.py`, line with `ADMIN_EMAIL`:

```python
# Find this line:
recipients=[app.config['ADMIN_EMAIL']],

# Change to:
recipients=[
    'sam@aussupersource.com.au',
    'info@aussupersource.com.au',
    'another@aussupersource.com.au'
],
```

### Change displayed email in UI

Edit `FABC/client/src/components/ContactSection.tsx`:

```tsx
// Find all instances of:
info@aussupersource.com.au

// Replace with your desired display email
```

### Disable user confirmation emails

In `.env`:

```env
SEND_CONFIRMATION_EMAIL=False
```

## Security Notes

1. ✅ Never share addi@ password or App Password
2. ✅ Never commit `.env` to version control (it's in .gitignore)
3. ✅ Use App Passwords instead of main passwords when 2FA is enabled
4. ✅ Regularly check Sam's inbox for spam
5. ✅ Monitor addi@ account for suspicious activity

## Summary Checklist

- [ ] addi@aussupersource.com.au - Zoho account set up
- [ ] sam@aussupersource.com.au - Valid inbox ready to receive
- [ ] info@aussupersource.com.au - Displayed in website UI
- [ ] `.env` configured with addi@ credentials
- [ ] `ADMIN_EMAIL=sam@aussupersource.com.au` in .env
- [ ] Tested with `test_email.py`
- [ ] Sam received test email successfully
- [ ] Contact form tested end-to-end

---

**You're all set!** 🎉

Emails will be sent FROM addi@, received by Sam, while showing info@ to users.
