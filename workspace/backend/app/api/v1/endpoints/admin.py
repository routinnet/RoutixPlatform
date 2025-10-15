"""
Admin Panel Endpoints
Dashboard, analytics, system management
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.core.dependencies import get_db, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get admin dashboard data with overview statistics
    """
    try:
        # Mock dashboard data
        dashboard_data = {
            "overview": {
                "total_users": 1247,
                "active_users_today": 342,
                "total_generations": 45678,
                "generations_today": 892,
                "total_revenue": 12450.50,
                "revenue_today": 234.50,
                "system_health": "excellent",
                "uptime_percentage": 99.97
            },
            "user_stats": {
                "new_users_today": 23,
                "new_users_this_week": 145,
                "new_users_this_month": 567,
                "user_growth_rate": 12.5,
                "churn_rate": 3.2,
                "average_session_duration": 1834  # seconds
            },
            "generation_stats": {
                "success_rate": 97.2,
                "average_generation_time": 48,  # seconds
                "total_credits_consumed": 52341,
                "peak_hour": 14,
                "most_popular_algorithm": "routix_v6",
                "queue_length": 12
            },
            "revenue_stats": {
                "total_subscriptions": 489,
                "free_tier_users": 758,
                "basic_tier_users": 234,
                "pro_tier_users": 198,
                "enterprise_tier_users": 57,
                "mrr": 8945.50,
                "arr": 107346.00
            },
            "recent_activity": [
                {
                    "id": "act_1",
                    "type": "user_registered",
                    "user_id": "usr_123",
                    "username": "john_doe",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                    "details": "New user registration"
                },
                {
                    "id": "act_2",
                    "type": "generation_completed",
                    "user_id": "usr_456",
                    "username": "jane_smith",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=8)).isoformat(),
                    "details": "Generated thumbnail with Routix V6"
                },
                {
                    "id": "act_3",
                    "type": "subscription_upgraded",
                    "user_id": "usr_789",
                    "username": "bob_wilson",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                    "details": "Upgraded from Basic to Pro tier"
                }
            ],
            "system_alerts": [
                {
                    "id": "alert_1",
                    "severity": "info",
                    "message": "System performance is optimal",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
        }
        
        return {
            "success": True,
            "data": dashboard_data,
            "message": "Dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(
    timeframe: str = Query("week", pattern="^(day|week|month|year|all)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed system statistics
    """
    try:
        # Mock system stats
        stats = {
            "timeframe": timeframe,
            "performance": {
                "api_response_time": {
                    "average": 145,  # ms
                    "p50": 120,
                    "p95": 280,
                    "p99": 450
                },
                "database_query_time": {
                    "average": 45,  # ms
                    "p50": 35,
                    "p95": 85,
                    "p99": 120
                },
                "cache_hit_rate": 87.5,
                "error_rate": 0.8,
                "throughput": 1234  # requests per minute
            },
            "infrastructure": {
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "disk_usage": 38.5,
                "network_in": 1234567,  # bytes per second
                "network_out": 9876543,
                "redis_memory": 256,  # MB
                "database_size": 2048  # MB
            },
            "usage": {
                "total_api_calls": 234567,
                "total_generations": 45678,
                "total_templates_uploaded": 892,
                "total_conversations": 3421,
                "total_messages": 18945,
                "bandwidth_used": 52.3  # GB
            },
            "errors": {
                "total_errors": 234,
                "4xx_errors": 189,
                "5xx_errors": 45,
                "top_errors": [
                    {"code": 404, "count": 123, "message": "Not Found"},
                    {"code": 401, "count": 66, "message": "Unauthorized"},
                    {"code": 500, "count": 28, "message": "Internal Server Error"}
                ]
            }
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "System stats retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    metric: str = Query("all", description="Specific metric to fetch"),
    timeframe: str = Query("week", pattern="^(day|week|month|year|all)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed analytics data
    """
    try:
        # Mock analytics data
        analytics = {
            "timeframe": timeframe,
            "metric": metric,
            "user_analytics": {
                "daily_active_users": [312, 345, 378, 402, 389, 421, 456],
                "new_registrations": [23, 28, 31, 19, 25, 27, 34],
                "user_retention": {
                    "day_1": 78.5,
                    "day_7": 56.2,
                    "day_30": 42.8
                },
                "geographic_distribution": {
                    "US": 45.2,
                    "UK": 12.8,
                    "Canada": 8.5,
                    "Germany": 6.7,
                    "Other": 26.8
                }
            },
            "generation_analytics": {
                "daily_generations": [812, 845, 902, 878, 923, 956, 892],
                "success_rate_trend": [95.2, 96.1, 97.2, 96.8, 97.5, 97.8, 97.2],
                "algorithm_usage": {
                    "routix_v6": 48.5,
                    "routix_v5": 28.3,
                    "routix_v7_anime": 15.2,
                    "routix_v4": 8.0
                },
                "template_categories": {
                    "gaming": 32.5,
                    "tech": 25.8,
                    "cooking": 18.2,
                    "vlog": 12.5,
                    "other": 11.0
                }
            },
            "revenue_analytics": {
                "daily_revenue": [234.50, 289.20, 312.45, 278.90, 301.25, 334.80, 289.75],
                "subscription_distribution": {
                    "free": 60.8,
                    "basic": 18.8,
                    "pro": 15.9,
                    "enterprise": 4.5
                },
                "ltv_by_tier": {
                    "free": 0,
                    "basic": 119.88,
                    "pro": 359.88,
                    "enterprise": 1199.88
                },
                "churn_by_tier": {
                    "basic": 5.2,
                    "pro": 3.8,
                    "enterprise": 1.2
                }
            }
        }
        
        return {
            "success": True,
            "data": analytics,
            "message": "Analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/activity", response_model=Dict[str, Any])
async def get_recent_activity(
    limit: int = Query(50, ge=1, le=200),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get recent system activity logs
    """
    try:
        # Mock activity data
        activities = []
        activity_types = [
            "user_registered", "user_login", "generation_created", 
            "generation_completed", "subscription_upgraded", "template_uploaded",
            "credit_purchased", "password_reset"
        ]
        
        for i in range(limit):
            activities.append({
                "id": f"act_{i}",
                "type": activity_types[i % len(activity_types)],
                "user_id": f"usr_{i}",
                "username": f"user_{i}",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=i*5)).isoformat(),
                "details": f"Activity details for {activity_types[i % len(activity_types)]}",
                "ip_address": f"192.168.1.{i % 255}",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            })
        
        # Filter by type if specified
        if activity_type:
            activities = [a for a in activities if a["type"] == activity_type]
        
        return {
            "success": True,
            "data": {
                "activities": activities,
                "total": len(activities),
                "limit": limit
            },
            "message": "Activity log retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity log: {str(e)}")


@router.get("/users", response_model=Dict[str, Any])
async def get_all_users_admin(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search users"),
    tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all users with admin view (detailed information)
    """
    try:
        # Mock user data
        users = []
        
        for i in range(offset, offset + limit):
            users.append({
                "id": f"usr_{i}",
                "username": f"user_{i}",
                "email": f"user{i}@example.com",
                "full_name": f"User {i}",
                "subscription_tier": ["free", "basic", "pro", "enterprise"][i % 4],
                "credits": 10 + (i * 5),
                "total_generations": i * 10,
                "is_active": True,
                "is_verified": i % 10 != 0,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                "last_login": (datetime.now(timezone.utc) - timedelta(hours=i % 24)).isoformat(),
                "total_spent": round(i * 1.5, 2),
                "referral_code": f"REF{i:04d}"
            })
        
        # Apply filters
        if search:
            users = [u for u in users if search.lower() in u["username"].lower() or search.lower() in u["email"].lower()]
        
        if tier:
            users = [u for u in users if u["subscription_tier"] == tier]
        
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


@router.post("/broadcast", response_model=Dict[str, Any])
async def broadcast_message(
    message: str = Query(..., description="Message to broadcast"),
    target: str = Query("all", pattern="^(all|free|basic|pro|enterprise)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Broadcast message to users
    """
    try:
        # Mock broadcast
        target_users = {
            "all": 1247,
            "free": 758,
            "basic": 234,
            "pro": 198,
            "enterprise": 57
        }
        
        return {
            "success": True,
            "data": {
                "message": message,
                "target": target,
                "recipients": target_users.get(target, 0),
                "sent_at": datetime.now(timezone.utc).isoformat()
            },
            "message": "Broadcast sent successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send broadcast: {str(e)}")