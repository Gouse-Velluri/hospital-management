# Render Environment Variables Setup Guide

## 🔧 Required Environment Variables for Render

### Step-by-Step Setup:

1. **Go to Render Dashboard:** https://dashboard.render.com/
2. **Select your Web Service:** `hospital-management-hrkp`
3. **Click Settings** (top right)
4. **Scroll to "Environment"**
5. **Add these variables:**

---

## Environment Variables to Set:

### 1. **Django Security**
```
DJANGO_SECRET_KEY=django-insecure-gn4)40e3k6@@^s*zk9@!t9pmbjum%v_s*lrq4+aw=v&p!#@*o%
```
> ⚠️ In production, use a strong random key instead!

### 2. **Debug Mode (IMPORTANT)**
```
DEBUG=False
```
> Production should always have DEBUG=False

### 3. **Database (PostgreSQL)**
```
DATABASE_URL=postgresql://user:password@hostname:5432/dbname
```
> Get this from your PostgreSQL database in Render Dashboard

### 4. **Allowed Hosts**
```
ALLOWED_HOSTS=hospital-management-hrkp.onrender.com
```
> Use your actual Render domain

### 5. **CSRF Trusted Origins**
```
CSRF_TRUSTED_ORIGINS=https://hospital-management-hrkp.onrender.com
```
> Must start with `https://`

### 6. **Email Configuration (Optional)**
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 📋 Complete Copy-Paste List:

```
DJANGO_SECRET_KEY=django-insecure-gn4)40e3k6@@^s*zk9@!t9pmbjum%v_s*lrq4+aw=v&p!#@*o%
DEBUG=False
DATABASE_URL=postgresql://user:password@hostname:5432/dbname
ALLOWED_HOSTS=hospital-management-hrkp.onrender.com
CSRF_TRUSTED_ORIGINS=https://hospital-management-hrkp.onrender.com
```

---

## 🎯 Steps in Render Dashboard:

1. Open: https://dashboard.render.com/
2. Click your service: `hospital-management-hrkp`
3. Click "Settings"
4. Scroll down to "Environment"
5. Click "Add Environment Variable"
6. Enter each key and value from above
7. Click "Save Changes"
8. Click "Manual Deploy" to redeploy

---

## ✅ What Each Variable Does:

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Encrypts sessions and tokens |
| `DEBUG=False` | Disables debug mode (required for production) |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Specifies which domains can access your app |
| `CSRF_TRUSTED_ORIGINS` | Allows form submissions from your domain |
| `EMAIL_*` | Configures email sending (forgot password, etc.) |

---

## ⚠️ Important Notes:

- **Never commit secrets to GitHub!** Use environment variables instead.
- If using Gmail, use an **App Password**, not your regular password.
- `DEBUG=False` in production hides sensitive error details.
- Changes take effect after redeploy.

---

## 🔗 Get PostgreSQL Connection String:

### Option 1: Create FREE PostgreSQL on Render

1. **Go to Render Dashboard:** https://dashboard.render.com/
2. **Click "New +"** button → Select **"PostgreSQL"**
3. **Configure Database:**
   - **Name:** `hospital-management-db` (or any name)
   - **Database:** `hospital_management`
   - **User:** `postgres` (default)
   - **Region:** North America (or same as your Web Service)
   - **Plan:** Free ($0/month)
4. **Click "Create Database"**
5. **Wait 2-3 minutes** for creation
6. **Copy the Connection String:**
   - Go to your PostgreSQL instance
   - Find **"External Database URL"** section
   - Click copy icon next to the URL
   - It will look like:
   ```
   postgresql://user_abc123:password123@dpg-xyz123.oregon-postgres.render.com:5432/hospital_management
   ```

7. **Add to Environment Variables:**
   - Go to Web Service settings
   - Add: `DATABASE_URL=` + (paste the URL you copied)

---

### Option 2: Use External PostgreSQL (AWS RDS, DigitalOcean, etc.)

If you have an external database:
```
DATABASE_URL=postgresql://username:password@host:port/dbname
```

Example:
```
DATABASE_URL=postgresql://admin:mypassword123@db.example.com:5432/hospital_management
```

---

### Step-by-Step Screenshot Guide:

**Step 1: Click "New +" in Render**
```
Dashboard → New + → PostgreSQL
```

**Step 2: Fill Form**
```
Name: hospital-management-db
Database: hospital_management
User: postgres
Plan: Free
```

**Step 3: Copy URL**
```
PostgreSQL instance → External Database URL → Copy
```

**Step 4: Add to Web Service**
```
Web Service Settings → Environment → Add Variable
Key: DATABASE_URL
Value: postgresql://...
```

**Step 5: Redeploy**
```
Web Service → Manual Deploy
```

If using Render's PostgreSQL:

---

## ✨ After Setting Variables:

1. Save changes
2. Click "Manual Deploy"
3. Wait 3-5 minutes
4. Test: https://hospital-management-hrkp.onrender.com/patient/login/

If you still get **400 error**, check Render logs for more details!
