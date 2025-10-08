# Routix Platform - System Architecture Design

## Executive Summary

This document outlines the complete system architecture for the Routix Platform, an AI-powered thumbnail generation platform with a ChatGPT-like conversational interface. The architecture follows microservices principles with FastAPI backend, Next.js frontend, and multiple AI service integrations.

## Implementation Approach

We will implement the following critical components:

1. **Chat-Based Interface** - Conversational UI with real-time messaging
2. **AI Template Matching Pipeline** - Secret template library with vector search
3. **Multi-Algorithm Generation System** - "Routix Versions" with different AI providers
4. **Real-Time Progress Tracking** - WebSocket-based status updates
5. **Admin Panel** - Template management and analytics dashboard
6. **Credit System** - Usage tracking and subscription management
7. **Security Layer** - JWT authentication with role-based access

Key technical challenges addressed:
- Vector similarity search for template matching
- Real-time communication for generation progress
- Scalable background task processing
- Secure template storage (never exposed to users)
- Multi-provider AI integration with fallbacks

## Main User-UI Interaction Patterns

### 1. Chat-Based Thumbnail Generation Flow
```
User: "Create gaming thumbnail with explosions"
↓
AI: "Got it! 🎮 Let me create that for you..."
AI: [Algorithm Selector: Routix v1, Pro, Lightning]
↓
User: [Clicks Routix v1]
↓
AI: "Would you like to add your face or logo?"
AI: [Upload buttons inline]
↓
User: [Uploads face image]
↓
AI: "Perfect! Generating now... ✨"
AI: [Progress: "Analyzing..." → "Generating..." → "Complete!"]
↓
AI: [Thumbnail Image Card with Download/Regenerate/Share buttons]
```

### 2. Admin Template Management Flow
```
Admin: Bulk upload templates → Drag & drop interface
↓
System: Upload to R2 storage → Create database entries
↓
Background: AI analysis → Extract design DNA → Generate embeddings
↓
Admin: Monitor progress → Templates become available for generation
```

### 3. Real-Time Progress Updates
```
WebSocket Connection: User ↔ Backend
Status Updates: analyzing → searching → composing → generating → completed
Progress: 0% → 30% → 50% → 90% → 100%
```

## System Architecture

```plantuml
@startuml
!define RECTANGLE class

package "Frontend Layer" {
    [Next.js 14 App] as NextJS
    [Chat Interface] as Chat
    [Admin Panel] as Admin
    [WebSocket Client] as WSClient
}

package "API Gateway" {
    [FastAPI Gateway] as Gateway
    [Authentication Middleware] as Auth
    [Rate Limiting] as RateLimit
}

package "Core Services" {
    [Chat Service] as ChatSvc
    [Generation Service] as GenSvc
    [Template Service] as TemplateSvc
    [User Service] as UserSvc
    [Admin Service] as AdminSvc
}

package "AI Services" {
    [Gemini Vision API] as Gemini
    [OpenAI GPT-4 Vision] as OpenAI
    [Midjourney API] as Midjourney
    [OpenAI Embeddings] as Embeddings
}

package "Background Processing" {
    [Celery Workers] as Celery
    [Template Analysis] as Analysis
    [Generation Pipeline] as Pipeline
}

package "Data Layer" {
    [PostgreSQL + pgvector] as DB
    [Redis Cache/Queue] as Redis
    [Cloudflare R2 Storage] as Storage
}

package "Real-time Layer" {
    [WebSocket Server] as WSServer
    [Server-Sent Events] as SSE
}

NextJS --> Gateway
Chat --> WSClient
Admin --> Gateway
WSClient --> WSServer

Gateway --> Auth
Gateway --> RateLimit
Gateway --> ChatSvc
Gateway --> GenSvc
Gateway --> TemplateSvc
Gateway --> UserSvc
Gateway --> AdminSvc

ChatSvc --> DB
ChatSvc --> WSServer
GenSvc --> Pipeline
GenSvc --> Celery
TemplateSvc --> Analysis
TemplateSvc --> Storage
UserSvc --> DB
AdminSvc --> DB

Pipeline --> Gemini
Pipeline --> OpenAI
Pipeline --> Midjourney
Analysis --> Gemini
Analysis --> Embeddings

Celery --> Redis
Pipeline --> Redis
WSServer --> Redis

ChatSvc --> Redis
GenSvc --> DB
TemplateSvc --> DB
Analysis --> DB
@enduml
```

## UI Navigation Flow

```plantuml
@startuml
state "Welcome Screen" as Welcome {
    [*] --> Welcome
    Welcome : Large Routix Logo
    Welcome : "Hey [Username]! Can I help you with anything?"
    Welcome : Suggested prompt chips
}

state "Chat Interface" as Chat {
    Chat : Message history
    Chat : Input bar with file upload
    Chat : Real-time typing indicators
}

state "Admin Dashboard" as AdminDash {
    AdminDash : Analytics overview
    AdminDash : System health metrics
}

state "Template Management" as Templates {
    Templates : Drag & drop upload
    Templates : Template grid/list view
    Templates : Bulk operations
}

state "Algorithm Management" as Algorithms {
    Algorithms : Routix Versions CRUD
    Algorithms : Configuration editor
    Algorithms : Performance metrics
}

state "User Management" as Users {
    Users : User list with filters
    Users : Credit management
    Users : Subscription handling
}

Welcome --> Chat : Start conversation
Chat --> Welcome : New chat
Chat --> Chat : Continue conversation

Welcome --> AdminDash : Admin login
AdminDash --> Templates : Manage templates
AdminDash --> Algorithms : Manage algorithms
AdminDash --> Users : Manage users
Templates --> AdminDash : Back to dashboard
Algorithms --> AdminDash : Back to dashboard
Users --> AdminDash : Back to dashboard
@enduml
```

## Class Diagram

