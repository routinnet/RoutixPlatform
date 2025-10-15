"""
Pytest Configuration and Fixtures for Routix Platform Tests
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_async_session
from app.core.config import settings


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
def test_client(test_session: AsyncSession) -> TestClient:
    """Create a test client with overridden dependencies"""
    
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session
    
    app.dependency_overrides[get_async_session] = override_get_session
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_test_client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for testing async endpoints"""
    
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session
    
    app.dependency_overrides[get_async_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def test_admin_data():
    """Sample admin user data for testing"""
    return {
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "AdminPassword123!",
        "full_name": "Admin User",
        "role": "admin"
    }


@pytest.fixture
def test_template_data():
    """Sample template data for testing"""
    return {
        "image_url": "https://example.com/test-template.jpg",
        "thumbnail_url": "https://example.com/test-template-thumb.jpg",
        "category": "gaming",
        "description": "Test gaming thumbnail",
        "has_face": True,
        "has_text": True,
        "has_logo": True,
        "energy_level": 8,
        "tags": '["gaming", "test"]',
        "style_dna": {
            "color_analysis": {
                "primary_colors": ["#FF0000", "#000000"],
                "color_temperature": "warm",
                "contrast_level": "high"
            },
            "style_characteristics": {
                "design_style": "modern",
                "energy_level": 8,
                "mood": "exciting"
            }
        }
    }


@pytest.fixture
def test_generation_request_data():
    """Sample generation request data for testing"""
    return {
        "prompt": "Create an epic gaming thumbnail",
        "category": "gaming",
        "custom_text": "EPIC GAMEPLAY",
        "style_preferences": {
            "energy_level": 9,
            "color_temperature": "warm"
        }
    }


@pytest.fixture
async def test_user(test_session: AsyncSession, test_user_data):
    """Create a test user in the database"""
    from app.models.user import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        email=test_user_data["email"],
        username=test_user_data["username"],
        full_name=test_user_data["full_name"],
        hashed_password=pwd_context.hash(test_user_data["password"]),
        is_active=True,
        is_verified=True,
        role="user",
        credits=100
    )
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    return user


@pytest.fixture
async def test_admin(test_session: AsyncSession, test_admin_data):
    """Create a test admin user in the database"""
    from app.models.user import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    admin = User(
        email=test_admin_data["email"],
        username=test_admin_data["username"],
        full_name=test_admin_data["full_name"],
        hashed_password=pwd_context.hash(test_admin_data["password"]),
        is_active=True,
        is_verified=True,
        role="admin",
        credits=1000
    )
    
    test_session.add(admin)
    await test_session.commit()
    await test_session.refresh(admin)
    
    return admin


@pytest.fixture
async def test_template(test_session: AsyncSession, test_admin, test_template_data):
    """Create a test template in the database"""
    from app.models.template import Template
    
    template = Template(
        **test_template_data,
        created_by=test_admin.id,
        is_active=True,
        performance_score=7.5,
        usage_count=0
    )
    
    test_session.add(template)
    await test_session.commit()
    await test_session.refresh(template)
    
    return template


@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers for test user"""
    from app.core.security import create_access_token
    
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin):
    """Generate authentication headers for test admin"""
    from app.core.security import create_access_token
    
    token = create_access_token(data={"sub": test_admin.id})
    return {"Authorization": f"Bearer {token}"}


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_ai: marks tests that require AI API keys"
    )
