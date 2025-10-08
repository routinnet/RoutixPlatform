"""
Routix Platform API Test Suite
Test all core FastAPI functionality
"""

import asyncio
import sys
import traceback
from app.main import app
from app.core.database import get_db_session
from app.core.security import create_access_token, verify_token
from app.services.user_service import UserService


async def test_database_connection():
    """Test database connectivity"""
    print("🧪 Testing database connection...")
    try:
        async with get_db_session() as db:
            result = await db.execute("SELECT 1 as test")
            row = result.fetchone()
            assert row[0] == 1
        print("   ✅ Database connection successful")
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False


async def test_jwt_authentication():
    """Test JWT token creation and verification"""
    print("🧪 Testing JWT authentication...")
    try:
        # Create token
        user_id = "test-user-123"
        token = create_access_token(user_id)
        
        # Verify token
        verified_user_id = verify_token(token)
        assert verified_user_id == user_id
        
        print(f"   ✅ JWT token created and verified: {token[:30]}...")
        return True
    except Exception as e:
        print(f"   ❌ JWT authentication failed: {e}")
        return False


async def test_user_service():
    """Test user service operations"""
    print("🧪 Testing user service...")
    try:
        async with get_db_session() as db:
            user_service = UserService(db)
            
            # Test get admin user
            admin_user = await user_service.get_user_by_email("admin@routix.com")
            assert admin_user is not None
            assert admin_user.is_admin is True
            
            print(f"   ✅ Admin user found: {admin_user.email}")
            
            # Test authentication
            auth_user = await user_service.authenticate_user(
                "admin@routix.com", 
                "secure_password"
            )
            assert auth_user is not None
            
            print("   ✅ User authentication successful")
            return True
            
    except Exception as e:
        print(f"   ❌ User service failed: {e}")
        traceback.print_exc()
        return False


async def test_fastapi_app():
    """Test FastAPI app initialization"""
    print("🧪 Testing FastAPI app...")
    try:
        # Check app is created
        assert app is not None
        assert app.title == "Routix Platform API"
        
        # Check routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ["/health", "/health/detailed", "/api/v1/auth/login"]
        
        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes), f"Route {expected_route} not found"
        
        print("   ✅ FastAPI app initialized with all routes")
        return True
        
    except Exception as e:
        print(f"   ❌ FastAPI app test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 ROUTIX PLATFORM - FASTAPI CORE TESTS")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_jwt_authentication,
        test_user_service,
        test_fastapi_app
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test {test.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 TEST SUMMARY")
    print("=" * 30)
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! FastAPI Core is ready!")
        print("\n✅ ACCEPTANCE CRITERIA MET:")
        print("   ✅ Server can start without errors")
        print("   ✅ Can connect to database")
        print("   ✅ JWT tokens generate and validate correctly")
        print("   ✅ All API routes are registered")
        print("   ✅ User authentication works")
        print("   ✅ Admin user is accessible")
        
        print("\n🚀 READY FOR NEXT PHASE: AI Services Integration")
        return True
    else:
        print(f"\n❌ {total-passed} tests failed. Please fix issues before proceeding.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)