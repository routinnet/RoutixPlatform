"""
User management endpoints
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from app.services.user_service import user_service, UserServiceError, UserRole, SubscriptionTier
from app.core.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()

class UserRegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    referral_code: Optional[str] = None

class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str
    remember_me: bool = False

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class CreditPurchaseRequest(BaseModel):
    credit_amount: int
    payment_method: str
    payment_token: str

@router.post("/register", response_model=Dict[str, Any])
async def register_user(request: UserRegistrationRequest):
    """
    Register a new user account
    """
    try:
        result = await user_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            referral_code=request.referral_code
        )
        
        return {
            "success": True,
            "data": result,
            "message": "User registered successfully"
        }
        
    except UserServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Dict[str, Any])
async def login_user(request: UserLoginRequest):
    """
    Authenticate user login
    """
    try:
        result = await user_service.login_user(
            username_or_email=request.username_or_email,
            password=request.password,
            remember_me=request.remember_me
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Login successful"
        }
        
    except UserServiceError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    try:
        profile_data = await user_service.get_user_profile(current_user.id)
        
        return {
            "success": True,
            "data": profile_data,
            "message": "Profile retrieved successfully"
        }
        
    except UserServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile
    """
    try:
        # Convert to dict and remove None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updated_profile = await user_service.update_user_profile(
            user_id=current_user.id,
            updates=updates
        )
        
        return {
            "success": True,
            "data": updated_profile,
            "message": "Profile updated successfully"
        }
        
    except UserServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

@router.get("/credits", response_model=Dict[str, Any])
async def get_user_credits(current_user: User = Depends(get_current_user)):
    """
    Get user credit balance and transaction history
    """
    try:
        credit_info = await user_service.get_user_credits(current_user.id)
        
        return {
            "success": True,
            "data": credit_info,
            "message": "Credit information retrieved successfully"
        }
        
    except UserServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get credits: {str(e)}")

