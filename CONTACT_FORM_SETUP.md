# Contact Form Integration Guide

## Overview

The contact form integration consists of two parts:
1. **Backend (Flask API)** - Handles form submissions and sends emails
2. **Frontend (React)** - User interface for the contact form

## How It Works

```
User fills form → Frontend validates → Sends to Flask API → API sends emails → Returns response → Frontend shows success/error
```

### Flow Diagram

```
┌─────────────────┐
│   User enters   │
│   form data     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  React form     │
│  validation     │
│  (Zod schema)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API call to    │
│  Flask backend  │
│  POST /api/     │
│  contact        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask API      │
│  validates &    │
│  processes      │
└────────┬────────┘
         │
         ├────────────────────┐
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  Email to admin │  │  Confirmation   │
│  (HTML format)  │  │  email to user  │
└─────────────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Response sent  │
│  back to React  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Show success   │
│  or error toast │
└─────────────────┘
```

## Setup Instructions

### Part 1: Backend Setup (Flask API)

#### 1. Navigate to Backend folder

```bash
cd "C:\Users\aggar\Desktop\smsf website\aussupersource-website\FABC\Backend"
```

#### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

Or create a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure environment variables

Create a `.env` file from the example:

```bash
copy .env.example .env
```

Edit `.env` with your email settings:

```env
# Flask Configuration
FLASK_DEBUG=False
PORT=5000

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True

# Your email credentials
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Admin email (receives contact form submissions)
ADMIN_EMAIL=info@aussupersource.com.au
```

**For Gmail:**
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password: https://support.google.com/accounts/answer/185833
4. Use the App Password (16 characters) in `MAIL_PASSWORD`

#### 4. Run the Flask server

**Option A: Using the batch file (easiest)**
```bash
run.bat
```

**Option B: Manually**
```bash
python app.py
```

The server will start at `http://localhost:5000`

### Part 2: Frontend Setup (React)

#### 1. Navigate to client folder

```bash
cd "C:\Users\aggar\Desktop\smsf website\aussupersource-website\FABC\client"
```

#### 2. Create environment file

```bash
copy .env.example .env.local
```

Edit `.env.local`:

```env
VITE_API_URL=http://localhost:5000
```

#### 3. Install dependencies (if not already done)

```bash
npm install
```

#### 4. Run the frontend

```bash
npm run dev
```

The frontend will start at `http://localhost:5173`

### Part 3: Test the Integration

1. **Start both servers:**
   - Flask backend at `http://localhost:5000`
   - React frontend at `http://localhost:5173`

2. **Check backend health:**
   Visit `http://localhost:5000/api/health` - should show:
   ```json
   {
     "status": "healthy",
     "service": "contact-form-api",
     "mail_configured": true
   }
   ```

3. **Test the form:**
   - Go to the Contact page on the frontend
   - Fill out the form
   - Click "Send Message"
   - You should see a success toast notification
   - Admin should receive an email
   - User should receive a confirmation email

## API Documentation

### Endpoint: Submit Contact Form

**URL:** `POST /api/contact`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "0412345678",
  "state": "NSW",
  "subject": "SMSF Inquiry",
  "message": "I would like to learn more about SMSF services"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Thank you for your message. We will get back to you soon!"
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": ["Name is required", "Email is required"]
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Failed to send email. Please try again later."
}
```

## Email Templates

### Admin Email

The admin receives a professional HTML email with:
- Contact person's details (name, email, phone, state)
- Subject line
- Full message content
- Timestamp
- Reply-to set to the contact's email

### User Confirmation Email

The user receives:
- Thank you message
- Confirmation that message was received
- Copy of their message
- Company branding

## Files Created

### Backend Files
- `Backend/app.py` - Main Flask application
- `Backend/requirements.txt` - Python dependencies
- `Backend/.env.example` - Environment variable template
- `Backend/.gitignore` - Git ignore rules
- `Backend/README.md` - Backend documentation
- `Backend/run.bat` - Windows startup script
- `Backend/frontend-integration-example.js` - Integration examples

### Frontend Files
- `client/src/lib/api.ts` - API utility functions
- `client/.env.example` - Frontend environment variables
- `client/src/components/ContactSection.tsx` - Updated contact form component

## Troubleshooting

### Email not sending

**Problem:** Emails are not being sent

**Solutions:**
1. Check `.env` file has correct email credentials
2. For Gmail, use App Password, not regular password
3. Check Flask console for error messages
4. Verify SMTP settings (server, port, TLS)
5. Check if email provider allows SMTP access

### CORS errors

**Problem:** Frontend can't connect to backend

**Solutions:**
1. Verify backend is running on port 5000
2. Check `FRONTEND_URL` in backend `.env` matches your frontend URL
3. Make sure Flask-CORS is installed
4. Check browser console for specific error

### API connection refused

**Problem:** "Failed to fetch" or "Connection refused"

**Solutions:**
1. Make sure Flask server is running
2. Check the API URL in frontend `.env.local`
3. Verify port 5000 is not blocked by firewall
4. Try accessing `http://localhost:5000/api/health` directly

### Form validation errors

**Problem:** Form shows validation errors

**Solutions:**
1. All required fields must be filled (name, email, state, subject, message)
2. Email must be valid format
3. Message must be at least 10 characters

## Production Deployment

### Backend Deployment

**Recommended platforms:**
- Render (https://render.com)
- Railway (https://railway.app)
- Heroku
- DigitalOcean App Platform

**Steps:**
1. Push code to GitHub
2. Connect repository to platform
3. Set environment variables
4. Deploy

**Environment variables to set:**
```
FLASK_DEBUG=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
ADMIN_EMAIL=info@aussupersource.com.au
FRONTEND_URL=https://your-domain.com
```

### Frontend Deployment

Update `.env.production`:
```
VITE_API_URL=https://your-backend-url.com
```

Then deploy to Vercel, Netlify, or your hosting platform.

## Security Notes

- Never commit `.env` files to git
- Use App Passwords for email
- Enable HTTPS in production
- Add rate limiting for production
- Validate all inputs on backend
- Keep dependencies updated

## Support

For issues:
1. Check Flask console logs
2. Check browser console
3. Review this documentation
4. Contact development team

## Next Steps

### Optional Enhancements

1. **Add rate limiting** - Prevent spam submissions
2. **Add reCAPTCHA** - Prevent bot submissions
3. **Database logging** - Store submissions in database
4. **Email templates** - Customize email designs
5. **File attachments** - Allow users to upload files
6. **Auto-responder** - Send different responses based on inquiry type
7. **Slack/Discord notifications** - Get notified on messaging platforms
8. **Analytics** - Track form submissions

### Code Examples

All implementation examples are available in:
- `Backend/frontend-integration-example.js`
- `Backend/README.md`

## Quick Start Script

Save this as `start-all.bat` in the FABC folder:

```batch
@echo off
echo Starting Australian Super Source website...

start cmd /k "cd Backend && run.bat"
timeout /t 3
start cmd /k "cd client && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
```

Run it to start both servers at once!