```plantuml
@startuml

interface ITemplateService {
    +upload_template(file: UploadFile, metadata: TemplateMetadata): Template
    +analyze_template(template_id: UUID): TemplateAnalysis
    +search_templates(query: str, filters: Dict): List[Template]
    +get_template_performance(template_id: UUID): PerformanceMetrics
}

interface IGenerationService {
    +create_generation_request(user_id: UUID, prompt: str, algorithm_id: UUID): GenerationRequest
    +process_generation(request_id: UUID): GenerationResult
    +get_generation_status(request_id: UUID): GenerationStatus
    +update_progress(request_id: UUID, progress: int, status: str): None
}

interface IChatService {
    +create_conversation(user_id: UUID): Conversation
    +send_message(conversation_id: UUID, message: Message): Message
    +get_conversation_history(conversation_id: UUID): List[Message]
    +update_conversation_title(conversation_id: UUID, title: str): None
}

interface IUserService {
    +create_user(user_data: UserCreate): User
    +authenticate_user(credentials: UserCredentials): AuthToken
    +update_credits(user_id: UUID, amount: int): User
    +get_user_usage(user_id: UUID): UsageStats
}

class Template {
    +id: UUID
    +image_url: str
    +thumbnail_url: str
    +style_dna: Dict
    +embedding: List[float]
    +category: str
    +tags: List[str]
    +has_face: bool
    +has_text: bool
    +has_logo: bool
    +energy_level: int
    +performance_score: float
    +usage_count: int
    +is_active: bool
    +created_at: datetime
    +updated_at: datetime
}

class GenerationAlgorithm {
    +id: UUID
    +name: str
    +display_name: str
    +ai_provider: str
    +config: Dict
    +cost_per_generation: float
    +credit_cost: int
    +is_active: bool
    +is_default: bool
    +performance_metrics: Dict
}

class GenerationRequest {
    +id: UUID
    +user_id: UUID
    +algorithm_id: UUID
    +prompt: str
    +user_face_url: str
    +user_logo_url: str
    +custom_text: str
    +status: GenerationStatus
    +progress: int
    +selected_template_id: UUID
    +final_thumbnail_url: str
    +processing_time: float
    +cost_incurred: float
    +created_at: datetime
    +completed_at: datetime
}

class User {
    +id: UUID
    +email: str
    +username: str
    +password_hash: str
    +credits: int
    +subscription_tier: str
    +is_active: bool
    +is_admin: bool
    +created_at: datetime
    +last_login: datetime
}

class Conversation {
    +id: UUID
    +user_id: UUID
    +title: str
    +messages: List[Message]
    +created_at: datetime
    +updated_at: datetime
}

class Message {
    +id: UUID
    +conversation_id: UUID
    +role: str
    +type: str
    +content: str
    +metadata: Dict
    +timestamp: datetime
}

enum GenerationStatus {
    PENDING
    ANALYZING
    SEARCHING
    COMPOSING
    GENERATING
    COMPLETED
    FAILED
}

ITemplateService ..> Template
IGenerationService ..> GenerationRequest
IGenerationService ..> GenerationAlgorithm
IChatService ..> Conversation
IChatService ..> Message
IUserService ..> User

GenerationRequest --> User
GenerationRequest --> GenerationAlgorithm
GenerationRequest --> Template
Conversation --> User
Message --> Conversation
@enduml
```

## Sequence Diagram

```plantuml
@startuml
actor User
participant "Chat UI" as UI
participant "WebSocket" as WS
participant "API Gateway" as Gateway
participant "Chat Service" as ChatSvc
participant "Generation Service" as GenSvc
participant "Template Service" as TemplateSvc
participant "AI Services" as AI
participant "Celery Worker" as Worker
participant "Database" as DB

User -> UI: Types "Create gaming thumbnail"
UI -> Gateway: POST /api/chat/message
    note right
        Input: {
            "conversation_id": "uuid",
            "content": "Create gaming thumbnail",
            "type": "text"
        }
    end note

Gateway -> ChatSvc: process_message()
ChatSvc -> DB: Save user message
ChatSvc -> GenSvc: analyze_request()
    note right
        Input: {
            "prompt": "Create gaming thumbnail",
            "user_id": "uuid"
        }
    end note

GenSvc -> AI: Analyze prompt with Gemini Vision
AI --> GenSvc: Intent analysis result
    note right
        Output: {
            "category": "gaming",
            "style": "energetic",
            "elements": ["explosions", "action"]
        }
    end note

GenSvc -> TemplateSvc: search_templates()
    note right
        Input: {
            "query_embedding": [0.1, 0.2, ...],
            "filters": {"category": "gaming"},
            "limit": 3
        }
    end note

TemplateSvc -> DB: Vector similarity search
DB --> TemplateSvc: Top matching templates
    note right
        Output: {
            "templates": [
                {"id": "uuid1", "similarity": 0.95},
                {"id": "uuid2", "similarity": 0.89},
                {"id": "uuid3", "similarity": 0.85}
            ]
        }
    end note

GenSvc -> ChatSvc: Send algorithm selection
ChatSvc -> WS: Broadcast message
WS -> UI: Display algorithm options
    note right
        Output: {
            "type": "algorithm_select",
            "options": [
                {"id": "routix_v1", "name": "Routix v1"},
                {"id": "routix_pro", "name": "Routix Pro"},
                {"id": "routix_lightning", "name": "Routix Lightning"}
            ]
        }
    end note

User -> UI: Selects "Routix v1"
UI -> Gateway: POST /api/generation/create
    note right
        Input: {
            "algorithm_id": "routix_v1",
            "prompt": "Create gaming thumbnail",
            "template_preferences": {...}
        }
    end note

Gateway -> GenSvc: create_generation_request()
GenSvc -> DB: Create generation record
GenSvc -> Worker: Queue generation task
    note right
        Task: {
            "request_id": "uuid",
            "algorithm_id": "routix_v1",
            "template_id": "uuid1",
            "prompt": "enhanced_prompt"
        }
    end note

Worker -> GenSvc: Update progress (10%)
GenSvc -> WS: Broadcast progress
WS -> UI: "Analyzing your request..."

Worker -> AI: Generate thumbnail via Midjourney
    note right
        Input: {
            "prompt": "gaming thumbnail with explosions, energetic style --ar 16:9 --style raw",
            "style_reference": "template_style_dna",
            "character_reference": "user_face_url"
        }
    end note

Worker -> GenSvc: Update progress (50%)
GenSvc -> WS: Broadcast progress
WS -> UI: "Generating thumbnail..."

AI --> Worker: Generation complete
    note right
        Output: {
            "image_url": "https://cdn.midjourney.com/...",
            "generation_id": "mj_12345",
            "status": "completed"
        }
    end note

Worker -> GenSvc: Update progress (100%)
Worker -> DB: Save final result
GenSvc -> WS: Broadcast completion
WS -> UI: Display thumbnail result
    note right
        Output: {
            "type": "thumbnail_result",
            "image_url": "https://storage.routix.com/...",
            "actions": ["download", "regenerate", "share"],
            "metadata": {
                "generation_time": "28s",
                "algorithm": "Routix v1"
            }
        }
    end note

UI -> User: Show thumbnail with actions
@enduml
```

