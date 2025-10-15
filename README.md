# Routix Platform

<div dir="rtl">

## 🎨 پلتفرم هوش مصنوعی تولید تامبنیل برای یوتیوبرها

Routix یک پلتفرم پیشرفته مبتنی بر هوش مصنوعی است که به کاربران کمک می‌کند تامبنیل‌های حرفه‌ای و جذاب برای ویدیوهای یوتیوب خود بسازند.

### ✨ ویژگی‌های کلیدی

- 🤖 **رابط چت هوشمند**: تعامل طبیعی با AI برای ساخت تامبنیل
- 🎨 **بانک تامبنیل مخفی**: استفاده از تامبنیل‌های طراحی شده توسط 90 طراح حرفه‌ای
- 🔍 **جستجوی معنایی**: پیدا کردن بهترین تامبنیل بر اساس درخواست کاربر
- ⚡ **تولید سریع**: ساخت تامبنیل در کمتر از 60 ثانیه
- 🎯 **الگوریتم‌های متعدد**: Routix V1, V2, V3 با قابلیت‌های مختلف
- 💳 **سیستم اعتبار**: مدل freemium با اشتراک‌های مختلف
- 📊 **پنل ادمین**: مدیریت کامل تامبنیل‌ها، کاربران و آمار

### 🏗️ معماری سیستم

```
routix-platform/
├── workspace/
│   ├── backend/          # FastAPI Backend
│   │   ├── app/
│   │   │   ├── api/      # API Endpoints
│   │   │   ├── core/     # Configuration & Security
│   │   │   ├── models/   # Database Models
│   │   │   ├── services/ # Business Logic
│   │   │   ├── workers/  # Background Tasks (Celery)
│   │   │   └── schemas/  # Pydantic Schemas
│   │   └── alembic/      # Database Migrations
│   ├── frontend/         # Next.js Frontend (Alternative)
│   └── shadcn-ui/        # Main Frontend (Vite + React)
├── docker-compose.yml    # Development Setup
└── docker-compose.prod.yml # Production Setup
```

### 🚀 فناوری‌های استفاده شده

#### Backend
- **FastAPI**: فریمورک وب مدرن و پرسرعت
- **PostgreSQL**: پایگاه داده اصلی
- **Redis**: کش و صف پیام‌ها
- **Celery**: پردازش پس‌زمینه
- **SQLAlchemy**: ORM
- **Alembic**: مدیریت مایگریشن

#### AI Services
- **Google Gemini**: تحلیل تصویر و تولید محتوا
- **OpenAI GPT-4**: پردازش زبان طبیعی
- **OpenAI DALL-E**: تولید تصویر
- **Midjourney API**: تولید تامبنیل حرفه‌ای

#### Frontend
- **React 18**: کتابخانه UI
- **Vite**: Build Tool
- **TailwindCSS**: استایل‌دهی
- **shadcn/ui**: کامپوننت‌های UI
- **React Query**: مدیریت state و API
- **WebSocket**: ارتباط Real-time

### 📦 نصب و راه‌اندازی

#### پیش‌نیازها
```bash
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (اختیاری)
```

#### راه‌اندازی با Docker (پیشنهادی)
```bash
# کلون کردن پروژه
git clone <repository-url>
cd routix-platform

# کپی فایل محیطی
cp .env.example .env
# ویرایش .env و اضافه کردن API Keys

# اجرای سرویس‌ها
docker-compose up -d

# اجرای مایگریشن
docker-compose exec backend alembic upgrade head
```

#### راه‌اندازی دستی

**Backend:**
```bash
cd workspace/backend

# ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای مایگریشن
alembic upgrade head

# اجرای سرور
python run.py
```

**Frontend:**
```bash
cd workspace/shadcn-ui

# نصب وابستگی‌ها
npm install

# اجرای سرور توسعه
npm run dev
```

**Celery Workers:**
```bash
cd workspace/backend

# Worker اصلی
celery -A app.workers.celery_app worker -l info

# Beat برای تسک‌های دوره‌ای
celery -A app.workers.celery_app beat -l info
```

