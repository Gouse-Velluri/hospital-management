# Hospital Management System - Deployment Guide

## 📦 GitHub Repository
✅ **URL**: https://github.com/Gouse-Velluri/hospital-management
✅ **Status**: All code pushed and ready for deployment

---

## 🚀 Deployment Options

### Option 1: Deploy to Render (Recommended - Free)

#### Step 1: Connect GitHub to Render
1. Visit https://render.com
2. Sign up or log in with GitHub
3. Click **"New +"** → Select **"Web Service"**
4. Authorize Render to access your GitHub repositories
5. Select: `Gouse-Velluri/hospital-management`

#### Step 2: Configure Web Service
| Setting | Value |
|---------|-------|
| **Name** | hospital-management |
| **Runtime** | Python 3.11 |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn hospital_management.wsgi` |
| **Region** | North America (or your preference) |
| **Plan** | Free |

#### Step 3: Environment Variables
Add these in Render dashboard (Settings → Environment):
```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.onrender.com
DATABASE_URL=postgresql://...  (if using external DB)
```

#### Step 4: Deploy
1. Click **"Create Web Service"**
2. Render will automatically:
   - Build the project (run `build.sh`)
   - Collect static files
   - Run migrations
   - Deploy to production

**Expected Deploy Time**: 3-5 minutes

---

### Option 2: Deploy to Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Deployment Steps
```bash
# Login to Heroku
heroku login

# Create new app
heroku create hospital-management

# Set environment variables
heroku config:set DJANGO_SECRET_KEY=your-secret-key --app hospital-management
heroku config:set DEBUG=False --app hospital-management
heroku config:set ALLOWED_HOSTS=hospital-management.herokuapp.com --app hospital-management

# Deploy
git push heroku main

# View logs
heroku logs --tail --app hospital-management
```

---

### Option 3: Deploy to AWS/DigitalOcean (Self-Hosted)

#### Prerequisites
- Ubuntu 20.04+ server
- SSH access
- Domain name (optional)

#### Quick Setup Script
```bash
#!/bin/bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib

# Clone repository
cd /var/www
sudo git clone https://github.com/Gouse-Velluri/hospital-management.git
cd hospital-management

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Set up database (PostgreSQL)
sudo -u postgres createdb hospital_management
sudo -u postgres createuser hospital_user --createdb
sudo -u postgres psql -c "ALTER USER hospital_user WITH PASSWORD 'secure-password';"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Configure Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 hospital_management.wsgi

# Configure Nginx (create /etc/nginx/sites-available/hospital)
# Configure systemd service
# Start services
```

---

## ✅ Pre-Deployment Checklist

Before deploying, verify:

```bash
cd /path/to/Hospital\ Management

# Check Python version
python --version  # Should be 3.8+

# Verify dependencies
pip list | grep -E "Django|gunicorn|psycopg2"

# Check static files location
cat hospital_management/settings.py | grep STATIC

# Verify build.sh
head -n 10 build.sh

# Test locally
python manage.py runserver 0.0.0.0:8000
```

---

## 🔐 Production Security Settings

Update `hospital_management/settings.py`:

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# HTTPS & Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": (
        "'self'",
        "cdn.jsdelivr.net",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js",
    ),
    "style-src": (
        "'self'",
        "'unsafe-inline'",
        "cdn.jsdelivr.net",
    ),
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
```

---

## 📊 Post-Deployment Tasks

### 1. Create Superuser (Admin)
```bash
# On Render: Go to Dashboard → Shell (if available)
# Or SSH into your server

python manage.py createsuperuser
# Enter username, email, password
```

### 2. Verify Deployment
```bash
curl https://your-domain.com/
# Should return HTML homepage
```

### 3. Access Admin Panel
```
https://your-domain.com/admin/
```

### 4. Configure Email (Optional)
- Update EMAIL settings in environment variables
- Test with: `python manage.py shell`
  ```python
  from django.core.mail import send_mail
  send_mail('Test', 'Email works!', 'from@example.com', ['to@example.com'])
  ```

### 5. Monitor Logs
```bash
# Render
# Dashboard → Logs tab

# Heroku
heroku logs --tail --app hospital-management

# Self-hosted
tail -f /var/log/nginx/access.log
journalctl -u hospital-management -f
```

---

## 🐛 Common Deployment Issues

### Issue: Static Files Not Loading
**Solution**:
```bash
python manage.py collectstatic --clear --noinput
# Restart your service
```

### Issue: Database Connection Error
**Solution**:
- Verify DATABASE_URL environment variable
- Check database server is running
- Test connection:
  ```bash
  python manage.py dbshell
  ```

### Issue: 500 Internal Server Error
**Solution**:
- Check logs for detailed error
- Verify ALLOWED_HOSTS setting
- Ensure all migrations ran:
  ```bash
  python manage.py migrate --check
  ```

### Issue: Email Not Sending
**Solution**:
- Verify EMAIL_* environment variables
- Check firewall allows port 587
- Test SMTP connection:
  ```bash
  python manage.py shell
  >>> import smtplib
  >>> smtplib.SMTP('smtp.gmail.com', 587).starttls()
  ```

---

## 📈 Performance Optimization

### 1. Enable Caching (Redis)
```python
# For Render: Add Redis add-on
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}
```

### 2. Database Optimization
```bash
# Create indexes
python manage.py dbshell
CREATE INDEX idx_appointment_date ON medicines_appointment(date);
CREATE INDEX idx_patient_email ON patients_patient(email);
```

### 3. CDN for Static Files
- Configure CloudFlare or AWS CloudFront
- Point to your static files domain

---

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push (Render)
1. Render automatically deploys when you push to main
2. To disable: Project Settings → Disable auto-deploy

### Manual Deployment Commands
```bash
# Push to GitHub
git push origin main

# Render automatically picks up changes and deploys

# For Heroku
git push heroku main
```

---

## 📱 Mobile Considerations

The app is already mobile-responsive, but verify on deployment:
- Test on iPhone/Android
- Check viewport settings in base.html
- Verify touch-friendly button sizes

---

## 🎯 Next Steps After Deployment

1. **Domain Setup** (Optional)
   - Purchase domain from GoDaddy, Namecheap, etc.
   - Point DNS to your hosting service
   - Update ALLOWED_HOSTS with your domain

2. **SSL Certificate** (Usually Automatic)
   - Render/Heroku provide free SSL
   - Verify HTTPS works

3. **Backup Strategy**
   - Daily database backups
   - GitHub is your code backup

4. **Monitoring**
   - Set up alerts for high error rates
   - Monitor CPU/Memory usage
   - Check database size regularly

---

## 📞 Support & Resources

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/5.2/howto/deployment/
- **Heroku Django**: https://devcenter.heroku.com/articles/getting-started-with-django
- **AWS Django**: https://aws.amazon.com/getting-started/hands-on/run-web-app-with-django/

---

## 🎉 Deployment Status

```
✅ Code pushed to GitHub
✅ Procfile configured
✅ build.sh ready
✅ requirements.txt up-to-date
✅ Ready for Render deployment!
```

**Your app is ready for production! 🚀**
