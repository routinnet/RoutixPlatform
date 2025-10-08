# Routix Platform - File Structure

## Backend Structure (FastAPI)

```
routix-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    # Environment configuration
│   │   ├── security.py                  # JWT authentication & security
│   │   ├── database.py                  # Database connection & session
│   │   ├── dependencies.py              # FastAPI dependencies
│   │   └── exceptions.py                # Custom exception handlers
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py                   # API router aggregation
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py              # Authentication endpoints
│   │           ├── chat.py              # Chat & conversation endpoints
│   │           ├── generation.py        # Thumbnail generation endpoints
│   │           ├── templates.py         # Template management endpoints
│   │           ├── users.py             # User management endpoints
│   │           ├── admin.py             # Admin panel endpoints
│   │           └── websocket.py         # WebSocket endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                      # SQLAlchemy base model
│   │   ├── user.py                      # User model
│   │   ├── template.py                  # Template model
│   │   ├── generation.py               # Generation request model
│   │   ├── conversation.py              # Chat conversation model
│   │   ├── subscription.py              # Subscription model
│   │   └── audit.py                     # Audit log model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                      # User Pydantic schemas
│   │   ├── template.py                  # Template Pydantic schemas
│   │   ├── generation.py               # Generation Pydantic schemas
│   │   ├── conversation.py              # Chat Pydantic schemas
│   │   ├── auth.py                      # Authentication schemas
│   │   └── common.py                    # Common/shared schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py              # Authentication business logic
│   │   ├── chat_service.py              # Chat management service
│   │   ├── generation_service.py        # Generation orchestration
│   │   ├── template_service.py          # Template management service
│   │   ├── user_service.py              # User management service
│   │   ├── ai_service.py                # AI provider integrations
│   │   ├── websocket_service.py         # WebSocket management
│   │   ├── cache_service.py             # Redis caching service
│   │   ├── storage_service.py           # File storage service
│   │   └── payment_service.py           # Stripe payment integration
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py                # Celery application setup
│   │   ├── template_analysis.py         # Template AI analysis tasks
│   │   ├── generation_pipeline.py       # Thumbnail generation tasks
│   │   ├── cleanup_tasks.py             # System cleanup tasks
│   │   └── notification_tasks.py        # Email/notification tasks
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── vector_search.py             # Vector similarity utilities
│   │   ├── file_upload.py               # File upload utilities
│   │   ├── image_processing.py          # Image manipulation utilities
│   │   ├── monitoring.py                # Metrics and monitoring
│   │   ├── validation.py                # Input validation utilities
│   │   └── helpers.py                   # General helper functions
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py                      # CORS middleware
│       ├── rate_limiting.py             # Rate limiting middleware
│       ├── logging.py                   # Request logging middleware
│       └── security.py                  # Security headers middleware
├── alembic/                             # Database migrations
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest configuration
│   ├── test_auth.py                     # Authentication tests
│   ├── test_chat.py                     # Chat functionality tests
│   ├── test_generation.py              # Generation pipeline tests
│   ├── test_templates.py               # Template management tests
│   ├── test_websocket.py               # WebSocket tests
│   └── integration/
│       ├── test_full_flow.py           # End-to-end tests
│       └── test_ai_integration.py      # AI service integration tests
├── scripts/
│   ├── init_db.py                      # Database initialization
│   ├── seed_data.py                    # Sample data seeding
│   ├── migrate_templates.py            # Template migration utilities
│   └── performance_test.py             # Performance testing scripts
├── docker/
│   ├── Dockerfile                      # Main application container
│   ├── Dockerfile.worker              # Celery worker container
│   ├── docker-compose.yml             # Development environment
│   ├── docker-compose.prod.yml        # Production environment
│   └── nginx.conf                      # Nginx configuration
├── .env.example                        # Environment variables template
├── .gitignore
├── requirements.txt                    # Python dependencies
├── requirements-dev.txt               # Development dependencies
├── pyproject.toml                     # Python project configuration
├── README.md
└── Makefile                           # Development commands
```

## Frontend Structure (Next.js 14)

