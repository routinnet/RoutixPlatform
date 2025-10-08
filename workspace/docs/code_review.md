# Routix Platform Code Review

## Repository Overview
The repository is split into a FastAPI backend under `workspace/backend` and a Next.js frontend under `workspace/frontend`. The backend exposes REST endpoints for authentication, templates, and AI generation orchestration, while the frontend provides a chat-driven thumbnail generation experience that depends on REST and WebSocket APIs. The following sections summarize the main findings from reviewing each side of the codebase.

## Backend Findings

### Configuration and secrets
* Sensitive defaults are checked into source control. Both the JWT `SECRET_KEY` and the primary database connection string embed placeholder secrets directly in `app/core/config.py`, which risks accidental use in non-development environments and encourages weak operational hygiene.【F:workspace/backend/app/core/config.py†L9-L83】

### Authentication and authorization
* `get_current_user` returns a fabricated user assembled from JWT claims instead of hydrating the account from persistent storage. Any field included in a forged token (including `is_admin`) would be blindly trusted, so role checks on admin endpoints are ineffective.【F:workspace/backend/app/core/dependencies.py†L13-L70】
* The authentication router issues tokens through `UserService`, but the service itself is an in-memory/Redis abstraction that does not integrate with SQLAlchemy models. Consequently, the FastAPI dependency graph mixes token validation with mocked persistence, creating divergent paths between `/api/v1/auth/*` and `/api/v1/users/*` flows.

### Data persistence and caching
* `UserService` uses Redis as the primary store via helper methods like `_store_user_data` without any relational persistence fallback; all user data can disappear if Redis is flushed. The module instantiates a singleton `user_service = UserService()` which reinforces the reliance on cache state.【F:workspace/backend/app/services/user_service.py†L640-L710】【F:workspace/backend/app/services/user_service.py†L889-L890】
* The service writes refresh tokens and transaction history through calls such as `redis_service.expire`, but `RedisService` never implements an `expire` method, so these operations will raise `AttributeError` at runtime.【F:workspace/backend/app/services/user_service.py†L681-L710】【F:workspace/backend/app/services/redis_service.py†L1-L213】

### Async blocking and resilience
* Every method in `RedisService` is declared `async` but delegates to the synchronous `redis` client. These blocking calls run on the event loop thread and can significantly degrade throughput under load; a true async driver (e.g., `aioredis`/`redis.asyncio`) or execution in a thread pool is needed.【F:workspace/backend/app/services/redis_service.py†L1-L200】
* Rate limiting is advertised via Redis sorted sets, yet the service stores per-process counters without namespacing by IP/user and lacks error surfacing, leading to inconsistent throttling behavior.【F:workspace/backend/app/services/redis_service.py†L154-L179】

### Realtime transport mismatch
* The only WebSocket endpoint simply echoes text payloads and does not authenticate subscribers or publish generation updates.【F:workspace/backend/app/api/v1/endpoints/websocket.py†L15-L28】 Frontend clients expect rich Socket.IO events for generation progress, so the backend needs a compatible implementation.

## Frontend Findings

### API client ergonomics
* The global Axios instance reads from `localStorage` in interceptors during module initialization. Because this file is shared between client and (potential) server contexts, importing it in a server component or middleware would throw `ReferenceError: localStorage is not defined`. Consider lazy access guarded by runtime checks or confining the client to browser-only modules.【F:workspace/frontend/lib/api.ts†L1-L114】
* The client references numerous REST routes such as `/api/v1/generation/create` and `/api/v1/generations/user` that do not exist in the FastAPI router, so many UI flows will fail at runtime until the backend contracts are aligned.【F:workspace/frontend/lib/api.ts†L62-L112】【F:workspace/backend/app/api/v1/api.py†L7-L26】

### Authentication state
* Tokens are stored in `localStorage` and reused across requests and WebSocket connections, making them vulnerable to theft via XSS. There is no HttpOnly cookie option, CSRF protection, or refresh token rotation logic on logout.【F:workspace/frontend/lib/auth.tsx†L38-L102】【F:workspace/frontend/lib/websocket.ts†L21-L105】
* `AuthProvider` blindly redirects to `/login` whenever `apiClient.getProfile()` fails, so transient 5xx errors will log users out instead of surfacing a recoverable error state.【F:workspace/frontend/lib/auth.tsx†L83-L104】

### Realtime UX expectations
* The chat interface subscribes to Socket.IO channels (`subscribe_generation`, `generation_progress`, etc.) and updates UI state based on detailed payloads, but the backend only exposes a bare WebSocket echo endpoint. Without matching server events, the chat will stay stuck in a “processing” state and never render the generated thumbnail.【F:workspace/frontend/components/chat/ChatInterface.tsx†L27-L126】【F:workspace/frontend/lib/websocket.ts†L21-L139】【F:workspace/backend/app/api/v1/endpoints/websocket.py†L15-L28】

## Recommendations
1. Externalize secrets into environment variables and fail fast when required values are missing instead of shipping defaults.【F:workspace/backend/app/core/config.py†L9-L83】
2. Replace the mocked `UserService` layer with database-backed CRUD operations and ensure `get_current_user` loads users from persistent storage before enforcing roles.【F:workspace/backend/app/core/dependencies.py†L13-L70】【F:workspace/backend/app/services/user_service.py†L640-L710】
3. Adopt an asynchronous Redis client (or wrap synchronous calls in `run_in_executor`) and implement the missing `expire` helper to keep background tasks non-blocking and error-free.【F:workspace/backend/app/services/redis_service.py†L1-L213】【F:workspace/backend/app/services/user_service.py†L681-L710】
4. Align frontend API expectations with actual FastAPI routes; add missing endpoints or update the client to call existing paths before further UI work.【F:workspace/frontend/lib/api.ts†L62-L112】【F:workspace/backend/app/api/v1/api.py†L7-L26】
5. Harden the authentication surface by moving tokens to cookies, handling refresh failures gracefully, and securing WebSocket handshakes with backend validation logic that mirrors the frontend’s Socket.IO contract.【F:workspace/frontend/lib/auth.tsx†L38-L104】【F:workspace/frontend/lib/websocket.ts†L21-L139】【F:workspace/backend/app/api/v1/endpoints/websocket.py†L15-L28】

