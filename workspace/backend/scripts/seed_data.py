"""
Seed data script for Routix Platform
Creates initial admin user, default algorithm, and system settings
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from passlib.context import CryptContext
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import AsyncSessionLocal, engine, Base
from app.models import (
    User, GenerationAlgorithm, SystemSettings
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_admin_user():
    """Create admin user"""
    async with AsyncSessionLocal() as session:
        # Check if admin user already exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == "admin@routix.com")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("✅ Admin user already exists")
            return existing_admin
        
        # Create admin user
        hashed_password = pwd_context.hash("secure_password")
        admin_user = User(
            email="admin@routix.com",
            username="admin",
            password_hash=hashed_password,
            credits=10000,  # Give admin plenty of credits
            subscription_tier="enterprise",
            is_active=True,
            is_admin=True,
            email_verified=True,
            last_login=datetime.now(timezone.utc)
        )
        
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        
        print(f"✅ Created admin user: {admin_user.email} (ID: {admin_user.id})")
        return admin_user


async def seed_default_algorithm():
    """Create default Routix v1 algorithm"""
    async with AsyncSessionLocal() as session:
        # Check if default algorithm already exists
        from sqlalchemy import select
        result = await session.execute(
            select(GenerationAlgorithm).where(GenerationAlgorithm.name == "routix_v1")
        )
        existing_algorithm = result.scalar_one_or_none()
        
        if existing_algorithm:
            print("✅ Default algorithm already exists")
            return existing_algorithm
        
        # Create default algorithm
        default_algorithm = GenerationAlgorithm(
            name="routix_v1",
            display_name="Routix v1",
            description="Default Routix algorithm using Midjourney API with template matching",
            ai_provider="midjourney",
            config='{"style": "raw", "quality": "high", "aspect_ratio": "16:9", "stylize": 750}',
            cost_per_generation=0.04,  # $0.04 per generation
            credit_cost=1,  # 1 credit per generation
            is_active=True,
            is_default=True,
            performance_metrics='{"success_rate": 95.0, "avg_processing_time": 25.5, "user_satisfaction": 4.2}'
        )
        
        session.add(default_algorithm)
        await session.commit()
        await session.refresh(default_algorithm)
        
        print(f"✅ Created default algorithm: {default_algorithm.display_name} (ID: {default_algorithm.id})")
        return default_algorithm


async def seed_additional_algorithms():
    """Create additional Routix algorithms"""
    async with AsyncSessionLocal() as session:
        algorithms = [
            {
                "name": "routix_pro",
                "display_name": "Routix Pro",
                "description": "Enhanced algorithm with better quality and customization options",
                "ai_provider": "midjourney",
                "config": '{"style": "raw", "quality": "ultra", "aspect_ratio": "16:9", "stylize": 1000, "chaos": 10}',
                "cost_per_generation": 0.08,
                "credit_cost": 2,
                "is_active": True,
                "is_default": False,
                "performance_metrics": '{"success_rate": 98.0, "avg_processing_time": 35.2, "user_satisfaction": 4.6}'
            },
            {
                "name": "routix_lightning",
                "display_name": "Routix Lightning",
                "description": "Fast generation algorithm optimized for speed",
                "ai_provider": "dalle3",
                "config": '{"quality": "standard", "size": "1792x1024", "style": "vivid"}',
                "cost_per_generation": 0.02,
                "credit_cost": 1,
                "is_active": True,
                "is_default": False,
                "performance_metrics": '{"success_rate": 92.0, "avg_processing_time": 12.8, "user_satisfaction": 4.0}'
            }
        ]
        
        for algo_data in algorithms:
            # Check if algorithm already exists
            from sqlalchemy import select
            result = await session.execute(
                select(GenerationAlgorithm).where(GenerationAlgorithm.name == algo_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"✅ Algorithm {algo_data['display_name']} already exists")
                continue
            
            algorithm = GenerationAlgorithm(**algo_data)
            session.add(algorithm)
            await session.commit()
            await session.refresh(algorithm)
            
            print(f"✅ Created algorithm: {algorithm.display_name} (ID: {algorithm.id})")


async def seed_system_settings():
    """Create system settings"""
    async with AsyncSessionLocal() as session:
        settings = [
            {
                "key": "platform_version",
                "value": '{"version": "1.0.0", "build": "initial", "release_date": "2024-12-07"}',
                "description": "Platform version information",
                "is_public": True
            },
            {
                "key": "credit_costs",
                "value": '{"routix_v1": 1, "routix_pro": 2, "routix_lightning": 1}',
                "description": "Credit costs for different algorithms",
                "is_public": False
            },
            {
                "key": "subscription_plans",
                "value": '{"free": {"credits": 10, "price": 0}, "pro": {"credits": 100, "price": 19.99}, "agency": {"credits": 500, "price": 49.99}, "enterprise": {"credits": -1, "price": "custom"}}',
                "description": "Available subscription plans and pricing",
                "is_public": True
            },
            {
                "key": "ai_service_config",
                "value": '{"midjourney": {"rate_limit": 10, "timeout": 60}, "dalle3": {"rate_limit": 50, "timeout": 30}, "gemini": {"rate_limit": 100, "timeout": 10}}',
                "description": "AI service configuration and limits",
                "is_public": False
            },
            {
                "key": "template_categories",
                "value": '["gaming", "business", "lifestyle", "education", "entertainment", "technology", "sports", "food", "travel", "music"]',
                "description": "Available template categories",
                "is_public": True
            },
            {
                "key": "max_file_sizes",
                "value": '{"face_image": 5242880, "logo_image": 2097152, "custom_image": 10485760}',
                "description": "Maximum file sizes in bytes for different asset types",
                "is_public": False
            }
        ]
        
        for setting_data in settings:
            # Check if setting already exists
            from sqlalchemy import select
            result = await session.execute(
                select(SystemSettings).where(SystemSettings.key == setting_data["key"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"✅ System setting {setting_data['key']} already exists")
                continue
            
            setting = SystemSettings(**setting_data)
            session.add(setting)
            await session.commit()
            await session.refresh(setting)
            
            print(f"✅ Created system setting: {setting.key} (ID: {setting.id})")


async def verify_seed_data():
    """Verify that all seed data was created correctly"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        
        # Count users
        result = await session.execute(select(func.count(User.id)))
        user_count = result.scalar()
        
        # Count algorithms
        result = await session.execute(select(func.count(GenerationAlgorithm.id)))
        algorithm_count = result.scalar()
        
        # Count system settings
        result = await session.execute(select(func.count(SystemSettings.id)))
        settings_count = result.scalar()
        
        print(f"\n📊 SEED DATA VERIFICATION:")
        print(f"   Users: {user_count}")
        print(f"   Algorithms: {algorithm_count}")
        print(f"   System Settings: {settings_count}")
        
        # Verify admin user
        result = await session.execute(
            select(User).where(User.email == "admin@routix.com")
        )
        admin = result.scalar_one_or_none()
        if admin:
            print(f"   ✅ Admin user verified: {admin.email} (Credits: {admin.credits})")
        
        # Verify default algorithm
        result = await session.execute(
            select(GenerationAlgorithm).where(GenerationAlgorithm.is_default == True)
        )
        default_algo = result.scalar_one_or_none()
        if default_algo:
            print(f"   ✅ Default algorithm verified: {default_algo.display_name}")
        
        return {
            "users": user_count,
            "algorithms": algorithm_count,
            "settings": settings_count,
            "admin_exists": admin is not None,
            "default_algorithm_exists": default_algo is not None
        }


async def main():
    """Main seed function"""
    print("🌱 Starting database seeding process...")
    
    try:
        # Create tables if they don't exist
        await create_tables()
        print("✅ Database tables ready")
        
        # Seed data
        admin_user = await seed_admin_user()
        default_algorithm = await seed_default_algorithm()
        await seed_additional_algorithms()
        await seed_system_settings()
        
        # Verify everything was created
        verification = await verify_seed_data()
        
        print(f"\n🎉 DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print(f"   Ready for Routix Platform development")
        
        return verification
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        raise


if __name__ == "__main__":
    # Install required packages if not available
    try:
        import passlib
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "passlib[bcrypt]"])
        import passlib
    
    # Run the seed script
    asyncio.run(main())