```
routix-frontend/
├── app/
│   ├── globals.css                     # Global styles
│   ├── layout.tsx                      # Root layout
│   ├── page.tsx                        # Landing page
│   ├── loading.tsx                     # Global loading component
│   ├── error.tsx                       # Global error component
│   ├── not-found.tsx                   # 404 page
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx               # Login page
│   │   ├── register/
│   │   │   └── page.tsx               # Registration page
│   │   ├── forgot-password/
│   │   │   └── page.tsx               # Password reset
│   │   └── layout.tsx                 # Auth layout
│   ├── (dashboard)/
│   │   ├── chat/
│   │   │   ├── page.tsx               # Main chat interface
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx           # Specific conversation
│   │   │   └── layout.tsx             # Chat layout
│   │   ├── profile/
│   │   │   ├── page.tsx               # User profile
│   │   │   ├── billing/
│   │   │   │   └── page.tsx           # Billing management
│   │   │   └── assets/
│   │   │       └── page.tsx           # User assets management
│   │   └── layout.tsx                 # Dashboard layout
│   ├── (admin)/
│   │   ├── admin/
│   │   │   ├── page.tsx               # Admin dashboard
│   │   │   ├── templates/
│   │   │   │   ├── page.tsx           # Template management
│   │   │   │   ├── upload/
│   │   │   │   │   └── page.tsx       # Bulk template upload
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # Template details
│   │   │   ├── algorithms/
│   │   │   │   ├── page.tsx           # Algorithm management
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # Algorithm configuration
│   │   │   ├── users/
│   │   │   │   ├── page.tsx           # User management
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx       # User details
│   │   │   ├── generations/
│   │   │   │   └── page.tsx           # Generation monitoring
│   │   │   └── analytics/
│   │   │       └── page.tsx           # Analytics dashboard
│   │   └── layout.tsx                 # Admin layout
│   └── api/                           # API routes (if needed)
│       ├── auth/
│       │   └── callback/
│       │       └── route.ts           # OAuth callback
│       └── webhooks/
│           └── stripe/
│               └── route.ts           # Stripe webhooks
├── components/
│   ├── ui/                            # Base UI components
│   │   ├── glass-card.tsx             # Glassmorphism card component
│   │   ├── gradient-button.tsx        # Purple gradient button
│   │   ├── progress-indicator.tsx     # Animated progress bar
│   │   ├── file-upload-zone.tsx       # Drag & drop file upload
│   │   ├── loading-spinner.tsx        # Loading animations
│   │   ├── modal.tsx                  # Modal component
│   │   ├── tooltip.tsx                # Tooltip component
│   │   ├── badge.tsx                  # Badge component
│   │   ├── input.tsx                  # Input field component
│   │   ├── button.tsx                 # Base button component
│   │   ├── select.tsx                 # Select dropdown
│   │   ├── checkbox.tsx               # Checkbox component
│   │   └── avatar.tsx                 # User avatar component
│   ├── chat/
│   │   ├── chat-container.tsx         # Main chat container
│   │   ├── message-list.tsx           # Scrollable message list
│   │   ├── chat-input.tsx             # Message input with file upload
│   │   ├── message-bubble.tsx         # Individual message display
│   │   ├── thumbnail-card.tsx         # Generated thumbnail display
│   │   ├── algorithm-selector.tsx     # Routix version picker
│   │   ├── progress-message.tsx       # Progress update message
│   │   ├── typing-indicator.tsx       # AI typing animation
│   │   └── conversation-starter.tsx   # Welcome screen prompts
│   ├── admin/
│   │   ├── template-grid.tsx          # Template grid/list view
│   │   ├── template-upload.tsx        # Bulk upload interface
│   │   ├── user-table.tsx             # User management table
│   │   ├── analytics-dashboard.tsx    # Charts and metrics
│   │   ├── algorithm-manager.tsx      # Algorithm CRUD interface
│   │   ├── generation-monitor.tsx     # Real-time generation monitoring
│   │   ├── system-health.tsx          # System status indicators
│   │   └── audit-log.tsx              # Admin action history
│   ├── layout/
│   │   ├── sidebar.tsx                # Navigation sidebar
│   │   ├── header.tsx                 # Top navigation header
│   │   ├── footer.tsx                 # Footer component
│   │   ├── navigation.tsx             # Main navigation menu
│   │   ├── breadcrumb.tsx             # Breadcrumb navigation
│   │   └── mobile-menu.tsx            # Mobile navigation
│   ├── auth/
│   │   ├── login-form.tsx             # Login form component
│   │   ├── register-form.tsx          # Registration form
│   │   ├── password-reset-form.tsx    # Password reset form
│   │   └── social-login.tsx           # OAuth login buttons
│   ├── billing/
│   │   ├── pricing-cards.tsx          # Subscription plans
│   │   ├── payment-form.tsx           # Stripe payment form
│   │   ├── billing-history.tsx        # Invoice history
│   │   └── usage-meter.tsx            # Credit usage display
│   └── common/
│       ├── error-boundary.tsx         # Error boundary component
│       ├── seo-head.tsx               # SEO meta tags
│       ├── theme-provider.tsx         # Theme context provider
│       └── analytics.tsx              # Analytics tracking
├── lib/
│   ├── api.ts                         # API client configuration
│   ├── websocket.ts                   # WebSocket manager
│   ├── auth.ts                        # Authentication utilities
│   ├── store.ts                       # Zustand store configuration
│   ├── utils.ts                       # General utilities
│   ├── constants.ts                   # Application constants
│   ├── validations.ts                 # Form validation schemas
│   └── types.ts                       # Shared TypeScript types
├── hooks/
│   ├── use-chat.ts                    # Chat functionality hook
│   ├── use-websocket.ts               # WebSocket connection hook
│   ├── use-auth.ts                    # Authentication hook
│   ├── use-generation.ts              # Generation status hook
│   ├── use-templates.ts               # Template management hook
│   ├── use-local-storage.ts           # Local storage hook
│   ├── use-debounce.ts                # Debounce hook
│   └── use-intersection-observer.ts   # Intersection observer hook
├── styles/
│   ├── globals.css                    # Global CSS styles
│   ├── components.css                 # Component-specific styles
│   └── themes/
│       ├── light.css                  # Light theme variables
│       └── dark.css                   # Dark theme variables
├── public/
│   ├── images/
│   │   ├── logo.svg                   # Routix logo
│   │   ├── icons/                     # Icon assets
│   │   └── placeholders/              # Placeholder images
│   ├── favicon.ico
│   ├── manifest.json                  # PWA manifest
│   └── robots.txt
├── types/
│   ├── api.ts                         # API response types
│   ├── chat.ts                        # Chat-related types
│   ├── user.ts                        # User-related types
│   ├── generation.ts                  # Generation-related types
│   ├── template.ts                    # Template-related types
│   └── global.d.ts                    # Global type declarations
├── .env.local.example                 # Environment variables template
├── .gitignore
├── next.config.js                     # Next.js configuration
├── tailwind.config.js                 # Tailwind CSS configuration
├── tsconfig.json                      # TypeScript configuration
├── package.json                       # Node.js dependencies
├── README.md
└── yarn.lock                          # Dependency lock file
```