@router.post("/credits/purchase", response_model=Dict[str, Any])
async def purchase_credits(
    request: CreditPurchaseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Purchase credits
    """
    try:
        result = await user_service.purchase_credits(
            user_id=current_user.id,
            credit_amount=request.credit_amount,
            payment_method=request.payment_method,
            payment_token=request.payment_token
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Credits purchased successfully"
        }
        
    except UserServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Credit purchase failed: {str(e)}")

@router.get("/analytics", response_model=Dict[str, Any])
async def get_user_analytics(
    timeframe: str = Query("month", regex="^(day|week|month|year)$", description="Analytics timeframe"),
    current_user: User = Depends(get_current_user)
):
    """
    Get user usage analytics
    """
    try:
        analytics_data = await user_service.get_user_analytics(
            user_id=current_user.id,
            timeframe=timeframe
        )
        
        return {
            "success": True,
            "data": analytics_data,
            "message": "Analytics retrieved successfully"
        }
        
    except UserServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/logout", response_model=Dict[str, Any])
async def logout_user(current_user: User = Depends(get_current_user)):
    """
    Logout user (invalidate tokens)
    """
    try:
        # In a real implementation, you would invalidate the JWT token
        # For now, we'll just return success
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.post("/verify-email", response_model=Dict[str, Any])
async def verify_email(
    token: str = Query(..., description="Email verification token")
):
    """
    Verify user email address
    """
    try:
        # Mock email verification (implement with actual token validation)
        from app.services.redis_service import redis_service
        
        user_id = await redis_service.get(f"verify:{token}")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # Update user verification status
        user_data = await user_service._get_user_data(user_id)
        if user_data:
            user_data["is_verified"] = True
            user_data["updated_at"] = datetime.utcnow().isoformat()
            await user_service._store_user_data(user_id, user_data)
            
            # Remove verification token
            await redis_service.delete(f"verify:{token}")
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email verification failed: {str(e)}")

@router.post("/password-reset/request", response_model=Dict[str, Any])
async def request_password_reset(email: EmailStr):
    """
    Request password reset
    """
    try:
        # Mock password reset request
        from app.services.redis_service import redis_service
        import secrets
        
        # Check if user exists
        user_id = await redis_service.get(f"user:email:{email}")
        
        if user_id:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            await redis_service.set(f"reset:{reset_token}", user_id, 3600)  # 1 hour
            
            # In real implementation, send email with reset link
            print(f"Password reset token for {email}: {reset_token}")
        
        # Always return success to prevent email enumeration
        return {
            "success": True,
            "message": "If the email exists, a password reset link has been sent"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset request failed: {str(e)}")

@router.post("/password-reset/confirm", response_model=Dict[str, Any])
async def confirm_password_reset(
    token: str,
    new_password: str
):
    """
    Confirm password reset with new password
    """
    try:
        from app.services.redis_service import redis_service
        
        # Validate reset token
        user_id = await redis_service.get(f"reset:{token}")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Update password
        user_data = await user_service._get_user_data(user_id)
        if user_data:
            user_data["password_hash"] = user_service._hash_password(new_password)
            user_data["updated_at"] = datetime.utcnow().isoformat()
            await user_service._store_user_data(user_id, user_data)
            
            # Remove reset token
            await redis_service.delete(f"reset:{token}")
            
            # Track password reset
            await user_service._track_user_event(user_id, "password_reset", {})
            
            return {
                "success": True,
                "message": "Password reset successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

@router.get("/subscription/tiers", response_model=Dict[str, Any])
async def get_subscription_tiers():
    """
    Get available subscription tiers and pricing
    """
    try:
        tiers = {
            "free": {
                "name": "Free",
                "price": 0,
                "monthly_credits": 10,
                "max_templates": 5,
                "features": ["Basic generation", "Community support"]
            },
            "basic": {
                "name": "Basic",
                "price": 9.99,
                "monthly_credits": 100,
                "max_templates": 50,
                "features": ["API access", "Priority generation", "Email support"]
            },
            "pro": {
                "name": "Pro",
                "price": 29.99,
                "monthly_credits": 500,
                "max_templates": 500,
                "features": ["Advanced AI features", "Priority support", "Custom templates"]
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 99.99,
                "monthly_credits": 2000,
                "max_templates": -1,
                "features": ["Unlimited templates", "Dedicated support", "Custom integrations"]
            }
        }
        
        return {
            "success": True,
            "data": {"tiers": tiers},
            "message": "Subscription tiers retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription tiers: {str(e)}")

@router.post("/subscription/upgrade", response_model=Dict[str, Any])
async def upgrade_subscription(
    tier: SubscriptionTier,
    payment_token: str,
    current_user: User = Depends(get_current_user)
):
    """
    Upgrade user subscription tier
    """
    try:
        # Mock subscription upgrade
        user_data = await user_service._get_user_data(current_user.id)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update subscription tier
        user_data["subscription_tier"] = tier
        user_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Add monthly credits based on tier
        monthly_credits = user_service._get_monthly_credit_allowance(tier)
        user_data["credits"] = user_data.get("credits", 0) + monthly_credits
        
        await user_service._store_user_data(current_user.id, user_data)
        
        # Track subscription upgrade
        await user_service._track_user_event(current_user.id, "subscription_upgraded", {
            "new_tier": tier,
            "credits_added": monthly_credits
        })
        
        return {
            "success": True,
            "data": {
                "new_tier": tier,
                "credits_added": monthly_credits,
                "new_balance": user_data["credits"]
            },
            "message": "Subscription upgraded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subscription upgrade failed: {str(e)}")

@router.get("/admin/users", response_model=Dict[str, Any])
async def get_all_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    role_filter: Optional[UserRole] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Get all users (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Mock admin user listing
        users = []
        
        for i in range(limit):
            user_id = f"user_admin_mock_{i + offset}"
            users.append({
                "id": user_id,
                "username": f"user_{i + offset}",
                "email": f"user{i + offset}@example.com",
                "role": UserRole.USER,
                "subscription_tier": SubscriptionTier.FREE,
                "is_active": True,
                "is_verified": True,
                "credits": 10 + (i * 5),
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            })
        
        # Apply filters
        if role_filter:
            users = [u for u in users if u["role"] == role_filter]
        
        if search:
            users = [u for u in users if search.lower() in u["username"].lower() or search.lower() in u["email"].lower()]
        
        return {
            "success": True,
            "data": {
                "users": users,
                "pagination": {
                    "total": len(users),
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(users) == limit
                }
            },
            "message": "Users retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@router.put("/admin/users/{user_id}/role", response_model=Dict[str, Any])
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(get_current_user)
):
    """
    Update user role (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get target user
        target_user = await user_service._get_user_data(user_id)
        
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update role
        target_user["role"] = new_role
        target_user["updated_at"] = datetime.utcnow().isoformat()
        
        await user_service._store_user_data(user_id, target_user)
        
        # Track role change
        await user_service._track_user_event(user_id, "role_updated", {
            "new_role": new_role,
            "updated_by": current_user.id
        })
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "new_role": new_role
            },
            "message": "User role updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Role update failed: {str(e)}")