## Database ER Diagram

```plantuml
@startuml
!define TABLE entity
!define PK <<PK>>
!define FK <<FK>>

entity "users" as users {
    * id : uuid PK
    --
    * email : varchar(255)
    * username : varchar(100)
    * password_hash : varchar(255)
    * credits : integer
    * subscription_tier : varchar(50)
    * is_active : boolean
    * is_admin : boolean
    * created_at : timestamp
    * updated_at : timestamp
    * last_login : timestamp
}

entity "templates" as templates {
    * id : uuid PK
    --
    * image_url : varchar(500)
    * thumbnail_url : varchar(500)
    * style_dna : jsonb
    * embedding : vector(1536)
    * category : varchar(100)
    * tags : varchar[]
    * description : text
    * has_face : boolean
    * has_text : boolean
    * has_logo : boolean
    * energy_level : integer
    * performance_score : float
    * usage_count : integer
    * success_rate : float
    * is_active : boolean
    * is_featured : boolean
    * priority : integer
    * created_at : timestamp
    * updated_at : timestamp
}

entity "generation_algorithms" as algorithms {
    * id : uuid PK
    --
    * name : varchar(100)
    * display_name : varchar(100)
    * ai_provider : varchar(50)
    * config : jsonb
    * cost_per_generation : decimal(10,4)
    * credit_cost : integer
    * is_active : boolean
    * is_default : boolean
    * performance_metrics : jsonb
    * created_at : timestamp
    * updated_at : timestamp
}

entity "generation_requests" as requests {
    * id : uuid PK
    --
    * user_id : uuid FK
    * algorithm_id : uuid FK
    * selected_template_id : uuid FK
    * prompt : text
    * style_preference : varchar(100)
    * user_face_url : varchar(500)
    * user_logo_url : varchar(500)
    * custom_text : varchar(500)
    * status : varchar(50)
    * progress : integer
    * final_thumbnail_url : varchar(500)
    * processing_time : float
    * cost_incurred : decimal(10,4)
    * error_message : text
    * created_at : timestamp
    * completed_at : timestamp
}

entity "conversations" as conversations {
    * id : uuid PK
    --
    * user_id : uuid FK
    * title : varchar(200)
    * created_at : timestamp
    * updated_at : timestamp
}

entity "messages" as messages {
    * id : uuid PK
    --
    * conversation_id : uuid FK
    * role : varchar(20)
    * type : varchar(50)
    * content : text
    * metadata : jsonb
    * timestamp : timestamp
}

entity "user_assets" as assets {
    * id : uuid PK
    --
    * user_id : uuid FK
    * asset_type : varchar(50)
    * file_url : varchar(500)
    * file_name : varchar(255)
    * file_size : bigint
    * mime_type : varchar(100)
    * is_active : boolean
    * created_at : timestamp
}

entity "subscriptions" as subscriptions {
    * id : uuid PK
    --
    * user_id : uuid FK
    * plan_name : varchar(100)
    * status : varchar(50)
    * current_period_start : timestamp
    * current_period_end : timestamp
    * stripe_subscription_id : varchar(255)
    * created_at : timestamp
    * updated_at : timestamp
}

entity "credit_transactions" as transactions {
    * id : uuid PK
    --
    * user_id : uuid FK
    * generation_request_id : uuid FK
    * transaction_type : varchar(50)
    * amount : integer
    * balance_after : integer
    * description : varchar(255)
    * created_at : timestamp
}

entity "admin_audit_log" as audit {
    * id : uuid PK
    --
    * admin_user_id : uuid FK
    * action : varchar(100)
    * resource_type : varchar(100)
    * resource_id : uuid
    * changes : jsonb
    * ip_address : inet
    * user_agent : varchar(500)
    * created_at : timestamp
}

users ||--o{ requests : "requests.user_id -> users.id"
users ||--o{ conversations : "conversations.user_id -> users.id"
users ||--o{ assets : "assets.user_id -> users.id"
users ||--o{ subscriptions : "subscriptions.user_id -> users.id"
users ||--o{ transactions : "transactions.user_id -> users.id"
users ||--o{ audit : "audit.admin_user_id -> users.id"

algorithms ||--o{ requests : "requests.algorithm_id -> algorithms.id"
templates ||--o{ requests : "requests.selected_template_id -> templates.id"

conversations ||--o{ messages : "messages.conversation_id -> conversations.id"
requests ||--o{ transactions : "transactions.generation_request_id -> requests.id"
@enduml
```

## Backend Architecture

### 1. FastAPI Application Structure

```python
# Project Structure
routix-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── security.py        # JWT and authentication
│   │   ├── database.py        # Database connection
│   │   └── dependencies.py    # Dependency injection
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── generation.py
│   │   │   │   ├── templates.py
│   │   │   │   ├── users.py
│   │   │   │   └── admin.py
│   │   │   └── api.py
│   │   └── deps.py
│   ├── models/
│   │   ├── user.py
│   │   ├── template.py
│   │   ├── generation.py
│   │   ├── conversation.py
│   │   └── base.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── template.py
│   │   ├── generation.py
│   │   └── conversation.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── generation_service.py
│   │   ├── template_service.py
│   │   ├── ai_service.py
│   │   └── websocket_service.py
│   ├── workers/
│   │   ├── celery_app.py
│   │   ├── template_analysis.py
│   │   ├── generation_pipeline.py
│   │   └── cleanup_tasks.py
│   └── utils/
│       ├── vector_search.py
│       ├── file_upload.py
│       └── monitoring.py
├── alembic/                   # Database migrations
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### 2. Core Services Architecture

```python
# Core Service Interfaces
class TemplateService:
    async def upload_template(self, file: UploadFile, metadata: dict) -> Template
    async def analyze_template(self, template_id: UUID) -> dict
    async def search_templates(self, query_embedding: List[float], filters: dict) -> List[Template]
    async def get_performance_metrics(self, template_id: UUID) -> dict

class GenerationService:
    async def create_request(self, user_id: UUID, prompt: str, algorithm_id: UUID) -> GenerationRequest
    async def process_generation(self, request_id: UUID) -> None
    async def update_progress(self, request_id: UUID, progress: int, status: str) -> None
    async def get_status(self, request_id: UUID) -> GenerationStatus

