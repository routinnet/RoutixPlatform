# Routix Platform - راهنمای استقرار و راه‌اندازی

<div dir="rtl">

## 🚀 راهنمای استقرار سریع

این راهنما شامل دستورالعمل‌های کامل برای راه‌اندازی پروژه Routix است.

---

## 📋 پیش‌نیازها

### نرم‌افزارهای مورد نیاز

```bash
# سیستم عامل
- Linux / macOS / Windows (WSL2 recommended)

# Runtime Environments
- Python 3.11+ 
- Node.js 18+
- npm 9+ یا yarn 1.22+

# Databases
- PostgreSQL 15+
- Redis 7+

# اختیاری
- Docker 24+
- Docker Compose 2+
```

### API Keys مورد نیاز

```env
GEMINI_API_KEY=       # از Google AI Studio
OPENAI_API_KEY=       # از OpenAI Platform
MIDJOURNEY_API_KEY=   # از GoAPI.ai یا Meydi
```

---

## 🔧 روش 1: نصب با Docker (پیشنهادی)

### مرحله 1: Clone و تنظیم Environment

```bash
# Clone repository
git clone <your-repo-url>
cd routix-platform

# کپی فایل .env
cp .env.example .env

# ویرایش .env و اضافه کردن API Keys
nano .env  # یا vi, vim, code, etc.
```

### مرحله 2: تنظیمات Environment

فایل `.env` را با اطلاعات زیر پر کنید:

```env
# Core Settings
SECRET_KEY=your-very-secret-key-here-change-in-production
ENVIRONMENT=production
DEBUG=false
VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://routix:routix123@postgres:5432/routix
POSTGRES_SERVER=postgres
POSTGRES_USER=routix
POSTGRES_PASSWORD=routix123
POSTGRES_DB=routix

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_DAYS=30

# AI Services
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
MIDJOURNEY_API_KEY=your_goapi_key_here

# CORS (اجازه دسترسی از frontend)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000"]
ALLOWED_HOSTS=["*"]

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_IMAGE_EXTENSIONS=[".jpg",".jpeg",".png"]

# Email (اختیاری)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@routix.com

# Stripe (اختیاری)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### مرحله 3: اجرای Docker Compose

```bash
# Build و اجرای تمام سرویس‌ها
docker-compose up -d

# مشاهده logs
docker-compose logs -f

# بررسی وضعیت
docker-compose ps
```

### مرحله 4: اجرای Migration

```bash
# اجرای migration برای ایجاد جداول
docker-compose exec backend alembic upgrade head

# ایجاد کاربر admin
docker-compose exec backend python -c "
from app.services.user_service import user_service
import asyncio

async def create_admin():
    admin = await user_service.create_user(
        email='admin@routix.com',
        password='Admin123!',
        full_name='Admin User',
        is_admin=True
    )
    print(f'Admin created: {admin.email}')

asyncio.run(create_admin())
"
```

### مرحله 5: دسترسی به سرویس‌ها

```
✅ Backend API: http://localhost:8000
✅ API Docs: http://localhost:8000/docs
✅ Frontend: http://localhost:5173
✅ PostgreSQL: localhost:5432
✅ Redis: localhost:6379
```

---

## 🛠️ روش 2: نصب دستی

### Backend Setup

```bash
cd workspace/backend

# ایجاد محیط مجازی Python
python -m venv venv

# فعال‌سازی
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows

# نصب dependencies
pip install --upgrade pip
pip install -r requirements.txt

# تنظیم environment variables
cp .env.example .env
# ویرایش .env

# اجرای migration
alembic upgrade head

# اجرای سرور
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd workspace/shadcn-ui

# نصب dependencies
npm install

# اجرای development server
npm run dev

# Build برای production
npm run build

# Preview production build
npm run preview
```

### Celery Workers Setup

```bash
cd workspace/backend

# Terminal 1: Worker
celery -A app.workers.celery_app worker \
  --loglevel=info \
  --concurrency=4

# Terminal 2: Beat (برای scheduled tasks)
celery -A app.workers.celery_app beat \
  --loglevel=info
```

### PostgreSQL Setup (اگر Docker استفاده نمی‌کنید)

```bash
# نصب PostgreSQL
sudo apt-get install postgresql-15  # Ubuntu/Debian
# یا
brew install postgresql@15  # macOS

# ایجاد database و user
sudo -u postgres psql

postgres=# CREATE DATABASE routix;
postgres=# CREATE USER routix WITH PASSWORD 'routix123';
postgres=# GRANT ALL PRIVILEGES ON DATABASE routix TO routix;
postgres=# \q
```

### Redis Setup (اگر Docker استفاده نمی‌کنید)

```bash
# نصب Redis
sudo apt-get install redis-server  # Ubuntu/Debian
# یا
brew install redis  # macOS

