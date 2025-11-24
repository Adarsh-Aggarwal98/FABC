# Render Deployment Guide - FREE TIER

## 🎉 100% Free Deployment

This guide shows you how to deploy your application **completely FREE** using Render's free tier.

### What You Get for FREE:
✅ **Static Site** (Frontend) - 100GB bandwidth/month
✅ **Web Service** (Backend API) - 750 hours/month
✅ **Custom Domain** support
✅ **Automatic SSL** certificates
✅ **Automatic deploys** from Git

### Free Tier Limitations to Know:
⚠️ **Backend spins down after 15 minutes of inactivity**
   - First request after inactivity: 30-60 second delay (cold start)
   - Subsequent requests: Fast (normal speed)
   - **Impact**: First contact form submission after inactivity will be slow

⚠️ **750 hours/month limit** for backend
   - More than enough for a business website
   - Resets every month

✅ **Frontend has NO limitations** - always fast, never sleeps

---

## Architecture Overview
- **Frontend**: React Static Site (Vite build) - Always fast ⚡
- **Backend**: Python Flask API (Contact form email service) - Sleeps when inactive 😴

---

## Prerequisites

1. **Git Repository**: Push your code to GitHub/GitLab/Bitbucket
2. **Render Account**: Sign up at https://render.com
3. **Email Credentials**: Have your Zoho/Gmail SMTP credentials ready

---

## Step 1: Deploy Python Backend (Flask API)

### 1.1 Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +" → "Web Service"**
3. Connect your Git repository
4. Configure:
   - **Name**: `aussupersource-api`
   - **Region**: Choose closest to Australia (e.g., Singapore)
   - **Branch**: `main`
   - **Root Directory**: `FABC/Backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: ⭐ **FREE** ⭐ (select the free tier option)

### 1.2 Set Environment Variables

In the "Environment" section, add these variables:

```
# SMTP Configuration (Use your Zoho credentials)
MAIL_SERVER=smtp.zoho.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@aussupersource.com.au
MAIL_PASSWORD=your-app-specific-password

# Email Settings
MAIL_DEFAULT_SENDER=your-email@aussupersource.com.au
ADMIN_EMAIL=sam@aussupersource.com.au
SEND_CONFIRMATION_EMAIL=True

# Flask Settings
FLASK_DEBUG=False
PORT=10000
```

**Important**: Replace `your-email@aussupersource.com.au` and `your-app-specific-password` with actual credentials.

### 1.3 Deploy

Click **"Create Web Service"**. Render will:
- Install dependencies
- Start the Flask app
- Provide a URL like: `https://aussupersource-api.onrender.com`

**Save this URL** - you'll need it for the frontend!

---

## Step 2: Deploy React Frontend (Static Site)

### 2.1 Update Frontend API URL

Before deploying, update the API endpoint in your code:

**File**: `FABC/client/.env` (create if doesn't exist)

```
VITE_API_URL=https://aussupersource-api.onrender.com
```

Replace `https://aussupersource-api.onrender.com` with your actual backend URL from Step 1.3.

### 2.2 Build the Frontend Locally (Test)

```bash
cd FABC
npm install
npm run build
```

This creates a `dist/` folder with your production build.

### 2.3 Create Static Site on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +" → "Static Site"**
3. Connect your Git repository
4. Configure:
   - **Name**: `aussupersource-website`
   - **Branch**: `main`
   - **Root Directory**: `FABC`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 2.4 Add Environment Variable

In "Environment" section:

```
VITE_API_URL=https://aussupersource-api.onrender.com
```

(Use your actual backend URL)

### 2.5 Deploy

Click **"Create Static Site"**. Render will provide a URL like:
`https://aussupersource-website.onrender.com`

---

## Step 3: Test Your Deployment

### 3.1 Test Backend API

Visit: `https://aussupersource-api.onrender.com/api/health`

Expected response:
```json
{
  "status": "healthy",
  "service": "contact-form-api",
  "mail_configured": true
}
```

### 3.2 Test Frontend

1. Visit your frontend URL: `https://aussupersource-website.onrender.com`
2. Navigate to the Contact page
3. Fill out and submit the contact form
4. Check `sam@aussupersource.com.au` for the email

---

## Step 4: Add Custom Domain (Optional)

### For Frontend:
1. Go to your Static Site settings
2. Click "Custom Domains"
3. Add your domain (e.g., `www.aussupersource.com.au`)
4. Update DNS records as instructed by Render

### For Backend API (if needed):
1. Go to your Web Service settings
2. Click "Custom Domains"
3. Add API subdomain (e.g., `api.aussupersource.com.au`)

---

## Important Notes

### Free Tier Performance:
- **Static Site (Frontend)**: ⚡ Always fast, never sleeps
- **Backend API**: 😴 Sleeps after 15 minutes of inactivity
  - **First request after sleep**: 30-60 seconds delay
  - **All subsequent requests**: Normal speed
  - **Real-world impact**: If no one submits contact form for 15+ minutes, next submission will be slow

### Tips for Free Tier:
1. **Inform users**: Add a note like "Please wait up to 60 seconds for form submission"
2. **Consider uptime monitoring**: Use a free service like [UptimeRobot](https://uptimerobot.com) to ping your API every 5 minutes (keeps it awake)
3. **Accept the trade-off**: Free tier is perfect for small business websites with moderate traffic

### Want to Eliminate Cold Starts? Upgrade to Paid:
- Costs $7/month for backend service
- Backend stays awake 24/7
- Instant form submissions
- More resources

### Monitoring:
- Check logs in Render Dashboard
- Monitor email delivery
- Set up error notifications

---

## Troubleshooting

### Contact Form Not Working:
1. Check backend logs in Render Dashboard
2. Verify environment variables are set correctly
3. Ensure CORS is enabled (already configured in `app.py`)
4. Verify `VITE_API_URL` in frontend points to correct backend URL

### Emails Not Sending:
1. Check SMTP credentials in environment variables
2. Verify Zoho/Gmail app-specific password
3. Check backend logs for email errors
4. Test with: `https://your-backend.onrender.com/api/health`

### CORS Errors:
- Already configured in `Backend/app.py` to accept all origins
- If issues persist, check browser console for specific error

---

## Quick Deploy Checklist

- [ ] Code pushed to Git repository
- [ ] Backend deployed with correct environment variables
- [ ] Backend health endpoint working
- [ ] Frontend `.env` file has correct `VITE_API_URL`
- [ ] Frontend deployed successfully
- [ ] Contact form tested and working
- [ ] Emails received at `sam@aussupersource.com.au`
- [ ] Custom domain configured (optional)

---

## Support

For Render-specific issues: https://render.com/docs
For code issues: Check application logs in Render Dashboard
