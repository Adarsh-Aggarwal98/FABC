# Zoho Mail Setup Guide for Contact Form

This guide will help you configure Zoho Mail for the contact form backend.

## Quick Setup (Simple Method)

### Step 1: Edit your `.env` file

Create `.env` from the example:
```bash
copy .env.example .env
```

Edit `.env` and configure:

```env
# Email Configuration
MAIL_SERVER=smtp.zoho.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Your Zoho Mail Credentials
MAIL_USERNAME=info@aussupersource.com.au
MAIL_PASSWORD=your-zoho-password

# Email Settings
MAIL_DEFAULT_SENDER=info@aussupersource.com.au
ADMIN_EMAIL=info@aussupersource.com.au
SEND_CONFIRMATION_EMAIL=True
```

**Replace:**
- `info@aussupersource.com.au` - with your actual Zoho email
- `your-zoho-password` - with your actual Zoho password

### Step 2: Test the configuration

Run the Flask app:
```bash
python app.py
```

Test by submitting the contact form!

---

## Secure Setup (Recommended - Using App Password)

For better security, use Zoho App Passwords instead of your main password.

### Step 1: Enable Two-Factor Authentication (2FA)

1. Go to Zoho Mail: https://mail.zoho.com
2. Click on your profile icon (top right) → **My Account**
3. Go to **Security** section
4. Under **Two-Factor Authentication**, click **Enable**
5. Follow the setup wizard (use SMS or Authenticator app)
6. Complete the 2FA setup

### Step 2: Generate App Password

1. Go to **My Account** → **Security**
2. Scroll down to **App Passwords** or **Application-Specific Passwords**
3. Click **Generate New Password**
4. Give it a name like "Contact Form API"
5. Copy the generated password (it will look like: `abcd efgh ijkl mnop`)
6. Save this password securely

### Step 3: Configure `.env` with App Password

```env
# Email Configuration
MAIL_SERVER=smtp.zoho.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Use App Password for better security
MAIL_USERNAME=info@aussupersource.com.au
MAIL_PASSWORD=abcdefghijklmnop

# Email Settings
MAIL_DEFAULT_SENDER=info@aussupersource.com.au
ADMIN_EMAIL=info@aussupersource.com.au
SEND_CONFIRMATION_EMAIL=True
```

---

## Zoho Mail SMTP Settings Reference

| Setting | Value |
|---------|-------|
| SMTP Server | `smtp.zoho.com` |
| Port (TLS) | `587` |
| Port (SSL) | `465` |
| Authentication | Required |
| TLS/SSL | TLS on port 587 or SSL on port 465 |

### For TLS (Recommended):
```env
MAIL_SERVER=smtp.zoho.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

### For SSL (Alternative):
```env
MAIL_SERVER=smtp.zoho.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
```

---

## Different Zoho Data Centers

Zoho has different SMTP servers based on your region:

| Region | SMTP Server |
|--------|-------------|
| Global/US | `smtp.zoho.com` |
| Europe | `smtp.zoho.eu` |
| India | `smtp.zoho.in` |
| Australia | `smtp.zoho.com.au` |
| China | `smtp.zoho.com.cn` |
| Japan | `smtp.zoho.jp` |

**To check your data center:**
1. Log in to Zoho Mail
2. Look at the URL: `mail.zoho.com`, `mail.zoho.eu`, `mail.zoho.in`, etc.
3. Use the corresponding SMTP server

**Example for Australia:**
```env
MAIL_SERVER=smtp.zoho.com.au
```

---

## Testing the Configuration

### Method 1: Using the Flask App

1. Start the Flask server:
   ```bash
   cd Backend
   python app.py
   ```

2. Visit your frontend contact form and submit a test message

3. Check the Flask console for errors

4. Check your email inbox for:
   - Admin email (sent to ADMIN_EMAIL)
   - User confirmation email

### Method 2: Using Python Script

Create a test file `test_email.py` in the Backend folder:

```python
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            subject="Test Email from Contact Form",
            recipients=[os.getenv('ADMIN_EMAIL')],
            body="This is a test email. If you receive this, your Zoho Mail configuration is working!"
        )
        mail.send(msg)
        print("✅ Email sent successfully!")
        print(f"Sent to: {os.getenv('ADMIN_EMAIL')}")
    except Exception as e:
        print("❌ Failed to send email")
        print(f"Error: {str(e)}")
