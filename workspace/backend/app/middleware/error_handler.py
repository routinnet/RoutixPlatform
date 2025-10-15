"""
Comprehensive Error Handling Middleware for Routix Platform
Provides consistent error responses and logging across the application
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import traceback
from typing import Union
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standard error response format"""
    
    def __init__(
        self,
        status_code: int,
        error_type: str,
        message: str,
        details: Union[dict, list, None] = None,
        request_id: str = None
    ):
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.details = details
        self.request_id = request_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        response = {
            "success": False,
            "error": {
                "type": self.error_type,
                "message": self.message,
                "timestamp": self.timestamp
            }
        }
        
        if self.details:
            response["error"]["details"] = self.details
        
        if self.request_id:
            response["error"]["request_id"] = self.request_id
        
        return response


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    
    request_id = request.state.__dict__.get("request_id", "unknown")
    
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} | "
        f"Path: {request.url.path} | "
        f"Request ID: {request_id}"
    )
    
    error_response = ErrorResponse(
        status_code=exc.status_code,
        error_type="http_error",
        message=exc.detail,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    
    request_id = request.state.__dict__.get("request_id", "unknown")
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {len(errors)} fields | "
        f"Path: {request.url.path} | "
        f"Request ID: {request_id}"
    )
    
    error_response = ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_type="validation_error",
        message="Request validation failed",
        details={"validation_errors": errors},
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors"""
    
    request_id = request.state.__dict__.get("request_id", "unknown")
    
    logger.error(
        f"Database error: {type(exc).__name__} | "
        f"Path: {request.url.path} | "
        f"Request ID: {request_id}",
        exc_info=True
    )
    
    if isinstance(exc, IntegrityError):
        error_type = "integrity_error"
        message = "Database integrity constraint violation"
        status_code = status.HTTP_409_CONFLICT
        
        details = None
        if "UNIQUE constraint failed" in str(exc):
            details = {"reason": "Duplicate entry - record already exists"}
        elif "FOREIGN KEY constraint failed" in str(exc):
            details = {"reason": "Referenced record does not exist"}
    else:
        error_type = "database_error"
        message = "An error occurred while processing your request"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        details = None
    
    error_response = ErrorResponse(
        status_code=status_code,
        error_type=error_type,
        message=message,
        details=details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions"""
    
    request_id = request.state.__dict__.get("request_id", "unknown")
    
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)} | "
        f"Path: {request.url.path} | "
        f"Request ID: {request_id}",
        exc_info=True
    )
    
    from app.core.config import settings
    
    if settings.is_production:
        message = "An internal error occurred. Please try again later."
        details = None
    else:
        message = f"{type(exc).__name__}: {str(exc)}"
        details = {
            "traceback": traceback.format_exc().split("\n")
        }
    
    error_response = ErrorResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="internal_error",
        message=message,
        details=details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.to_dict()
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app
    
    Usage:
        from app.middleware.error_handler import register_exception_handlers
        register_exception_handlers(app)
    """
    
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Registered exception handlers")


class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundError(BusinessLogicError):
    """Resource not found error"""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class InsufficientCreditsError(BusinessLogicError):
    """User has insufficient credits"""
    def __init__(self, required: int, available: int):
        message = f"Insufficient credits. Required: {required}, Available: {available}"
        super().__init__(message, status.HTTP_402_PAYMENT_REQUIRED)


class RateLimitExceededError(BusinessLogicError):
    """Rate limit exceeded"""
    def __init__(self, retry_after: int = None):
        message = "Rate limit exceeded. Please try again later."
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)
        self.retry_after = retry_after


class UnauthorizedError(BusinessLogicError):
    """Unauthorized access"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(BusinessLogicError):
    """Forbidden access"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """Handle business logic errors"""
    
    request_id = request.state.__dict__.get("request_id", "unknown")
    
    logger.warning(
        f"Business logic error: {exc.message} | "
        f"Path: {request.url.path} | "
        f"Request ID: {request_id}"
    )
    
    error_response = ErrorResponse(
        status_code=exc.status_code,
        error_type=type(exc).__name__,
        message=exc.message,
        request_id=request_id
    )
    
    response = JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )
    
    if isinstance(exc, RateLimitExceededError) and exc.retry_after:
        response.headers["Retry-After"] = str(exc.retry_after)
    
    return response


def register_all_handlers(app):
    """Register all exception handlers including custom business logic handlers"""
    
    register_exception_handlers(app)
    
    app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)
    
    logger.info("All exception handlers registered successfully")
