# Quick Start - Deploy to Render FREE TIER

## 🚀 Deploy in 10 Minutes (Free)

### Step 1: Push to GitHub (5 minutes)

If you haven't already:

```bash
cd "C:\Users\aggar\Desktop\smsf website\aussupersource-website"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/aussupersource-website.git
git push -u origin main
```

---

### Step 2: Deploy Backend to Render (3 minutes)

1. Go to https://render.com and sign up/login
2. Click **"New +" → "Web Service"**
3. Connect your GitHub repository
4. Fill in:
   - **Name**: `aussupersource-api`
   - **Root Directory**: `FABC/Backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: **FREE**

5. Add Environment Variables:
   ```
   MAIL_SERVER=smtp.zoho.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-zoho-email@aussupersource.com.au
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-zoho-email@aussupersource.com.au
   ADMIN_EMAIL=sam@aussupersource.com.au
   ```

6. Click **"Create Web Service"**
7. **Copy your backend URL**: `https://aussupersource-api.onrender.com`

---

### Step 3: Update Frontend with Backend URL (1 minute)

Create file `FABC/client/.env`:

```
VITE_API_URL=https://aussupersource-api.onrender.com
```

Replace with your actual backend URL from Step 2.

**Commit and push this change:**

```bash
git add FABC/client/.env
git commit -m "Add production API URL"
git push
```

---

### Step 4: Deploy Frontend to Render (1 minute)

1. In Render dashboard, click **"New +" → "Static Site"**
2. Connect same GitHub repository
3. Fill in:
   - **Name**: `aussupersource-website`
   - **Root Directory**: `FABC`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. Add Environment Variable:
   ```
   VITE_API_URL=https://aussupersource-api.onrender.com
   ```

5. Click **"Create Static Site"**

---

### Step 5: Test (1 minute)

1. Visit your site: `https://aussupersource-website.onrender.com`
2. Go to Contact page
3. Submit a test form
4. Check email at `sam@aussupersource.com.au`

**Note**: First submission may take 30-60 seconds if backend was sleeping.

---

## ✅ You're Done!

Your website is now live on:
- **Frontend**: `https://aussupersource-website.onrender.com`
- **Backend**: `https://aussupersource-api.onrender.com`

### Next Steps (Optional):

1. **Add Custom Domain**:
   - Go to Static Site settings → Custom Domains
   - Add `www.aussupersource.com.au`

2. **Keep Backend Awake** (free service):
   - Sign up at https://uptimerobot.com
   - Create monitor for `https://aussupersource-api.onrender.com/api/health`
   - Ping every 5 minutes
   - Prevents cold starts

3. **Monitor Your Site**:
   - Check Render Dashboard for logs
   - Monitor email delivery

---

## 💡 Free Tier Reminder

- ✅ Frontend: Always fast
- ⚠️ Backend: Sleeps after 15 min inactivity
- 💰 Upgrade to $7/month to eliminate sleep mode

---

## Need Help?

See full guide: `RENDER_DEPLOYMENT.md`
