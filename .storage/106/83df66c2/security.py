"""
Routix Platform Security
JWT authentication, password hashing, and security utilities
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Request

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

# JWT settings
ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta = None,
    additional_claims: dict = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify JWT token and return subject"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            return None
            
        # Get subject (user ID)
        subject: str = payload.get("sub")
        if subject is None:
            return None
            
        return subject
        
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def generate_api_key() -> str:
    """Generate a secure API key"""
    import secrets
    return f"rk_{secrets.token_urlsafe(32)}"


class JWTBearer(HTTPBearer):
    """Custom JWT Bearer authentication"""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            
            user_id = verify_token(credentials.credentials)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            
            return user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )


# Global JWT bearer instance
jwt_bearer = JWTBearer()


def create_password_reset_token(email: str) -> str:
    """Create password reset token"""
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email"""
    return verify_token(token, token_type="password_reset")


def create_email_verification_token(email: str) -> str:
    """Create email verification token"""
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify email verification token and return email"""
    return verify_token(token, token_type="email_verification")


# Rate limiting utilities
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self._requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is allowed within rate limit"""
        now = datetime.utcnow()
        
        if key not in self._requests:
            self._requests[key] = []
        
        # Remove old requests outside window
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if (now - req_time).seconds < window
        ]
        
        # Check if under limit
        if len(self._requests[key]) < limit:
            self._requests[key].append(now)
            return True
        
        return False


# Global rate limiter
rate_limiter = RateLimiter()