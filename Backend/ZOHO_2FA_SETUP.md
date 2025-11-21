# Zoho Mail with 2FA - App Password Setup

## ⚠️ IMPORTANT: If you have 2FA enabled

When Two-Factor Authentication (2FA) is enabled on your Zoho account, you **CANNOT** use your regular password for the contact form. You **MUST** use an **App Password**.

---

## Why App Passwords?

When 2FA is enabled:
- ✅ You log in to Zoho Mail with: **Email + Password + 2FA Code**
- ❌ Apps cannot use 2FA codes automatically
- ✅ Solution: Generate an **App Password** for the contact form

---

## Step-by-Step: Generate Zoho App Password

### Step 1: Log in to Zoho Mail

1. Go to https://mail.zoho.com
2. Log in with your email and password
3. Enter your 2FA code (from SMS or Authenticator app)

### Step 2: Access Security Settings

1. Click your **profile icon** (top right corner)
2. Click **My Account**
3. Click **Security** in the left sidebar

### Step 3: Generate App Password

1. Scroll down to find **"Application-Specific Passwords"** or **"App Passwords"**
2. Click **"Generate New Password"**
3. Enter a name: `Contact Form API` or `Website Contact Form`
4. Click **Generate**

### Step 4: Copy the Password

You'll see a password like: `abcd efgh ijkl mnop`

**IMPORTANT:**
- Copy this password immediately
- Save it securely (you won't see it again!)
- This is what you'll use in your `.env` file

### Step 5: Configure `.env`

Edit your `.env` file:

```env
# Zoho Mail Configuration
MAIL_SERVER=smtp.zoho.com.au
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Your Zoho email
MAIL_USERNAME=info@aussupersource.com.au

# USE APP PASSWORD HERE (not your regular password!)
MAIL_PASSWORD=abcdefghijklmnop

# Email settings
MAIL_DEFAULT_SENDER=info@aussupersource.com.au
ADMIN_EMAIL=info@aussupersource.com.au
SEND_CONFIRMATION_EMAIL=True
```

**Replace:**
- `info@aussupersource.com.au` with your actual Zoho email
- `abcdefghijklmnop` with the App Password you just generated

---

## Visual Guide

```
Regular Login (Web):
┌─────────────────────────────────────┐
│ Email: info@aussupersource.com.au   │
│ Password: YourRegularPassword       │
│ 2FA Code: 123456                    │
└─────────────────────────────────────┘
            ↓
    ✅ Logged In


App Login (Contact Form):
┌─────────────────────────────────────┐
│ MAIL_USERNAME: info@aussupersource │
│ MAIL_PASSWORD: abcdefghijklmnop     │ ← App Password
│ (No 2FA code needed)                │
└─────────────────────────────────────┘
            ↓
    ✅ Emails Sent
```

---

## Complete Configuration Example

### Your `.env` file should look like this:

```env
# Flask Configuration
FLASK_DEBUG=False
PORT=5000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173

# Email Configuration - ZOHO MAIL
MAIL_SERVER=smtp.zoho.com.au
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# Zoho Credentials (with App Password)
MAIL_USERNAME=info@aussupersource.com.au
MAIL_PASSWORD=abcd efgh ijkl mnop

# Email Settings
MAIL_DEFAULT_SENDER=info@aussupersource.com.au
ADMIN_EMAIL=info@aussupersource.com.au
SEND_CONFIRMATION_EMAIL=True
```

**Note:** The App Password might have spaces when generated. You can:
- Keep the spaces: `abcd efgh ijkl mnop`
- Remove the spaces: `abcdefghijklmnop`

Both work fine!

---

## Testing Your Configuration

### Method 1: Run Test Script

```bash
cd Backend
python test_email.py
```

This will:
- Check your configuration
- Try to send a test email
- Tell you if everything is working

### Method 2: Start the API and Test

```bash
# Start Flask server
python app.py

# Then submit the contact form on your website
```

---

## Troubleshooting

### Error: "Authentication Failed"

**Possible Causes:**
1. ❌ Using regular password instead of App Password
2. ❌ Copied App Password incorrectly (extra spaces, missing characters)
3. ❌ App Password was deleted or expired

**Solutions:**
1. ✅ Make sure you're using the App Password, not your regular password
2. ✅ Generate a new App Password and copy it carefully
3. ✅ Check Zoho Mail → Security → App Passwords to see if it's still active

### Error: "SMTP Authentication Error"

**Solution:**
Generate a new App Password and update `.env` file

### Email sends but you're not receiving it

**Check:**
1. Spam/Junk folder
2. Check if `ADMIN_EMAIL` is correct in `.env`
3. Log in to Zoho Mail and check Sent folder

---

## Managing App Passwords

### View All App Passwords

1. Zoho Mail → Profile → My Account
2. Security → Application-Specific Passwords
3. You'll see a list of all generated passwords with their names

### Revoke an App Password

1. Find the password in the list
2. Click **Revoke** or **Delete**
3. Generate a new one if needed

### Best Practices

1. ✅ Use descriptive names: "Contact Form API", "Website Email"
2. ✅ Generate separate passwords for different apps/services
3. ✅ Revoke old passwords you're not using
4. ✅ Keep App Passwords secure (treat like regular passwords)
5. ✅ Rotate App Passwords periodically (every 3-6 months)

---

## Quick Checklist

- [ ] 2FA is enabled on your Zoho account
- [ ] Generated App Password in Zoho Mail → Security
- [ ] Copied App Password correctly
- [ ] Updated `.env` file with App Password
- [ ] Set `MAIL_SERVER=smtp.zoho.com.au` (or your region)
- [ ] Set `MAIL_USERNAME` to your Zoho email
- [ ] Set `MAIL_PASSWORD` to the App Password (not regular password!)
- [ ] Ran `test_email.py` successfully
- [ ] Received test email in your inbox

---

## Need Help?

### If test email fails:

1. **Double-check `.env` file:**
   ```bash
   # Make sure .env is in the Backend folder
   cd Backend
   notepad .env
   ```

2. **Verify App Password:**
   - Log in to Zoho Mail
   - Go to Security → App Passwords
   - Check if your password is listed and active
   - If not, generate a new one

3. **Check SMTP Server:**
   - Australia: `smtp.zoho.com.au`
   - Europe: `smtp.zoho.eu`
   - India: `smtp.zoho.in`
   - Others: `smtp.zoho.com`

4. **Try different port:**
   ```env
   # Try SSL on port 465
   MAIL_PORT=465
   MAIL_USE_TLS=False
   MAIL_USE_SSL=True
   ```

5. **Restart Flask:**
   ```bash
   # Stop the server (Ctrl+C)
   # Start again
   python app.py
   ```

---

## Summary

### DO ✅
- Use App Password when 2FA is enabled
- Keep App Password secure
- Save App Password before closing the generation window
- Test configuration with `test_email.py`

### DON'T ❌
- Don't use your regular password in `.env`
- Don't share App Passwords
- Don't commit `.env` to git (it's in .gitignore)
- Don't forget to update `.env` after generating new App Password

---

**You're all set!** 🎉

Your Zoho Mail with 2FA is now configured for the contact form.

Run `python test_email.py` to verify!