## Infrastructure & DevOps

```
infrastructure/
├── docker/
│   ├── docker-compose.yml             # Development environment
│   ├── docker-compose.prod.yml        # Production environment
│   ├── Dockerfile.api                 # API container
│   ├── Dockerfile.worker              # Celery worker container
│   ├── Dockerfile.frontend            # Frontend container
│   └── nginx.conf                     # Nginx configuration
├── kubernetes/
│   ├── namespace.yaml                 # K8s namespace
│   ├── configmap.yaml                 # Configuration maps
│   ├── secrets.yaml                   # Secrets management
│   ├── api-deployment.yaml            # API deployment
│   ├── worker-deployment.yaml         # Worker deployment
│   ├── frontend-deployment.yaml       # Frontend deployment
│   ├── postgres-deployment.yaml       # Database deployment
│   ├── redis-deployment.yaml          # Redis deployment
│   ├── services.yaml                  # K8s services
│   ├── ingress.yaml                   # Ingress configuration
│   └── hpa.yaml                       # Horizontal Pod Autoscaler
├── terraform/
│   ├── main.tf                        # Main Terraform configuration
│   ├── variables.tf                   # Variable definitions
│   ├── outputs.tf                     # Output definitions
│   ├── modules/
│   │   ├── vpc/                       # VPC module
│   │   ├── rds/                       # RDS module
│   │   ├── elasticache/               # ElastiCache module
│   │   ├── s3/                        # S3 module
│   │   └── cloudfront/                # CloudFront module
│   └── environments/
│       ├── dev/                       # Development environment
│       ├── staging/                   # Staging environment
│       └── prod/                      # Production environment
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml             # Prometheus configuration
│   │   └── alerts.yml                 # Alert rules
│   ├── grafana/
│   │   ├── dashboards/                # Grafana dashboards
│   │   └── datasources.yml            # Data source configuration
│   └── jaeger/
│       └── jaeger.yml                 # Distributed tracing config
├── ci-cd/
│   ├── .github/
│   │   └── workflows/
│   │       ├── api-ci.yml             # API CI/CD pipeline
│   │       ├── frontend-ci.yml        # Frontend CI/CD pipeline
│   │       ├── security-scan.yml      # Security scanning
│   │       └── deploy.yml             # Deployment workflow
│   ├── scripts/
│   │   ├── build.sh                   # Build script
│   │   ├── test.sh                    # Test script
│   │   ├── deploy.sh                  # Deployment script
│   │   └── rollback.sh                # Rollback script
│   └── helm/
│       ├── Chart.yaml                 # Helm chart metadata
│       ├── values.yaml                # Default values
│       ├── templates/                 # Kubernetes templates
│       └── values/
│           ├── dev.yaml               # Development values
│           ├── staging.yaml           # Staging values
│           └── prod.yaml              # Production values
└── docs/
    ├── deployment.md                  # Deployment guide
    ├── monitoring.md                  # Monitoring setup
    ├── security.md                    # Security guidelines
    └── troubleshooting.md             # Troubleshooting guide
```