class ChatService:
    async def create_conversation(self, user_id: UUID) -> Conversation
    async def send_message(self, conversation_id: UUID, message: dict) -> Message
    async def get_history(self, conversation_id: UUID, limit: int = 50) -> List[Message]
    async def update_title(self, conversation_id: UUID, title: str) -> None
```

### 3. Database Configuration

```python
# PostgreSQL with pgvector setup
DATABASE_URL = "postgresql://user:pass@localhost/routix"

# SQLAlchemy models with vector support
class Template(Base):
    __tablename__ = "templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension
    style_dna = Column(JSON)
    
    # Vector similarity search index
    __table_args__ = (
        Index('ix_templates_embedding', 'embedding', postgresql_using='ivfflat'),
    )

# Redis configuration for caching and queues
REDIS_URL = "redis://localhost:6379"
redis_client = redis.from_url(REDIS_URL)

# Celery configuration
celery_app = Celery(
    "routix",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.workers.template_analysis', 'app.workers.generation_pipeline']
)
```

### 4. AI Services Integration

```python
class AIServiceManager:
    def __init__(self):
        self.gemini_client = genai.GenerativeModel('gemini-pro-vision')
        self.openai_client = openai.OpenAI()
        self.midjourney_client = MidjourneyAPI()
    
    async def analyze_template(self, image_url: str) -> dict:
        """Extract design DNA using Gemini Vision"""
        try:
            response = await self.gemini_client.generate_content([
                "Analyze this thumbnail design and extract:",
                "1. Color palette (dominant colors)",
                "2. Typography style (bold, script, etc.)",
                "3. Composition (layout, focal points)",
                "4. Energy level (1-10 scale)",
                "5. Visual elements (face, text, objects)",
                "Return as structured JSON.",
                {"mime_type": "image/jpeg", "data": image_url}
            ])
            return json.loads(response.text)
        except Exception as e:
            # Fallback to OpenAI GPT-4 Vision
            return await self._analyze_with_openai(image_url)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for semantic search"""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    async def generate_thumbnail(self, prompt: str, style_ref: str, char_ref: str = None) -> str:
        """Generate thumbnail using Midjourney API"""
        enhanced_prompt = f"{prompt} --ar 16:9 --style raw --stylize 750"
        if style_ref:
            enhanced_prompt += f" --sref {style_ref}"
        if char_ref:
            enhanced_prompt += f" --cref {char_ref}"
        
        job = await self.midjourney_client.imagine(enhanced_prompt)
        return await self._poll_generation_status(job.id)
```

## Frontend Architecture

### 1. Next.js 14 Project Structure

```typescript
// Project Structure
routix-frontend/
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx              # Landing page
│   ├── chat/
│   │   ├── page.tsx          # Main chat interface
│   │   ├── [id]/page.tsx     # Specific conversation
│   │   └── layout.tsx
│   ├── admin/
│   │   ├── page.tsx          # Admin dashboard
│   │   ├── templates/
│   │   ├── users/
│   │   ├── algorithms/
│   │   └── analytics/
│   └── api/                  # API routes (if needed)
├── components/
│   ├── ui/                   # Base UI components
│   │   ├── glass-card.tsx
│   │   ├── gradient-button.tsx
│   │   ├── progress-indicator.tsx
│   │   └── file-upload-zone.tsx
│   ├── chat/
│   │   ├── chat-container.tsx
│   │   ├── message-list.tsx
│   │   ├── chat-input.tsx
│   │   ├── message-bubble.tsx
│   │   └── thumbnail-card.tsx
│   ├── admin/
│   │   ├── template-grid.tsx
│   │   ├── user-table.tsx
│   │   ├── analytics-dashboard.tsx
│   │   └── algorithm-manager.tsx
│   └── layout/
│       ├── sidebar.tsx
│       ├── header.tsx
│       └── navigation.tsx
├── lib/
│   ├── api.ts               # API client
│   ├── websocket.ts         # WebSocket manager
│   ├── auth.ts              # Authentication
│   ├── store.ts             # Zustand store
│   └── utils.ts
├── hooks/
│   ├── use-chat.ts
│   ├── use-websocket.ts
│   ├── use-auth.ts
│   └── use-generation.ts
├── types/
│   ├── api.ts
│   ├── chat.ts
│   ├── user.ts
│   └── generation.ts
└── styles/
    ├── globals.css
    └── components.css
```

### 2. Design System Implementation

```typescript
// Glassmorphism Design System
export const theme = {
  colors: {
    primary: '#6B5DD3',
    accent: '#8B7AFF',
    background: 'linear-gradient(135deg, #E0C3FC 0%, #D5E1FF 25%, #E8F4FF 50%, #FFE8F5 75%, #FFE5E5 100%)',
    text: {
      primary: '#2D2A4A',
      secondary: '#6B6B8D'
    },
    glass: {
      background: 'rgba(255, 255, 255, 0.25)',
      border: 'rgba(255, 255, 255, 0.18)',
      shadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
    }
  },
  effects: {
    backdropBlur: '20px',
    borderRadius: '16px',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
  }
}

// Glass Card Component
export const GlassCard: React.FC<GlassCardProps> = ({ children, className, ...props }) => {
  return (
    <div
      className={cn(
        "backdrop-blur-[20px] bg-white/25 border border-white/18",
        "rounded-2xl shadow-[0_8px_32px_0_rgba(31,38,135,0.37)]",
        "transition-all duration-300 ease-out",
        "hover:bg-white/30 hover:shadow-[0_12px_40px_0_rgba(31,38,135,0.45)]",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// Gradient Button Component
export const GradientButton: React.FC<ButtonProps> = ({ children, variant = "primary", ...props }) => {
  return (
    <button
      className={cn(
        "px-6 py-3 rounded-xl font-semibold text-white",
        "bg-gradient-to-r from-purple-600 to-purple-500",
        "hover:from-purple-700 hover:to-purple-600",
        "transform hover:scale-105 transition-all duration-200",
        "shadow-lg hover:shadow-xl",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
      )}
      {...props}
    >
      {children}
    </button>
  )
}
```

### 3. Chat Interface Implementation

```typescript
// Chat Container Component
export const ChatContainer: React.FC = () => {
  const { messages, sendMessage, isLoading } = useChat()
  const { isConnected, progress } = useWebSocket()
  
  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-100 via-blue-50 to-pink-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <MessageList messages={messages} />
        <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
        {progress && <ProgressIndicator progress={progress} />}
      </div>
    </div>
  )
}

// Message List Component
export const MessageList: React.FC<{ messages: Message[] }> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}

// WebSocket Hook
export const useWebSocket = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [progress, setProgress] = useState<ProgressUpdate | null>(null)
  
  useEffect(() => {
    const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/ws`)
    
    ws.onopen = () => {
      setIsConnected(true)
      setSocket(ws)
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'progress_update') {
        setProgress(data.payload)
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      setSocket(null)
    }
    
    return () => {
      ws.close()
    }
  }, [])
  
  return { socket, isConnected, progress }
}
```

## Real-Time Communication Strategy

### 1. WebSocket Implementation

```python
# Backend WebSocket Manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[UUID, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: UUID, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
    
    async def disconnect(self, connection_id: str, user_id: UUID):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].remove(connection_id)
    
    async def send_to_user(self, user_id: UUID, message: dict):
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_json(message)
    
    async def broadcast_progress(self, user_id: UUID, request_id: UUID, progress: int, status: str):
        message = {
            "type": "progress_update",
            "payload": {
                "request_id": str(request_id),
                "progress": progress,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.send_to_user(user_id, message)

# FastAPI WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user = await get_current_user_from_token(token)
    connection_id = str(uuid.uuid4())
    
    await websocket_manager.connect(websocket, user.id, connection_id)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_id, user.id)
```

### 2. Progress Tracking System

```python
# Generation Progress Tracker
class ProgressTracker:
    def __init__(self, websocket_manager: WebSocketManager):
        self.ws_manager = websocket_manager
        self.redis_client = redis.from_url(REDIS_URL)
    
    async def update_progress(self, request_id: UUID, user_id: UUID, progress: int, status: str, message: str = ""):
        # Update database
        await self.update_request_progress(request_id, progress, status)
        
        # Cache in Redis for fast access
        progress_data = {
            "progress": progress,
            "status": status,
            "message": message,
            "updated_at": datetime.utcnow().isoformat()
        }
        await self.redis_client.setex(
            f"progress:{request_id}",
            300,  # 5 minutes TTL
            json.dumps(progress_data)
        )
        
        # Broadcast to user via WebSocket
        await self.ws_manager.broadcast_progress(user_id, request_id, progress, status)
    
    async def get_progress(self, request_id: UUID) -> dict:
        # Try Redis first (fast)
        cached = await self.redis_client.get(f"progress:{request_id}")
        if cached:
            return json.loads(cached)
        
        # Fallback to database
        return await self.get_request_progress(request_id)

# Celery Task with Progress Updates
@celery_app.task(bind=True)
def generate_thumbnail_task(self, request_id: str, user_id: str, algorithm_config: dict):
    progress_tracker = ProgressTracker(websocket_manager)
    
    try:
        # Step 1: Analyze request (10%)
        await progress_tracker.update_progress(
            UUID(request_id), UUID(user_id), 10, "analyzing", "Analyzing your request..."
        )
        
        # Step 2: Search templates (30%)
        await progress_tracker.update_progress(
            UUID(request_id), UUID(user_id), 30, "searching", "Finding best matching templates..."
        )
        
        # Step 3: Compose prompt (50%)
        await progress_tracker.update_progress(
            UUID(request_id), UUID(user_id), 50, "composing", "Composing generation prompt..."
        )
        
        # Step 4: Generate with AI (70-95%)
        await progress_tracker.update_progress(
            UUID(request_id), UUID(user_id), 70, "generating", "Generating your thumbnail..."
        )
        
        # AI generation with periodic updates
        result = await ai_service.generate_thumbnail(algorithm_config)
        
        # Step 5: Complete (100%)
        await progress_tracker.update_progress(
            UUID(request_id), UUID(user_id), 100, "completed", "Your thumbnail is ready!"
        )
        
        return result
        
    except Exception as e:
        await progress_tracker.update_progress(
            UUID(request_id), UUID(user_id), 0, "failed", f"Generation failed: {str(e)}"
        )
        raise
```

## Security & Authentication

### 1. JWT Authentication Flow

```python
# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user or not self.verify_password(password, user.password_hash):
            return None
        return user

# Authentication Dependencies
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await get_user(UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user

# Role-based Access Control
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### 2. API Security Measures

```python
# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Protected Endpoints
@app.post("/api/v1/generation/create")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def create_generation(
    request: Request,
    generation_data: GenerationCreate,
    current_user: User = Depends(get_current_user)
):
    # Check user credits
    if current_user.credits < generation_data.algorithm.credit_cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits"
        )
    
    # Create generation request
    return await generation_service.create_request(current_user.id, generation_data)

# Input Validation
class GenerationCreate(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    algorithm_id: UUID
    user_face_url: Optional[HttpUrl] = None
    user_logo_url: Optional[HttpUrl] = None
    custom_text: Optional[str] = Field(None, max_length=200)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        # Check for inappropriate content
        if contains_inappropriate_content(v):
            raise ValueError('Prompt contains inappropriate content')
        return v

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://routix.com", "https://app.routix.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## Template Analysis Pipeline

### 1. AI-Powered Design DNA Extraction

```python
class TemplateAnalyzer:
    def __init__(self):
        self.gemini_client = genai.GenerativeModel('gemini-pro-vision')
        self.openai_client = openai.OpenAI()
        self.embedding_service = EmbeddingService()
    
    async def analyze_template(self, template_id: UUID, image_url: str) -> dict:
        """Extract comprehensive design DNA from template image"""
        
        # Step 1: Visual Analysis with Gemini Vision
        design_dna = await self._extract_visual_features(image_url)
        
        # Step 2: Generate semantic embeddings
        embedding = await self._generate_embedding(design_dna)
        
        # Step 3: Classify template characteristics
        classification = await self._classify_template(design_dna)
        
        # Step 4: Calculate energy and style metrics
        metrics = await self._calculate_metrics(design_dna)
        
        # Combine all analysis results
        complete_analysis = {
            "visual_features": design_dna,
            "embedding": embedding,
            "classification": classification,
            "metrics": metrics,
            "analysis_version": "1.0",
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        await self._save_analysis(template_id, complete_analysis)
        
        return complete_analysis
    
    async def _extract_visual_features(self, image_url: str) -> dict:
        """Use Gemini Vision to extract detailed visual features"""
        
        prompt = """
        Analyze this thumbnail design and extract detailed information:
        
        1. COLOR ANALYSIS:
           - Primary colors (hex codes)
           - Secondary colors
           - Color temperature (warm/cool)
           - Contrast level (high/medium/low)
        
        2. TYPOGRAPHY:
           - Text style (bold, script, modern, etc.)
           - Text size (large, medium, small)
           - Text placement (center, corner, overlay)
           - Font characteristics
        
        3. COMPOSITION:
           - Layout type (centered, rule-of-thirds, asymmetric)
           - Focal points
           - Visual hierarchy
           - Balance (symmetric/asymmetric)
        
        4. VISUAL ELEMENTS:
           - Has human face (yes/no)
           - Has text overlay (yes/no)
           - Has logo/branding (yes/no)
           - Background type (solid, gradient, image, pattern)
           - Visual effects (glow, shadow, blur, etc.)
        
        5. STYLE CHARACTERISTICS:
           - Design style (minimalist, maximalist, vintage, modern, etc.)
           - Energy level (1-10, where 1=calm, 10=high-energy)
           - Mood (exciting, professional, playful, dramatic, etc.)
           - Target audience (gaming, business, lifestyle, etc.)
        
        Return as valid JSON only, no additional text.
        """
        
        try:
            response = await self.gemini_client.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_url}
            ])
            
            # Parse and validate JSON response
            design_dna = json.loads(response.text)
            return self._validate_design_dna(design_dna)
            
        except Exception as e:
            # Fallback to OpenAI GPT-4 Vision
            return await self._extract_with_openai(image_url, prompt)
    
    async def _generate_embedding(self, design_dna: dict) -> List[float]:
        """Generate semantic embedding for template search"""
        
        # Create searchable text from design DNA
        searchable_text = self._create_searchable_text(design_dna)
        
        # Generate embedding using OpenAI
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=searchable_text
        )
        
        return response.data[0].embedding
    
    def _create_searchable_text(self, design_dna: dict) -> str:
        """Convert design DNA to searchable text for embedding"""
        
        elements = []
        
        # Add style characteristics
        if "style_characteristics" in design_dna:
            style = design_dna["style_characteristics"]
            elements.extend([
                style.get("design_style", ""),
                style.get("mood", ""),
                style.get("target_audience", "")
            ])
        
        # Add color information
        if "color_analysis" in design_dna:
            colors = design_dna["color_analysis"]
            elements.extend([
                colors.get("color_temperature", ""),
                f"contrast {colors.get('contrast_level', '')}"
            ])
        
        # Add composition details
        if "composition" in design_dna:
            comp = design_dna["composition"]
            elements.extend([
                comp.get("layout_type", ""),
                comp.get("balance", "")
            ])
        
        # Add visual elements
        if "visual_elements" in design_dna:
            visual = design_dna["visual_elements"]
            if visual.get("has_human_face"):
                elements.append("human face person")
            if visual.get("has_text_overlay"):
                elements.append("text overlay typography")
            if visual.get("has_logo_branding"):
                elements.append("logo branding")
        
        return " ".join(filter(None, elements))

# Celery Task for Background Analysis
@celery_app.task(bind=True)
def analyze_template_task(self, template_id: str, image_url: str):
    """Background task to analyze uploaded template"""
    
    analyzer = TemplateAnalyzer()
    
    try:
        # Update status to analyzing
        update_template_status(UUID(template_id), "analyzing")
        
        # Perform analysis
        analysis_result = await analyzer.analyze_template(UUID(template_id), image_url)
        
        # Update template with results
        await update_template_analysis(UUID(template_id), analysis_result)
        
        # Update status to completed
        await update_template_status(UUID(template_id), "analyzed")
        
        return {
            "template_id": template_id,
            "status": "completed",
            "analysis_version": analysis_result["analysis_version"]
        }
        
    except Exception as e:
        # Update status to failed
        await update_template_status(UUID(template_id), "failed")
        
        # Log error
        logger.error(f"Template analysis failed for {template_id}: {str(e)}")
        
        raise self.retry(exc=e, countdown=60, max_retries=3)
```

### 2. Vector Search Implementation

```python
class VectorSearchService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def search_similar_templates(
        self,
        query_embedding: List[float],
        filters: dict = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[dict]:
        """Search for similar templates using vector similarity"""
        
        # Base query with vector similarity
        query = select(Template).where(
            Template.is_active == True,
            Template.embedding.cosine_distance(query_embedding) < (1 - similarity_threshold)
        )
        
        # Apply filters
        if filters:
            if "category" in filters:
                query = query.where(Template.category == filters["category"])
            
            if "has_face" in filters:
                query = query.where(Template.has_face == filters["has_face"])
            
            if "has_text" in filters:
                query = query.where(Template.has_text == filters["has_text"])
            
            if "energy_level_min" in filters:
                query = query.where(Template.energy_level >= filters["energy_level_min"])
            
            if "energy_level_max" in filters:
                query = query.where(Template.energy_level <= filters["energy_level_max"])
        
        # Order by similarity and performance
        query = query.order_by(
            Template.embedding.cosine_distance(query_embedding),
            Template.performance_score.desc()
        ).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        # Calculate similarity scores
        results = []
        for template in templates:
            similarity = 1 - cosine_distance(query_embedding, template.embedding)
            results.append({
                "template": template,
                "similarity_score": similarity,
                "performance_score": template.performance_score
            })
        
        return results
    
    async def create_query_embedding(self, user_prompt: str, intent_analysis: dict) -> List[float]:
        """Create search embedding from user prompt and AI analysis"""
        
        # Enhance prompt with intent analysis
        enhanced_query = self._enhance_search_query(user_prompt, intent_analysis)
        
        # Generate embedding
        embedding_service = EmbeddingService()
        return await embedding_service.generate_embedding(enhanced_query)
    
    def _enhance_search_query(self, prompt: str, intent: dict) -> str:
        """Enhance user prompt with AI-extracted intent for better search"""
        
        enhanced_parts = [prompt]
        
        if "category" in intent:
            enhanced_parts.append(f"category:{intent['category']}")
        
        if "style" in intent:
            enhanced_parts.append(f"style:{intent['style']}")
        
        if "mood" in intent:
            enhanced_parts.append(f"mood:{intent['mood']}")
        
        if "energy_level" in intent:
            enhanced_parts.append(f"energy:{intent['energy_level']}")
        
        if "visual_elements" in intent:
            for element in intent["visual_elements"]:
                enhanced_parts.append(element)
        
        return " ".join(enhanced_parts)
```

## Scalability Considerations

### 1. Database Optimization

```python
# Database Connection Pooling
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": False
}

# Read Replicas for Scaling
class DatabaseManager:
    def __init__(self):
        self.write_engine = create_async_engine(WRITE_DB_URL, **DATABASE_CONFIG)
        self.read_engines = [
            create_async_engine(READ_url, **DATABASE_CONFIG) 
            for read_url in READ_DB_URLS
        ]
        self.read_engine_index = 0
    
    def get_write_session(self):
        return AsyncSession(self.write_engine)
    
    def get_read_session(self):
        # Round-robin read replica selection
        engine = self.read_engines[self.read_engine_index]
        self.read_engine_index = (self.read_engine_index + 1) % len(self.read_engines)
        return AsyncSession(engine)

# Vector Index Optimization
"""
-- Create optimized indexes for vector search
CREATE INDEX CONCURRENTLY idx_templates_embedding_ivfflat 
ON templates USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Composite indexes for filtered searches
CREATE INDEX CONCURRENTLY idx_templates_category_active 
ON templates (category, is_active) 
WHERE is_active = true;

