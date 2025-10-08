# Routix Platform - FastAPI Core Documentation

## 🚀 Phase 1 Complete: FastAPI Application Core

### Architecture Overview

The Routix Platform backend is built with **FastAPI** and follows a clean architecture pattern:

```
app/
├── main.py              # FastAPI application and middleware
├── core/                # Core configuration and utilities
│   ├── config.py        # Environment settings
│   ├── database.py      # Database connection (from Phase 1.1)
│   ├── security.py      # JWT authentication & password hashing
│   ├── dependencies.py  # FastAPI dependency injection
│   └── exceptions.py    # Custom exception classes
├── api/v1/              # API version 1 endpoints
│   ├── api.py          # Main API router
│   └── endpoints/       # Individual endpoint modules
│       ├── auth.py      # Authentication (login, register, refresh)
│       ├── users.py     # User management
│       ├── templates.py # Template management (placeholder)
│       ├── algorithms.py# Algorithm management (placeholder)
│       ├── generations.py# Thumbnail generation (placeholder)
│       ├── conversations.py# Chat history (placeholder)
│       ├── admin.py     # Admin panel (placeholder)
│       └── websocket.py # Real-time communication (placeholder)
├── schemas/             # Pydantic models for request/response
│   ├── auth.py         # Authentication schemas
│   └── user.py         # User schemas
├── services/            # Business logic layer
│   └── user_service.py # User operations
└── models/              # SQLAlchemy models (from Phase 1.1)
```

## 🔧 Core Features Implemented

### 1. FastAPI Application (`app/main.py`)
- **Application lifecycle management** with startup/shutdown events
- **CORS middleware** for frontend integration
- **Security middleware** (TrustedHost)
- **Request timing middleware** for performance monitoring
- **Global exception handling** with custom error responses
- **Health check endpoints** (`/health`, `/health/detailed`)
- **Swagger documentation** at `/docs`

### 2. Configuration Management (`app/core/config.py`)
- **Environment-based settings** using Pydantic BaseSettings
- **Database connection** with PostgreSQL + AsyncPG
- **Security settings** (JWT, CORS, rate limiting)
- **AI service configuration** (OpenAI, Gemini, Midjourney)
- **File storage settings** (local, S3, Cloudflare R2)
- **Payment integration** (Stripe)
- **Email configuration** (SMTP)

### 3. Security System (`app/core/security.py`)
- **JWT authentication** with access and refresh tokens
- **Password hashing** using bcrypt
- **Token verification** and validation
- **Custom JWT Bearer** authentication class
- **Password reset tokens** with expiration
- **Email verification tokens**
- **Rate limiting** utilities

### 4. Dependency Injection (`app/core/dependencies.py`)
- **Database session** management
- **User authentication** dependencies
- **Admin authorization** checks
- **Query parameter** parsing (pagination, search, sorting)
- **Rate limiting** enforcement
- **WebSocket authentication**

### 5. Exception Handling (`app/core/exceptions.py`)
Custom exception classes for:
- Authentication errors (401)
- Authorization errors (403)
- Validation errors (422)
- Not found errors (404)
- Conflict errors (409)
- Insufficient credits (402)
- Rate limit errors (429)
- AI service errors (503)
- File upload errors (400)
- Generation errors (500)

## 🔐 Authentication Flow

### Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

### Login
```http
POST /api/v1/auth/login/json
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 691200
}
```

### Authenticated Requests
```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## 📊 API Endpoints

### Authentication (`/api/v1/auth/`)
- `POST /register` - User registration
- `POST /login` - OAuth2 password flow login
- `POST /login/json` - JSON payload login
- `POST /refresh` - Refresh access token
- `POST /password-reset-request` - Request password reset
- `POST /password-reset` - Reset password with token
- `POST /logout` - Logout (client-side token removal)

### Users (`/api/v1/users/`)
- `GET /me` - Get current user profile
- `PUT /me` - Update current user profile
- `GET /` - Get all users (admin only)
- `GET /{user_id}` - Get user by ID (admin only)
- `DELETE /{user_id}` - Delete user (admin only)

### Health Checks
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with database check

## 🧪 Testing & Verification

### Acceptance Criteria ✅
- [x] **Server starts without errors**
- [x] **Can connect to database**
- [x] **JWT tokens generate and validate correctly**
- [x] **Swagger docs accessible at `/docs`**
- [x] **All API routes registered**
- [x] **User authentication working**
- [x] **Admin user accessible**

### Test Results
```
🚀 ROUTIX PLATFORM - FASTAPI CORE TESTS
==================================================
🧪 Testing database connection...
   ✅ Database connection successful

🧪 Testing JWT authentication...
   ✅ JWT token created and verified

🧪 Testing user service...
   ✅ Admin user found: admin@routix.com
   ✅ User authentication successful

🧪 Testing FastAPI app...
   ✅ FastAPI app initialized with all routes

📊 TEST SUMMARY
==============================
   Passed: 4/4
   Success Rate: 100.0%

🎉 ALL TESTS PASSED! FastAPI Core is ready!
```

## 🚀 Next Steps

### Phase 2: AI Services Integration
1. **Gemini Vision API** integration for template analysis
2. **OpenAI Embeddings** for semantic search
3. **Midjourney API** wrapper for thumbnail generation
4. **Template analysis pipeline**
5. **Semantic search implementation**

### Phase 3: Core Features
1. **Template management system**
2. **Algorithm management** ("Routix Versions")
3. **Generation pipeline** (end-to-end)
4. **Real-time progress tracking**
5. **User credit system**

## 🔧 Development Commands

### Start Development Server
```bash
cd /workspace/backend
python run.py
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
cd /workspace/backend
python test_api.py
```

### Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 📋 Environment Setup

Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `SECRET_KEY` - JWT signing key
- `POSTGRES_*` - Database connection
- `OPENAI_API_KEY` - OpenAI integration
- `GEMINI_API_KEY` - Google Gemini integration
- `MIDJOURNEY_API_KEY` - Midjourney integration

---

**Status:** ✅ **Phase 1 Complete - FastAPI Application Core Ready**  
**Next Phase:** 🚀 **AI Services Integration**