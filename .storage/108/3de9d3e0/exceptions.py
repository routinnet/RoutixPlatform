"""
Routix Platform Custom Exceptions
Application-specific exception classes
"""

from typing import Any, Dict, Optional


class RouxixException(Exception):
    """Base exception for Routix Platform"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "ROUTIX_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(RouxixException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(RouxixException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ValidationError(RouxixException):
    """Input validation errors"""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
            
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=error_details
        )


class NotFoundError(RouxixException):
    """Resource not found errors"""
    
    def __init__(self, resource: str, identifier: str = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} not found"
        if identifier:
            message += f" (ID: {identifier})"
            
        error_details = details or {}
        error_details["resource"] = resource
        if identifier:
            error_details["identifier"] = identifier
            
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND_ERROR",
            details=error_details
        )


class ConflictError(RouxixException):
    """Resource conflict errors"""
    
    def __init__(self, message: str, resource: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if resource:
            error_details["resource"] = resource
            
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR",
            details=error_details
        )


class InsufficientCreditsError(RouxixException):
    """Insufficient credits for operation"""
    
    def __init__(self, required: int, available: int, details: Optional[Dict[str, Any]] = None):
        message = f"Insufficient credits. Required: {required}, Available: {available}"
        error_details = details or {}
        error_details.update({
            "required_credits": required,
            "available_credits": available
        })
        
        super().__init__(
            message=message,
            status_code=402,
            error_code="INSUFFICIENT_CREDITS",
            details=error_details
        )


class RateLimitError(RouxixException):
    """Rate limit exceeded errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details=error_details
        )


class AIServiceError(RouxixException):
    """AI service integration errors"""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        error_details["service"] = service
        
        super().__init__(
            message=f"{service} error: {message}",
            status_code=503,
            error_code="AI_SERVICE_ERROR",
            details=error_details
        )


class FileUploadError(RouxixException):
    """File upload related errors"""
    
    def __init__(self, message: str, filename: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if filename:
            error_details["filename"] = filename
            
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            details=error_details
        )


class GenerationError(RouxixException):
    """Thumbnail generation errors"""
    
    def __init__(self, message: str, generation_id: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if generation_id:
            error_details["generation_id"] = generation_id
            
        super().__init__(
            message=message,
            status_code=500,
            error_code="GENERATION_ERROR",
            details=error_details
        )


class TemplateAnalysisError(RouxixException):
    """Template analysis errors"""
    
    def __init__(self, message: str, template_id: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if template_id:
            error_details["template_id"] = template_id
            
        super().__init__(
            message=message,
            status_code=500,
            error_code="TEMPLATE_ANALYSIS_ERROR",
            details=error_details
        )


class WebSocketError(RouxixException):
    """WebSocket related errors"""
    
    def __init__(self, message: str, connection_id: str = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if connection_id:
            error_details["connection_id"] = connection_id
            
        super().__init__(
            message=message,
            status_code=500,
            error_code="WEBSOCKET_ERROR",
            details=error_details
        )