CREATE INDEX CONCURRENTLY idx_templates_performance 
ON templates (performance_score DESC, usage_count DESC) 
WHERE is_active = true;

-- Partial indexes for common queries
CREATE INDEX CONCURRENTLY idx_templates_has_face 
ON templates (has_face, energy_level) 
WHERE is_active = true AND has_face = true;
"""
```

### 2. Caching Strategy

```python
# Redis Caching Layers
class CacheService:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)
        self.default_ttl = 3600  # 1 hour
    
    async def get_template_analysis(self, template_id: UUID) -> Optional[dict]:
        """Cache template analysis results"""
        key = f"template:analysis:{template_id}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
    
    async def set_template_analysis(self, template_id: UUID, analysis: dict):
        key = f"template:analysis:{template_id}"
        await self.redis.setex(key, self.default_ttl * 24, json.dumps(analysis))  # 24 hours
    
    async def get_search_results(self, query_hash: str) -> Optional[List[dict]]:
        """Cache search results for identical queries"""
        key = f"search:results:{query_hash}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
    
    async def set_search_results(self, query_hash: str, results: List[dict]):
        key = f"search:results:{query_hash}"
        await self.redis.setex(key, 300, json.dumps(results))  # 5 minutes
    
    async def get_user_credits(self, user_id: UUID) -> Optional[int]:
        """Cache user credits for fast access"""
        key = f"user:credits:{user_id}"
        cached = await self.redis.get(key)
        return int(cached) if cached else None
    
    async def update_user_credits(self, user_id: UUID, credits: int):
        key = f"user:credits:{user_id}"
        await self.redis.setex(key, 300, str(credits))  # 5 minutes

# Application-level Caching
from functools import lru_cache
from cachetools import TTLCache
import asyncio

# In-memory cache for frequently accessed data
template_cache = TTLCache(maxsize=1000, ttl=3600)  # 1000 templates, 1 hour TTL
algorithm_cache = TTLCache(maxsize=50, ttl=7200)   # 50 algorithms, 2 hours TTL

@lru_cache(maxsize=128)
def get_algorithm_config(algorithm_id: str) -> dict:
    """Cache algorithm configurations"""
    return algorithm_cache.get(algorithm_id) or fetch_algorithm_config(algorithm_id)
```

### 3. Load Balancing & Auto-scaling

```yaml
# Docker Compose for Horizontal Scaling
version: '3.8'

services:
  # Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api-1
      - api-2
      - api-3

  # API Instances
  api-1:
    build: .
    environment:
      - INSTANCE_ID=api-1
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  api-2:
    build: .
    environment:
      - INSTANCE_ID=api-2
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  api-3:
    build: .
    environment:
      - INSTANCE_ID=api-3
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # Celery Workers
  worker-1:
    build: .
    command: celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
    environment:
      - WORKER_TYPE=generation
      - REDIS_URL=${REDIS_URL}
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'

  worker-2:
    build: .
    command: celery -A app.workers.celery_app worker --loglevel=info --concurrency=2
    environment:
      - WORKER_TYPE=analysis
      - REDIS_URL=${REDIS_URL}
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'

  # Database
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=routix
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'

  # Redis
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

volumes:
  postgres_data:
```

### 4. Monitoring & Observability

```python
# Application Metrics
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
generation_requests = Counter('generation_requests_total', 'Total generation requests', ['algorithm', 'status'])
generation_duration = Histogram('generation_duration_seconds', 'Generation duration', ['algorithm'])
active_users = Gauge('active_users', 'Number of active users')
template_searches = Counter('template_searches_total', 'Total template searches')
api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])

# Middleware for request tracking
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    api_requests.labels(
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()
    
    return response

# Health Check Endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check AI services
    for service_name, service in ai_services.items():
        try:
            await service.health_check()
            health_status["services"][service_name] = "healthy"
        except Exception as e:
            health_status["services"][service_name] = f"unhealthy: {str(e)}"
    
    return health_status
```

## API Contracts & Integration Points

### 1. REST API Specification

```yaml
# OpenAPI 3.0 Specification
openapi: 3.0.0
info:
  title: Routix Platform API
  version: 1.0.0
  description: AI-powered thumbnail generation platform

paths:
  /api/v1/auth/login:
    post:
      summary: User authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
      responses:
        200:
          description: Authentication successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
                  user:
                    $ref: '#/components/schemas/User'

  /api/v1/chat/conversations:
    get:
      summary: Get user conversations
      security:
        - bearerAuth: []
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        200:
          description: List of conversations
          content:
            application/json:
              schema:
                type: object
                properties:
                  conversations:
                    type: array
                    items:
                      $ref: '#/components/schemas/Conversation'
                  total:
                    type: integer

    post:
      summary: Create new conversation
      security:
        - bearerAuth: []
      responses:
        201:
          description: Conversation created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Conversation'

  /api/v1/chat/conversations/{conversation_id}/messages:
    get:
      summary: Get conversation messages
      security:
        - bearerAuth: []
      parameters:
        - name: conversation_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: List of messages
          content:
            application/json:
              schema:
                type: object
                properties:
                  messages:
                    type: array
                    items:
                      $ref: '#/components/schemas/Message'

    post:
      summary: Send message
      security:
        - bearerAuth: []
      parameters:
        - name: conversation_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                content:
                  type: string
                type:
                  type: string
                  enum: [text, file_upload, algorithm_selection]
                metadata:
                  type: object
      responses:
        201:
          description: Message sent
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Message'

  /api/v1/generation/create:
    post:
      summary: Create generation request
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conversation_id:
                  type: string
                  format: uuid
                prompt:
                  type: string
                  minLength: 1
                  maxLength: 1000
                algorithm_id:
                  type: string
                  format: uuid
                user_face_url:
                  type: string
                  format: uri
                user_logo_url:
                  type: string
                  format: uri
                custom_text:
                  type: string
                  maxLength: 200
      responses:
        201:
          description: Generation request created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenerationRequest'

  /api/v1/generation/{request_id}/status:
    get:
      summary: Get generation status
      security:
        - bearerAuth: []
      parameters:
        - name: request_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Generation status
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                  status:
                    type: string
                    enum: [pending, analyzing, searching, composing, generating, completed, failed]
                  progress:
                    type: integer
                    minimum: 0
                    maximum: 100
                  message:
                    type: string
                  final_thumbnail_url:
                    type: string
                    format: uri
                  processing_time:
                    type: number

  /api/v1/admin/templates:
    get:
      summary: Get templates (Admin)
      security:
        - bearerAuth: []
      parameters:
        - name: category
          in: query
          schema:
            type: string
        - name: status
          in: query
          schema:
            type: string
            enum: [pending_analysis, analyzing, analyzed, failed]
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
      responses:
        200:
          description: List of templates
          content:
            application/json:
              schema:
                type: object
                properties:
                  templates:
                    type: array
                    items:
                      $ref: '#/components/schemas/Template'

    post:
      summary: Upload template (Admin)
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                category:
                  type: string
                tags:
                  type: array
                  items:
                    type: string
                description:
                  type: string
      responses:
        201:
          description: Template uploaded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Template'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        username:
          type: string
        credits:
          type: integer
        subscription_tier:
          type: string
        created_at:
          type: string
          format: date-time

    Conversation:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    Message:
      type: object
      properties:
        id:
          type: string
          format: uuid
        role:
          type: string
          enum: [user, assistant, system]
        type:
          type: string
        content:
          type: string
        metadata:
          type: object
        timestamp:
          type: string
          format: date-time

    Template:
      type: object
      properties:
        id:
          type: string
          format: uuid
        image_url:
          type: string
          format: uri
        thumbnail_url:
          type: string
          format: uri
        category:
          type: string
        tags:
          type: array
          items:
            type: string
        performance_score:
          type: number
        usage_count:
          type: integer
        is_active:
          type: boolean

    GenerationRequest:
      type: object
      properties:
        id:
          type: string
          format: uuid
        status:
          type: string
        progress:
          type: integer
        created_at:
          type: string
          format: date-time

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### 2. WebSocket Events

```typescript
// WebSocket Event Types
interface WebSocketEvents {
  // Connection Events
  'connection:established': {
    connection_id: string;
    user_id: string;
    timestamp: string;
  };

  'connection:error': {
    error: string;
    code: number;
  };

  // Generation Progress Events
  'generation:progress': {
    request_id: string;
    progress: number;
    status: 'analyzing' | 'searching' | 'composing' | 'generating';
    message: string;
    timestamp: string;
  };

  'generation:completed': {
    request_id: string;
    thumbnail_url: string;
    processing_time: number;
    algorithm_used: string;
    timestamp: string;
  };

  'generation:failed': {
    request_id: string;
    error: string;
    retry_possible: boolean;
    timestamp: string;
  };

  // Chat Events
  'chat:message': {
    conversation_id: string;
    message: Message;
    timestamp: string;
  };

  'chat:typing': {
    conversation_id: string;
    is_typing: boolean;
    timestamp: string;
  };

  // System Events
  'system:maintenance': {
    message: string;
    scheduled_time: string;
    duration_minutes: number;
  };

  'system:credits_low': {
    user_id: string;
    current_credits: number;
    threshold: number;
  };
}

// Frontend WebSocket Client
class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws?token=${token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };

      this.ws.onclose = () => {
        this.handleDisconnect();
      };

      this.ws.onerror = (error) => {
        reject(error);
      };
    });
  }

  private handleMessage(data: any) {
    switch (data.type) {
      case 'generation:progress':
        this.onProgressUpdate(data.payload);
        break;
      case 'generation:completed':
        this.onGenerationCompleted(data.payload);
        break;
      case 'chat:message':
        this.onChatMessage(data.payload);
        break;
      // Handle other event types...
    }
  }

  private handleDisconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.reconnect();
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
    }
  }
}
```

## Anything UNCLEAR

The following aspects require clarification or further specification:

### 1. AI Service Integration Details
- **Midjourney API Access**: Need to confirm availability and pricing for unofficial APIs (GoAPI.ai, UseAPI.net)
- **Rate Limiting**: Specific rate limits for each AI provider need to be defined
- **Fallback Strategy**: Detailed fallback logic when primary AI services are unavailable
- **Cost Optimization**: Strategy for minimizing AI API costs while maintaining quality

### 2. Template Secrecy Implementation
- **Storage Security**: How to ensure original templates are never accessible via direct URLs
- **Access Control**: Detailed permissions for template viewing/downloading
- **Audit Trail**: Tracking who accesses what templates and when

### 3. Real-time Performance Requirements
- **Concurrent Users**: Specific targets for simultaneous WebSocket connections
- **Message Throughput**: Expected messages per second during peak usage
- **Latency Requirements**: Acceptable delays for progress updates and chat responses

### 4. Scalability Thresholds
- **Auto-scaling Triggers**: CPU/memory thresholds for horizontal scaling
- **Database Sharding**: When and how to implement database partitioning
- **CDN Strategy**: Content delivery for generated thumbnails and static assets

### 5. Business Logic Clarifications
- **Credit Rollover Rules**: Exact logic for unused credit handling
- **Algorithm Pricing**: Different credit costs for different "Routix Versions"
- **Usage Analytics**: What metrics to track for business intelligence

### 6. Security & Compliance
- **Data Retention**: How long to keep user conversations and generated images
- **GDPR Compliance**: User data deletion and export requirements
- **Content Moderation**: Automated filtering for inappropriate content

### 7. Mobile Considerations
- **Progressive Web App**: Requirements for mobile-optimized experience
- **Offline Functionality**: What features should work without internet
- **Push Notifications**: Integration with mobile notification systems

These clarifications will help refine the implementation details and ensure all stakeholders have aligned expectations for the platform's capabilities and constraints.

---

*This system architecture document provides a comprehensive foundation for building the Routix Platform. The modular design allows for iterative development while maintaining scalability and maintainability.*