```

Run the test:
```bash
python test_email.py
```

---

## Troubleshooting

### Error: "Authentication failed"

**Causes:**
1. Wrong email or password
2. Using main password when 2FA is enabled (need App Password)
3. Wrong SMTP server for your region

**Solutions:**
1. Double-check your email and password in `.env`
2. If you have 2FA enabled, generate and use an App Password
3. Verify you're using the correct SMTP server for your region
4. Try logging in to Zoho Mail with the same credentials

### Error: "Connection refused" or "Connection timeout"

**Causes:**
1. Wrong port number
2. Firewall blocking outgoing SMTP
3. Wrong SMTP server

**Solutions:**
1. Try port 465 with SSL instead of 587 with TLS
2. Check firewall settings
3. Verify SMTP server matches your Zoho data center

### Error: "SMTP server requires authentication"

**Solution:**
Make sure `MAIL_USERNAME` and `MAIL_PASSWORD` are set correctly in `.env`

### Error: "Sender address rejected"

**Causes:**
1. `MAIL_DEFAULT_SENDER` doesn't match `MAIL_USERNAME`
2. Email address not verified in Zoho

**Solutions:**
1. Set `MAIL_DEFAULT_SENDER` to the same email as `MAIL_USERNAME`
2. Verify your email address in Zoho Mail settings

### Email sends but doesn't arrive

**Check:**
1. Spam/Junk folder
2. Zoho Mail sent folder to confirm it was sent
3. Email address is correct
4. Check Flask console for any errors

---

## Configuration Examples

### Example 1: Using info@aussupersource.com.au

```env
MAIL_SERVER=smtp.zoho.com.au
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=info@aussupersource.com.au
MAIL_PASSWORD=your-password-here
MAIL_DEFAULT_SENDER=info@aussupersource.com.au
ADMIN_EMAIL=info@aussupersource.com.au
```

### Example 2: Using different sender and admin emails

```env
MAIL_SERVER=smtp.zoho.com.au
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=noreply@aussupersource.com.au
MAIL_PASSWORD=your-password-here
MAIL_DEFAULT_SENDER=noreply@aussupersource.com.au
ADMIN_EMAIL=info@aussupersource.com.au
```

### Example 3: Using SSL instead of TLS

```env
MAIL_SERVER=smtp.zoho.com.au
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=info@aussupersource.com.au
MAIL_PASSWORD=your-password-here
MAIL_DEFAULT_SENDER=info@aussupersource.com.au
ADMIN_EMAIL=info@aussupersource.com.au
```

---

## Security Best Practices

1. **Use App Passwords** instead of your main password
2. **Never commit `.env`** to version control (already in `.gitignore`)
3. **Enable 2FA** on your Zoho account
4. **Use strong passwords** for your Zoho account
5. **Regularly rotate** App Passwords
6. **Monitor** Zoho's sent folder for unusual activity
7. **Use environment variables** for all sensitive data

---

## Zoho Mail Limits

Be aware of Zoho's sending limits:

| Plan | Daily Limit |
|------|-------------|
| Free | 500 emails/day |
| Mail Lite | 500 emails/day |
| Mail Premium | 1000 emails/day |
| Workplace | 2000 emails/day |

For high-volume contact forms, consider:
- Using a dedicated email service (SendGrid, Mailgun, etc.)
- Implementing rate limiting
- Setting up multiple sending accounts

---

## Additional Resources

- **Zoho Mail Help**: https://www.zoho.com/mail/help/
- **SMTP Configuration**: https://www.zoho.com/mail/help/zoho-smtp.html
- **App Passwords**: https://www.zoho.com/mail/help/adminconsole/app-passwords.html
- **Zoho Mail Admin Console**: https://mailadmin.zoho.com/

---

## Need Help?

If you're still having issues:

1. Check the Flask console for detailed error messages
2. Test your credentials by logging into Zoho Mail directly
3. Review the error messages carefully
4. Make sure your `.env` file is in the `Backend` folder
5. Restart the Flask server after changing `.env`

---

## Quick Checklist

- [ ] Created `.env` file from `.env.example`
- [ ] Set `MAIL_SERVER=smtp.zoho.com.au` (or your region)
- [ ] Set `MAIL_PORT=587`
- [ ] Set `MAIL_USE_TLS=True`
- [ ] Set your Zoho email in `MAIL_USERNAME`
- [ ] Set your password/app password in `MAIL_PASSWORD`
- [ ] Set `MAIL_DEFAULT_SENDER` to same as `MAIL_USERNAME`
- [ ] Set `ADMIN_EMAIL` to receive contact forms
- [ ] Tested with `test_email.py` or the contact form
- [ ] Checked spam folder for test emails
- [ ] Confirmed emails are being received

---

**You're all set!** 🎉

Your contact form should now be sending emails through Zoho Mail.