## Database Migrations

```
migrations/
├── alembic/
│   ├── versions/
│   │   ├── 001_initial_schema.py      # Initial database schema
│   │   ├── 002_add_templates.py       # Template system
│   │   ├── 003_add_vectors.py         # Vector search support
│   │   ├── 004_add_conversations.py   # Chat system
│   │   ├── 005_add_subscriptions.py   # Billing system
│   │   ├── 006_add_audit_logs.py      # Audit logging
│   │   └── 007_add_indexes.py         # Performance indexes
│   ├── env.py                         # Alembic environment
│   ├── script.py.mako                 # Migration template
│   └── alembic.ini                    # Alembic configuration
├── seeds/
│   ├── 001_admin_user.py              # Create admin user
│   ├── 002_default_algorithms.py      # Default generation algorithms
│   ├── 003_sample_templates.py        # Sample templates
│   └── 004_system_settings.py         # System configuration
└── scripts/
    ├── backup.sh                      # Database backup
    ├── restore.sh                     # Database restore
    └── migrate.sh                     # Migration runner
```

## Configuration Files

```
config/
├── environments/
│   ├── development.env                # Development environment
│   ├── staging.env                    # Staging environment
│   ├── production.env                 # Production environment
│   └── testing.env                    # Testing environment
├── nginx/
│   ├── nginx.conf                     # Main Nginx config
│   ├── ssl.conf                       # SSL configuration
│   └── rate-limit.conf                # Rate limiting rules
├── redis/
│   ├── redis.conf                     # Redis configuration
│   └── sentinel.conf                  # Redis Sentinel config
├── postgres/
│   ├── postgresql.conf                # PostgreSQL configuration
│   ├── pg_hba.conf                    # Authentication config
│   └── recovery.conf                  # Recovery configuration
└── monitoring/
    ├── prometheus.yml                 # Prometheus config
    ├── grafana.ini                    # Grafana configuration
    └── jaeger.yml                     # Jaeger tracing config
```

## Key Architecture Decisions

### 1. Technology Stack Rationale

**Frontend: Next.js 14 with App Router**
- Server-side rendering for better SEO and performance
- Built-in API routes for webhooks and callbacks
- Excellent TypeScript support
- Modern React features with concurrent rendering

**Backend: FastAPI with Python**
- High performance async framework
- Automatic API documentation with OpenAPI
- Excellent type hints and validation
- Easy integration with AI/ML libraries

**Database: PostgreSQL with pgvector**
- ACID compliance for financial transactions
- Vector similarity search for template matching
- Mature ecosystem and tooling
- Horizontal scaling capabilities

**Caching: Redis**
- High-performance in-memory storage
- Pub/Sub for real-time features
- Session storage and rate limiting
- Task queue for Celery

### 2. Scalability Patterns

**Microservices Architecture**
- Separate services for chat, generation, templates, and admin
- Independent scaling and deployment
- Clear service boundaries and responsibilities

**Event-Driven Communication**
- WebSocket for real-time updates
- Celery for background processing
- Redis pub/sub for service communication

**Caching Strategy**
- Multi-layer caching (Redis, CDN, browser)
- Cache invalidation strategies
- Read replicas for database scaling

### 3. Security Considerations

**Authentication & Authorization**
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- API rate limiting and throttling

**Data Protection**
- Encrypted storage for sensitive data
- Secure file upload and validation
- HTTPS everywhere with HSTS

**Template Security**
- Original templates never exposed to users
- Signed URLs for authorized access
- Audit logging for all template operations

### 4. Development Workflow

**Code Organization**
- Clear separation of concerns
- Dependency injection for testability
- Type safety throughout the stack

**Testing Strategy**
- Unit tests for business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows

**CI/CD Pipeline**
- Automated testing and security scanning
- Blue-green deployments
- Database migration automation

This file structure provides a solid foundation for building a scalable, maintainable, and secure AI-powered thumbnail generation platform.