### 🔐 تنظیمات محیطی

فایل `.env` شامل تنظیمات زیر است:

```env
# Core Settings
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/routix

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
MIDJOURNEY_API_KEY=your-midjourney-key

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 📚 مستندات API

بعد از اجرای backend، مستندات API در آدرس‌های زیر در دسترس است:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 🎯 API Endpoints اصلی

#### Authentication
- `POST /api/v1/auth/register` - ثبت‌نام کاربر
- `POST /api/v1/auth/login` - ورود به سیستم
- `POST /api/v1/auth/refresh` - تمدید توکن

#### Templates
- `POST /api/v1/templates/upload` - آپلود تامبنیل به بانک
- `GET /api/v1/templates/search` - جستجوی تامبنیل‌ها
- `DELETE /api/v1/templates/{id}` - حذف تامبنیل

#### Generation
- `POST /api/v1/generation/create` - ساخت تامبنیل جدید
- `GET /api/v1/generation/{id}/status` - وضعیت تولید
- `GET /api/v1/generation/{id}/result` - دریافت نتیجه

#### Chat
- `POST /api/v1/chat/message` - ارسال پیام به AI
- `GET /api/v1/chat/conversations` - لیست مکالمات
- `WS /api/v1/ws/{token}` - WebSocket برای Real-time

#### Admin
- `GET /api/v1/admin/dashboard` - داشبورد ادمین
- `GET /api/v1/admin/analytics` - آمار و تحلیل
- `POST /api/v1/admin/broadcast` - ارسال پیام گروهی

### 🧪 تست

```bash
# Backend Tests
cd workspace/backend
pytest

# Frontend Tests
cd workspace/shadcn-ui
npm run test
```

### 📊 وضعیت پروژه

#### ✅ تکمیل شده
- [x] Backend Core (FastAPI)
- [x] Authentication System
- [x] Database Models
- [x] AI Services Integration
- [x] Template Service
- [x] Generation Pipeline
- [x] Admin Panel APIs
- [x] Frontend UI Components
- [x] WebSocket Support

#### 🚧 در حال توسعه
- [ ] Template Bank Management UI
- [ ] Advanced Analytics Dashboard
- [ ] Payment Integration (Stripe)
- [ ] Email Notifications
- [ ] Mobile App (React Native)

#### 📋 نواقص شناسایی شده
1. **بانک تامبنیل مخفی**: UI برای آپلود و مدیریت تامبنیل‌های طراح‌ها
2. **سیستم پرداخت**: اتصال Stripe و مدیریت اشتراک‌ها
3. **تست‌های جامع**: پوشش تست کامل برای تمام سرویس‌ها
4. **دیتابیس واقعی**: جایگزینی Mock Data با Database Queries
5. **Drag & Drop Upload**: پیاده‌سازی آپلود چندتایی با کشیدن و رها کردن

### 🔧 توسعه

#### ساختار Branch‌ها
- `main`: کد Production
- `development`: کد در حال توسعه
- `feature/*`: برای feature های جدید
- `bugfix/*`: برای رفع باگ‌ها

#### Commit Guidelines
```
feat: Add new feature
fix: Fix a bug
docs: Documentation changes
style: Code style changes
refactor: Code refactoring
test: Add tests
chore: Build/config changes
```

### 🤝 مشارکت

1. Fork کردن پروژه
2. ایجاد Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit تغییرات (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push به Branch (`git push origin feature/AmazingFeature`)
5. ایجاد Pull Request

### 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

### 👥 تیم

- **Backend Development**: AI Agent
- **Frontend Development**: AI Agent  
- **UI/UX Design**: Provided by User
- **Thumbnail Designers**: 90 Professional Designers

### 📞 پشتیبانی

برای سوالات و پشتیبانی:
- 📧 Email: support@routix.com
- 💬 Discord: [Join our server]
- 📚 Docs: [Documentation]

---

**ساخته شده با ❤️ توسط تیم Routix**

</div>
