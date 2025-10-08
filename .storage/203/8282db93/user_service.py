"""
User Service for Routix Platform
Handles user registration, authentication, credit management, and analytics
"""
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import bcrypt
import jwt
from app.core.config import settings
from app.services.redis_service import redis_service

class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"
    MODERATOR = "moderator"

class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class TransactionType(str, Enum):
    """Credit transaction type enumeration"""
    PURCHASE = "purchase"
    DEDUCTION = "deduction"
    REFUND = "refund"
    BONUS = "bonus"
    ADMIN_ADJUSTMENT = "admin_adjustment"

class UserServiceError(Exception):
    """Custom exception for user service errors"""
    pass

class UserService:
    """Comprehensive user management service"""
    
    def __init__(self):
        # Authentication configuration
        self.password_min_length = 8
        self.token_expire_hours = 24
        self.refresh_token_expire_days = 30
        
        # Credit system configuration
        self.free_tier_credits = 10
        self.basic_tier_credits = 100
        self.pro_tier_credits = 500
        self.enterprise_tier_credits = 2000
        
        # Rate limiting
        self.login_attempts_limit = 5
        self.login_lockout_minutes = 15
        
        # Cache configuration
        self.user_cache_ttl = 3600  # 1 hour
        self.session_cache_ttl = 86400  # 24 hours
        
    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        referral_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password
            full_name: Optional full name
            referral_code: Optional referral code
            
        Returns:
            User registration data with tokens
        """
        try:
            print(f"[{datetime.utcnow()}] Registering user: {username}")
            
            # Validate input
            await self._validate_registration_data(username, email, password)
            
            # Check if user already exists
            if await self._user_exists(username, email):
                raise UserServiceError("User with this username or email already exists")
            
            # Generate user ID
            user_id = self._generate_user_id()
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Create user data
            user_data = {
                "id": user_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name or "",
                "role": UserRole.USER,
                "subscription_tier": SubscriptionTier.FREE,
                "is_active": True,
                "is_verified": False,
                "credits": self.free_tier_credits,
                "total_credits_purchased": 0,
                "total_credits_used": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None,
                "login_count": 0,
                "profile": {
                    "avatar_url": None,
                    "bio": "",
                    "website": "",
                    "location": "",
                    "preferences": {
                        "email_notifications": True,
                        "marketing_emails": False,
                        "theme": "light"
                    }
                },
                "limits": {
                    "daily_generations": 10,
                    "monthly_generations": 100,
                    "max_templates": 50
                },
                "usage_stats": {
                    "total_generations": 0,
                    "total_templates": 0,
                    "total_conversations": 0
                }
            }
            
            # Handle referral
            if referral_code:
                referrer_bonus = await self._process_referral(referral_code, user_id)
                if referrer_bonus:
                    user_data["credits"] += 5  # Bonus for new user
                    user_data["referral_bonus"] = 5
            
            # Store user data
            await self._store_user_data(user_id, user_data)
            
            # Generate tokens
            access_token = self._generate_access_token(user_data)
            refresh_token = self._generate_refresh_token(user_id)
            
            # Store refresh token
            await self._store_refresh_token(user_id, refresh_token)
            
            # Send verification email (mock)
            verification_token = await self._create_verification_token(user_id)
            
            # Track registration
            await self._track_user_event(user_id, "registered", {"referral_code": referral_code})
            
            # Initial credit transaction
            await self._log_credit_transaction(
                user_id, self.free_tier_credits, TransactionType.BONUS, "Welcome bonus"
            )
            
            print(f"[{datetime.utcnow()}] User registered successfully: {user_id}")
            
            return {
                "user": self._sanitize_user_data(user_data),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "verification_token": verification_token,
                "message": "Registration successful. Please verify your email."
            }
            
        except Exception as e:
            print(f"User registration failed: {e}")
            raise UserServiceError(f"Registration failed: {str(e)}")
    
    async def login_user(
        self,
        username_or_email: str,
        password: str,
        remember_me: bool = False
    ) -> Dict[str, Any]:
        """
        Authenticate user login
        
        Args:
            username_or_email: Username or email
            password: Plain text password
            remember_me: Whether to extend token lifetime
            
        Returns:
            User data with authentication tokens
        """
        try:
            print(f"[{datetime.utcnow()}] Login attempt for: {username_or_email}")
            
            # Check rate limiting
            await self._check_login_rate_limit(username_or_email)
            
            # Find user
            user_data = await self._find_user_by_username_or_email(username_or_email)
            
            if not user_data:
                await self._record_failed_login(username_or_email)
                raise UserServiceError("Invalid username/email or password")
            
            # Verify password
            if not self._verify_password(password, user_data["password_hash"]):
                await self._record_failed_login(username_or_email)
                raise UserServiceError("Invalid username/email or password")
            
            # Check if user is active
            if not user_data.get("is_active", True):
                raise UserServiceError("Account is deactivated")
            
            # Update login statistics
            user_data["last_login"] = datetime.utcnow().isoformat()
            user_data["login_count"] = user_data.get("login_count", 0) + 1
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Store updated user data
            await self._store_user_data(user_data["id"], user_data)
            
            # Generate tokens
            token_lifetime = 7 * 24 if remember_me else 24  # 7 days or 24 hours
            access_token = self._generate_access_token(user_data, token_lifetime)
            refresh_token = self._generate_refresh_token(user_data["id"])
            
            # Store refresh token
            await self._store_refresh_token(user_data["id"], refresh_token)
            
            # Clear failed login attempts
            await self._clear_failed_logins(username_or_email)
            
            # Track login
            await self._track_user_event(user_data["id"], "logged_in", {"remember_me": remember_me})
            
            print(f"[{datetime.utcnow()}] User logged in successfully: {user_data['id']}")
            
            return {
                "user": self._sanitize_user_data(user_data),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "message": "Login successful"
            }
            
        except Exception as e:
            print(f"User login failed: {e}")
            raise UserServiceError(f"Login failed: {str(e)}")
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile data
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data
        """
        try:
            user_data = await self._get_user_data(user_id)
            
            if not user_data:
                raise UserServiceError(f"User not found: {user_id}")
            
            # Get additional profile data
            profile_data = self._sanitize_user_data(user_data)
            
            # Add computed fields
            profile_data["account_age_days"] = self._calculate_account_age(user_data["created_at"])
            profile_data["credit_usage_percentage"] = self._calculate_credit_usage_percentage(user_data)
            profile_data["tier_benefits"] = self._get_tier_benefits(user_data["subscription_tier"])
            
            return profile_data
            
        except Exception as e:
            print(f"Failed to get user profile {user_id}: {e}")
            raise UserServiceError(f"Failed to get profile: {str(e)}")
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            updates: Fields to update
            
        Returns:
            Updated user profile
        """
        try:
            user_data = await self._get_user_data(user_id)
            
            if not user_data:
                raise UserServiceError(f"User not found: {user_id}")
            
            # Validate and apply updates
            allowed_fields = [
                "full_name", "email", "profile.avatar_url", "profile.bio", 
                "profile.website", "profile.location", "profile.preferences"
            ]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    if "." in field:
                        # Nested field update
                        parent, child = field.split(".", 1)
                        if parent not in user_data:
                            user_data[parent] = {}
                        if "." in child:
                            # Handle deeper nesting
                            parts = child.split(".")
                            current = user_data[parent]
                            for part in parts[:-1]:
                                if part not in current:
                                    current[part] = {}
                                current = current[part]
                            current[parts[-1]] = value
                        else:
                            user_data[parent][child] = value
                    else:
                        user_data[field] = value
            
            # Special handling for email updates
            if "email" in updates:
                await self._validate_email_update(user_id, updates["email"])
                user_data["is_verified"] = False  # Re-verify email
            
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Store updated data
            await self._store_user_data(user_id, user_data)
            
            # Track profile update
            await self._track_user_event(user_id, "profile_updated", {"fields": list(updates.keys())})
            
            return self._sanitize_user_data(user_data)
            
        except Exception as e:
            print(f"Failed to update user profile {user_id}: {e}")
            raise UserServiceError(f"Failed to update profile: {str(e)}")
    
    async def get_user_credits(self, user_id: str) -> Dict[str, Any]:
        """
        Get user credit information
        
        Args:
            user_id: User ID
            
        Returns:
            Credit balance and transaction history
        """
        try:
            user_data = await self._get_user_data(user_id)
            
            if not user_data:
                raise UserServiceError(f"User not found: {user_id}")
            
            # Get recent transactions
            transactions = await self._get_credit_transactions(user_id, 10)
            
            credit_info = {
                "user_id": user_id,
                "current_balance": user_data.get("credits", 0),
                "total_purchased": user_data.get("total_credits_purchased", 0),
                "total_used": user_data.get("total_credits_used", 0),
                "subscription_tier": user_data.get("subscription_tier", SubscriptionTier.FREE),
                "monthly_allowance": self._get_monthly_credit_allowance(user_data["subscription_tier"]),
                "recent_transactions": transactions,
                "next_refill": self._calculate_next_credit_refill(user_data)
            }
            
            return credit_info
            
        except Exception as e:
            print(f"Failed to get user credits {user_id}: {e}")
            raise UserServiceError(f"Failed to get credits: {str(e)}")
    
    async def purchase_credits(
        self,
        user_id: str,
        credit_amount: int,
        payment_method: str,
        payment_token: str
    ) -> Dict[str, Any]:
        """
        Process credit purchase
        
        Args:
            user_id: User ID
            credit_amount: Number of credits to purchase
            payment_method: Payment method (stripe, paypal, etc.)
            payment_token: Payment token from frontend
            
        Returns:
            Purchase result and updated credit balance
        """
        try:
            print(f"[{datetime.utcnow()}] Processing credit purchase for user {user_id}: {credit_amount} credits")
            
            user_data = await self._get_user_data(user_id)
            
            if not user_data:
                raise UserServiceError(f"User not found: {user_id}")
            
            # Validate credit amount
            if credit_amount <= 0 or credit_amount > 10000:
                raise UserServiceError("Invalid credit amount")
            
            # Calculate cost (mock pricing)
            cost_per_credit = 0.10  # $0.10 per credit
            total_cost = credit_amount * cost_per_credit
            
            # Process payment (mock implementation)
            payment_result = await self._process_payment(
                user_id, total_cost, payment_method, payment_token
            )
            
            if not payment_result["success"]:
                raise UserServiceError(f"Payment failed: {payment_result['error']}")
            
            # Update user credits
            user_data["credits"] = user_data.get("credits", 0) + credit_amount
            user_data["total_credits_purchased"] = user_data.get("total_credits_purchased", 0) + credit_amount
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Store updated data
            await self._store_user_data(user_id, user_data)
            
            # Log transaction
            await self._log_credit_transaction(
                user_id, 
                credit_amount, 
                TransactionType.PURCHASE,
                f"Credit purchase - {payment_method}",
                {
                    "payment_id": payment_result["payment_id"],
                    "amount_paid": total_cost,
                    "payment_method": payment_method
                }
            )
            
            # Track purchase
            await self._track_user_event(user_id, "credits_purchased", {
                "amount": credit_amount,
                "cost": total_cost,
                "payment_method": payment_method
            })
            
            print(f"[{datetime.utcnow()}] Credit purchase completed: {user_id}")
            
            return {
                "purchase_id": payment_result["payment_id"],
                "credits_purchased": credit_amount,
                "amount_paid": total_cost,
                "new_balance": user_data["credits"],
                "message": "Credits purchased successfully"
            }
            
        except Exception as e:
            print(f"Credit purchase failed for user {user_id}: {e}")
            raise UserServiceError(f"Credit purchase failed: {str(e)}")
    
    async def get_user_analytics(
        self,
        user_id: str,
        timeframe: str = "month"
    ) -> Dict[str, Any]:
        """
        Get user usage analytics
        
        Args:
            user_id: User ID
            timeframe: Analytics timeframe (day, week, month, year)
            
        Returns:
            User analytics data
        """
        try:
            user_data = await self._get_user_data(user_id)
            
            if not user_data:
                raise UserServiceError(f"User not found: {user_id}")
            
            # Get analytics data (mock implementation)
            analytics = {
                "user_id": user_id,
                "timeframe": timeframe,
                "period": self._get_analytics_period(timeframe),
                "summary": {
                    "total_generations": user_data.get("usage_stats", {}).get("total_generations", 0),
                    "total_templates": user_data.get("usage_stats", {}).get("total_templates", 0),
                    "total_conversations": user_data.get("usage_stats", {}).get("total_conversations", 0),
                    "credits_used": user_data.get("total_credits_used", 0),
                    "credits_remaining": user_data.get("credits", 0)
                },
                "trends": {
                    "daily_generations": [2, 5, 3, 8, 4, 6, 7],
                    "daily_credit_usage": [3, 7, 4, 12, 6, 9, 10],
                    "peak_usage_day": "Friday",
                    "average_session_duration": 25  # minutes
                },
                "top_activities": [
                    {"activity": "thumbnail_generation", "count": 45, "percentage": 60},
                    {"activity": "template_upload", "count": 20, "percentage": 27},
                    {"activity": "conversation_chat", "count": 10, "percentage": 13}
                ],
                "subscription_info": {
                    "current_tier": user_data.get("subscription_tier", SubscriptionTier.FREE),
                    "tier_usage_percentage": 75,
                    "upgrade_recommended": user_data.get("credits", 0) < 10
                }
            }
            
            return analytics
            
        except Exception as e:
            print(f"Failed to get user analytics {user_id}: {e}")
            raise UserServiceError(f"Failed to get analytics: {str(e)}")
    
    async def deduct_user_credits(
        self,
        user_id: str,
        amount: int,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deduct credits from user account
        
        Args:
            user_id: User ID
            amount: Credits to deduct
            reason: Reason for deduction
            metadata: Additional transaction metadata
            
        Returns:
            Deduction result and new balance
        """
        try:
            user_data = await self._get_user_data(user_id)
            
            if not user_data:
                raise UserServiceError(f"User not found: {user_id}")
            
            current_credits = user_data.get("credits", 0)
            
            if current_credits < amount:
                raise UserServiceError(f"Insufficient credits. Required: {amount}, Available: {current_credits}")
            
            # Deduct credits
            user_data["credits"] = current_credits - amount
            user_data["total_credits_used"] = user_data.get("total_credits_used", 0) + amount
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Store updated data
            await self._store_user_data(user_id, user_data)
            
            # Log transaction
            await self._log_credit_transaction(
                user_id, -amount, TransactionType.DEDUCTION, reason, metadata
            )
            
            return {
                "credits_deducted": amount,
                "new_balance": user_data["credits"],
                "reason": reason
            }
            
        except Exception as e:
            print(f"Credit deduction failed for user {user_id}: {e}")
            raise UserServiceError(f"Credit deduction failed: {str(e)}")
    
    # Private helper methods
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _generate_access_token(self, user_data: Dict[str, Any], hours: int = 24) -> str:
        """Generate JWT access token"""
        payload = {
            "sub": user_data["username"],
            "user_id": user_data["id"],
            "email": user_data["email"],
            "role": user_data["role"],
            "is_admin": user_data["role"] in [UserRole.ADMIN, UserRole.MODERATOR],
            "credits": user_data.get("credits", 0),
            "exp": datetime.utcnow() + timedelta(hours=hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    def _generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        return f"refresh_{user_id}_{secrets.token_urlsafe(32)}"
    
    async def _validate_registration_data(self, username: str, email: str, password: str) -> None:
        """Validate registration input data"""
        # Username validation
        if not username or len(username) < 3 or len(username) > 30:
            raise UserServiceError("Username must be 3-30 characters long")
        
        if not username.replace("_", "").replace("-", "").isalnum():
            raise UserServiceError("Username can only contain letters, numbers, hyphens, and underscores")
        
        # Email validation (basic)
        if not email or "@" not in email or "." not in email:
            raise UserServiceError("Invalid email address")
        
        # Password validation
        if not password or len(password) < self.password_min_length:
            raise UserServiceError(f"Password must be at least {self.password_min_length} characters long")
    
    async def _user_exists(self, username: str, email: str) -> bool:
        """Check if user already exists"""
        # Mock implementation - replace with actual database query
        existing_user = await redis_service.get(f"user:username:{username}")
        if existing_user:
            return True
        
        existing_email = await redis_service.get(f"user:email:{email}")
        return existing_email is not None
    
    async def _store_user_data(self, user_id: str, user_data: Dict[str, Any]) -> None:
        """Store user data in cache and database"""
        # Cache user data
        await redis_service.set(f"user:{user_id}", user_data, self.user_cache_ttl)
        
        # Index by username and email
        await redis_service.set(f"user:username:{user_data['username']}", user_id, self.user_cache_ttl)
        await redis_service.set(f"user:email:{user_data['email']}", user_id, self.user_cache_ttl)
    
    async def _get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from cache"""
        return await redis_service.get(f"user:{user_id}")
    
    async def _find_user_by_username_or_email(self, username_or_email: str) -> Optional[Dict[str, Any]]:
        """Find user by username or email"""
        # Try username first
        user_id = await redis_service.get(f"user:username:{username_or_email}")
        
        if not user_id:
            # Try email
            user_id = await redis_service.get(f"user:email:{username_or_email}")
        
        if user_id:
            return await self._get_user_data(user_id)
        
        return None
    
    def _sanitize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from user object"""
        sanitized = user_data.copy()
        sanitized.pop("password_hash", None)
        return sanitized
    
    async def _store_refresh_token(self, user_id: str, refresh_token: str) -> None:
        """Store refresh token"""
        await redis_service.set(
            f"refresh_token:{user_id}", 
            refresh_token, 
            self.refresh_token_expire_days * 24 * 3600
        )
    
    async def _log_credit_transaction(
        self,
        user_id: str,
        amount: int,
        transaction_type: TransactionType,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log credit transaction"""
        transaction = {
            "id": f"txn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}",
            "user_id": user_id,
            "amount": amount,
            "type": transaction_type,
            "description": description,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store transaction
        await redis_service.lpush(f"transactions:{user_id}", transaction)
        await redis_service.expire(f"transactions:{user_id}", 86400 * 90)  # 90 days
    
    async def _track_user_event(self, user_id: str, event: str, metadata: Dict[str, Any]) -> None:
        """Track user analytics event"""
        event_data = {
            "user_id": user_id,
            "event": event,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await redis_service.lpush(f"analytics:user:{user_id}", event_data)
        await redis_service.expire(f"analytics:user:{user_id}", 86400 * 30)  # 30 days
    
    async def _get_credit_transactions(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent credit transactions"""
        transactions = await redis_service.lrange(f"transactions:{user_id}", 0, limit - 1)
        return transactions or []
    
    def _calculate_account_age(self, created_at: str) -> int:
        """Calculate account age in days"""
        created = datetime.fromisoformat(created_at)
        return (datetime.utcnow() - created).days
    
    def _calculate_credit_usage_percentage(self, user_data: Dict[str, Any]) -> float:
        """Calculate credit usage percentage"""
        total_purchased = user_data.get("total_credits_purchased", 0)
        total_used = user_data.get("total_credits_used", 0)
        
        if total_purchased == 0:
            return 0.0
        
        return min(100.0, (total_used / total_purchased) * 100)
    
    def _get_tier_benefits(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get subscription tier benefits"""
        benefits = {
            SubscriptionTier.FREE: {
                "monthly_credits": 10,
                "max_templates": 5,
                "priority_support": False,
                "api_access": False
            },
            SubscriptionTier.BASIC: {
                "monthly_credits": 100,
                "max_templates": 50,
                "priority_support": False,
                "api_access": True
            },
            SubscriptionTier.PRO: {
                "monthly_credits": 500,
                "max_templates": 500,
                "priority_support": True,
                "api_access": True
            },
            SubscriptionTier.ENTERPRISE: {
                "monthly_credits": 2000,
                "max_templates": -1,  # Unlimited
                "priority_support": True,
                "api_access": True
            }
        }
        
        return benefits.get(tier, benefits[SubscriptionTier.FREE])
    
    async def _process_payment(
        self,
        user_id: str,
        amount: float,
        payment_method: str,
        payment_token: str
    ) -> Dict[str, Any]:
        """Process payment (mock implementation)"""
        # Mock payment processing
        payment_id = f"pay_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
        
        # Simulate payment success/failure
        success = True  # In real implementation, integrate with payment processor
        
        return {
            "success": success,
            "payment_id": payment_id,
            "amount": amount,
            "payment_method": payment_method,
            "error": None if success else "Payment processing failed"
        }
    
    def _get_monthly_credit_allowance(self, tier: SubscriptionTier) -> int:
        """Get monthly credit allowance for subscription tier"""
        allowances = {
            SubscriptionTier.FREE: 10,
            SubscriptionTier.BASIC: 100,
            SubscriptionTier.PRO: 500,
            SubscriptionTier.ENTERPRISE: 2000
        }
        return allowances.get(tier, 10)
    
    def _calculate_next_credit_refill(self, user_data: Dict[str, Any]) -> str:
        """Calculate next credit refill date"""
        # Mock implementation - first day of next month
        now = datetime.utcnow()
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        
        return next_month.isoformat()
    
    def _get_analytics_period(self, timeframe: str) -> Dict[str, str]:
        """Get analytics period dates"""
        now = datetime.utcnow()
        
        if timeframe == "day":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif timeframe == "week":
            start = now - timedelta(days=7)
        elif timeframe == "month":
            start = now - timedelta(days=30)
        else:  # year
            start = now - timedelta(days=365)
        
        return {
            "start": start.isoformat(),
            "end": now.isoformat()
        }
    
    async def _check_login_rate_limit(self, username_or_email: str) -> None:
        """Check login rate limiting"""
        key = f"login_attempts:{username_or_email}"
        attempts = await redis_service.get(key) or 0
        
        if attempts >= self.login_attempts_limit:
            raise UserServiceError(f"Too many login attempts. Try again in {self.login_lockout_minutes} minutes.")
    
    async def _record_failed_login(self, username_or_email: str) -> None:
        """Record failed login attempt"""
        key = f"login_attempts:{username_or_email}"
        await redis_service.incr(key)
        await redis_service.expire(key, self.login_lockout_minutes * 60)
    
    async def _clear_failed_logins(self, username_or_email: str) -> None:
        """Clear failed login attempts"""
        key = f"login_attempts:{username_or_email}"
        await redis_service.delete(key)
    
    async def _create_verification_token(self, user_id: str) -> str:
        """Create email verification token"""
        token = secrets.token_urlsafe(32)
        await redis_service.set(f"verify:{token}", user_id, 86400)  # 24 hours
        return token
    
    async def _validate_email_update(self, user_id: str, new_email: str) -> None:
        """Validate email update"""
        # Check if email is already taken
        existing_user_id = await redis_service.get(f"user:email:{new_email}")
        if existing_user_id and existing_user_id != user_id:
            raise UserServiceError("Email address is already in use")
    
    async def _process_referral(self, referral_code: str, new_user_id: str) -> bool:
        """Process referral bonus"""
        # Mock referral processing
        referrer_id = await redis_service.get(f"referral:{referral_code}")
        
        if referrer_id:
            # Give bonus to referrer
            referrer_data = await self._get_user_data(referrer_id)
            if referrer_data:
                referrer_data["credits"] = referrer_data.get("credits", 0) + 10
                await self._store_user_data(referrer_id, referrer_data)
                
                # Log referral transaction
                await self._log_credit_transaction(
                    referrer_id, 10, TransactionType.BONUS, f"Referral bonus for {new_user_id}"
                )
                
                return True
        
        return False

# Global user service instance
user_service = UserService()