# اجرا
redis-server

# تست
redis-cli ping  # باید PONG برگرداند
```

---

## 🧪 تست سیستم

### بررسی Backend

```bash
# Health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# API documentation
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux
```

### بررسی Frontend

```bash
# باز کردن در مرورگر
open http://localhost:5173
```

### تست API با curl

```bash
# ثبت‌نام کاربر
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# ورود
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'

# ذخیره token
export TOKEN="<access_token_from_login>"

# دریافت اطلاعات کاربر
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📦 استقرار Production

### آماده‌سازی برای Production

```bash
# 1. تغییر SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# کپی کردن خروجی و جایگذاری در .env

# 2. تنظیم DEBUG=false
sed -i 's/DEBUG=true/DEBUG=false/' .env

# 3. تنظیم CORS برای دامنه واقعی
# در .env:
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]

# 4. Build Frontend
cd workspace/shadcn-ui
npm run build
```

### استقرار با Docker Compose (Production)

```bash
# استفاده از docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# با Nginx reverse proxy
# افزودن nginx.conf برای SSL و load balancing
```

### استقرار در AWS

```bash
# 1. ایجاد EC2 Instance
# - AMI: Ubuntu 22.04
# - Instance Type: t3.medium یا بالاتر
# - Storage: 30GB SSD

# 2. نصب Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

# 3. Clone و Deploy
git clone <repo>
cd routix-platform
docker-compose -f docker-compose.prod.yml up -d

# 4. تنظیم Nginx + SSL
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### استقرار در DigitalOcean

```bash
# 1. ایجاد Droplet
# - OS: Ubuntu 22.04
# - Plan: $12/month (2GB RAM)

# 2. اتصال SSH
ssh root@your-droplet-ip

# 3. نصب و اجرا
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
git clone <repo>
cd routix-platform
docker-compose up -d
```

---

## 🔒 امنیت

### چک‌لیست امنیت

- [ ] SECRET_KEY تغییر کرده است
- [ ] DEBUG=false در production
- [ ] HTTPS/TLS فعال است
- [ ] CORS صحیح تنظیم شده
- [ ] Firewall فعال است (فقط 80, 443, 22)
- [ ] Database password قوی است
- [ ] API Keys در environment variables هستند (نه در کد)
- [ ] Rate limiting فعال است
- [ ] Backup روزانه تنظیم شده

### تنظیم Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# بررسی وضعیت
sudo ufw status
```

---

## 💾 Backup و Recovery

### Backup دیتابیس

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U routix routix > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U routix routix < backup_20241015.sql
```

### Backup Redis

```bash
# Backup
docker-compose exec redis redis-cli SAVE
docker cp routix-redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb

# Restore
docker cp redis_backup_20241015.rdb routix-redis:/data/dump.rdb
docker-compose restart redis
```

### Backup فایل‌ها

```bash
# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz workspace/backend/uploads/

# Restore
tar -xzf uploads_backup_20241015.tar.gz
```

---

## 📊 Monitoring

### Logs

```bash
# تمام logs
docker-compose logs -f

# فقط backend
docker-compose logs -f backend

# فقط celery worker
docker-compose logs -f celery-worker

# 100 خط آخر
docker-compose logs --tail=100
```

### System Metrics

```bash
# استفاده از منابع
docker stats

# Disk usage
du -sh workspace/backend/uploads/
docker system df
```

---

## 🐛 عیب‌یابی

### مشکلات رایج

#### 1. Backend start نمی‌شود

```bash
# بررسی logs
docker-compose logs backend

# بررسی database connection
docker-compose exec backend python -c "
from app.core.database import engine
import asyncio
async def test():
    async with engine.begin() as conn:
        print('Database connection OK')
asyncio.run(test())
"
```

#### 2. Frontend به backend وصل نمی‌شود

```bash
# بررسی CORS settings
# در .env:
BACKEND_CORS_ORIGINS=["http://localhost:5173"]

# Restart backend
docker-compose restart backend
```

#### 3. Celery tasks اجرا نمی‌شوند

```bash
# بررسی Redis
docker-compose exec redis redis-cli ping

# بررسی Celery worker
docker-compose logs celery-worker

# Restart worker
docker-compose restart celery-worker
```

#### 4. Out of Memory

```bash
# بررسی استفاده از RAM
free -h

# افزایش swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🔄 بروزرسانی

### بروزرسانی کد

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d

# اجرای migration های جدید
docker-compose exec backend alembic upgrade head
```

---

## 📞 پشتیبانی

برای مشکلات و سوالات:

- 📧 Email: support@routix.com
- 📚 Documentation: [docs.routix.com]
- 💬 Discord: [Join Server]

---

**موفق باشید! 🚀**

</div>
