"""
Database Seeding Script for Routix Platform
Creates initial data for development and testing
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session, engine
from app.core.config import settings
from app.models import User, Template, Asset
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user(session: AsyncSession) -> User:
    """Create default admin user"""
    try:
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == "admin@routix.dev")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            logger.info("Admin user already exists")
            return existing_admin
        
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        admin = User(
            email="admin@routix.dev",
            username="admin",
            full_name="Admin User",
            hashed_password=pwd_context.hash("admin123"),  # Change in production!
            role="admin",
            is_active=True,
            is_verified=True,
            credits=10000,
            subscription_tier="enterprise",
            subscription_status="active"
        )
        
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        
        logger.info(f"Created admin user: {admin.email}")
        return admin
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        await session.rollback()
        raise


async def create_demo_users(session: AsyncSession) -> list[User]:
    """Create demo users for testing"""
    try:
        from passlib.context import CryptContext
        from sqlalchemy import select
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        demo_users = [
            {
                "email": "user@demo.com",
                "username": "demo_user",
                "full_name": "Demo User",
                "role": "user",
                "credits": 100,
                "subscription_tier": "pro",
                "subscription_status": "active"
            },
            {
                "email": "creator@demo.com",
                "username": "content_creator",
                "full_name": "Content Creator",
                "role": "user",
                "credits": 500,
                "subscription_tier": "enterprise",
                "subscription_status": "active"
            },
            {
                "email": "free@demo.com",
                "username": "free_user",
                "full_name": "Free User",
                "role": "user",
                "credits": 10,
                "subscription_tier": "free",
                "subscription_status": "active"
            }
        ]
        
        created_users = []
        
        for user_data in demo_users:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info(f"User {user_data['email']} already exists")
                created_users.append(existing_user)
                continue
            
            user = User(
                **user_data,
                hashed_password=pwd_context.hash("demo123"),
                is_active=True,
                is_verified=True
            )
            
            session.add(user)
            created_users.append(user)
            logger.info(f"Created demo user: {user_data['email']}")
        
        await session.commit()
        
        for user in created_users:
            await session.refresh(user)
        
        return created_users
        
    except Exception as e:
        logger.error(f"Failed to create demo users: {e}")
        await session.rollback()
        raise


async def create_sample_templates(session: AsyncSession, admin_user: User) -> list[Template]:
    """Create sample templates for testing"""
    try:
        from sqlalchemy import select
        
        sample_templates = [
            {
                "image_url": "https://example.com/templates/gaming-1.jpg",
                "thumbnail_url": "https://example.com/templates/gaming-1-thumb.jpg",
                "category": "gaming",
                "description": "High-energy gaming thumbnail with bold text and vibrant colors",
                "has_face": True,
                "has_text": True,
                "has_logo": True,
                "energy_level": 9,
                "tags": '["gaming", "action", "vibrant", "bold"]',
                "style_dna": {
                    "color_analysis": {
                        "primary_colors": ["#FF0000", "#000000", "#FFFFFF"],
                        "color_temperature": "warm",
                        "contrast_level": "high"
                    },
                    "typography": {
                        "text_style": "bold",
                        "text_size": "large",
                        "text_placement": "center"
                    },
                    "style_characteristics": {
                        "design_style": "modern",
                        "energy_level": 9,
                        "mood": "exciting"
                    }
                },
                "performance_score": 8.5,
                "is_featured": True,
                "priority": 10
            },
            {
                "image_url": "https://example.com/templates/tech-1.jpg",
                "thumbnail_url": "https://example.com/templates/tech-1-thumb.jpg",
                "category": "technology",
                "description": "Clean tech tutorial thumbnail with product showcase",
                "has_face": False,
                "has_text": True,
                "has_logo": True,
                "energy_level": 6,
                "tags": '["tech", "tutorial", "clean", "modern"]',
                "style_dna": {
                    "color_analysis": {
                        "primary_colors": ["#0066CC", "#FFFFFF", "#F5F5F5"],
                        "color_temperature": "cool",
                        "contrast_level": "medium"
                    },
                    "typography": {
                        "text_style": "clean",
                        "text_size": "medium",
                        "text_placement": "top"
                    },
                    "style_characteristics": {
                        "design_style": "minimalist",
                        "energy_level": 6,
                        "mood": "professional"
                    }
                },
                "performance_score": 7.8,
                "is_featured": True,
                "priority": 8
            },
            {
                "image_url": "https://example.com/templates/vlog-1.jpg",
                "thumbnail_url": "https://example.com/templates/vlog-1-thumb.jpg",
                "category": "vlog",
                "description": "Lifestyle vlog thumbnail with personal branding",
                "has_face": True,
                "has_text": True,
                "has_logo": False,
                "energy_level": 7,
                "tags": '["vlog", "lifestyle", "personal", "friendly"]',
                "style_dna": {
                    "color_analysis": {
                        "primary_colors": ["#FFC0CB", "#FFD700", "#FFFFFF"],
                        "color_temperature": "warm",
                        "contrast_level": "medium"
                    },
                    "typography": {
                        "text_style": "casual",
                        "text_size": "medium",
                        "text_placement": "bottom"
                    },
                    "style_characteristics": {
                        "design_style": "casual",
                        "energy_level": 7,
                        "mood": "friendly"
                    }
                },
                "performance_score": 7.5,
                "is_featured": False,
                "priority": 5
            },
            {
                "image_url": "https://example.com/templates/education-1.jpg",
                "thumbnail_url": "https://example.com/templates/education-1-thumb.jpg",
                "category": "education",
                "description": "Professional educational content thumbnail",
                "has_face": True,
                "has_text": True,
                "has_logo": True,
                "energy_level": 5,
                "tags": '["education", "professional", "clear", "trustworthy"]',
                "style_dna": {
                    "color_analysis": {
                        "primary_colors": ["#003366", "#FFFFFF", "#F0F0F0"],
                        "color_temperature": "cool",
                        "contrast_level": "high"
                    },
                    "typography": {
                        "text_style": "professional",
                        "text_size": "large",
                        "text_placement": "center"
                    },
                    "style_characteristics": {
                        "design_style": "professional",
                        "energy_level": 5,
                        "mood": "trustworthy"
                    }
                },
                "performance_score": 8.2,
                "is_featured": True,
                "priority": 9
            },
            {
                "image_url": "https://example.com/templates/comedy-1.jpg",
                "thumbnail_url": "https://example.com/templates/comedy-1-thumb.jpg",
                "category": "entertainment",
                "description": "Fun and engaging comedy/entertainment thumbnail",
                "has_face": True,
                "has_text": True,
                "has_logo": False,
                "energy_level": 8,
                "tags": '["comedy", "entertainment", "fun", "engaging"]',
                "style_dna": {
                    "color_analysis": {
                        "primary_colors": ["#FFFF00", "#FF00FF", "#00FFFF"],
                        "color_temperature": "warm",
                        "contrast_level": "high"
                    },
                    "typography": {
                        "text_style": "playful",
                        "text_size": "large",
                        "text_placement": "center"
                    },
                    "style_characteristics": {
                        "design_style": "playful",
                        "energy_level": 8,
                        "mood": "fun"
                    }
                },
                "performance_score": 7.9,
                "is_featured": False,
                "priority": 6
            }
        ]
        
        created_templates = []
        
        for template_data in sample_templates:
            result = await session.execute(
                select(Template).where(
                    Template.image_url == template_data["image_url"]
                )
            )
            existing_template = result.scalar_one_or_none()
            
            if existing_template:
                logger.info(f"Template {template_data['category']} already exists")
                created_templates.append(existing_template)
                continue
            
            template = Template(
                **template_data,
                created_by=admin_user.id,
                is_active=True,
                usage_count=0,
                success_rate=0.0
            )
            
            session.add(template)
            created_templates.append(template)
            logger.info(f"Created sample template: {template_data['category']}")
        
        await session.commit()
        
        for template in created_templates:
            await session.refresh(template)
        
        return created_templates
        
    except Exception as e:
        logger.error(f"Failed to create sample templates: {e}")
        await session.rollback()
        raise


async def main():
    """Main seeding function"""
    try:
        logger.info("=" * 60)
        logger.info("Starting Routix Platform Database Seeding")
        logger.info("=" * 60)
        
        async for session in get_async_session():
            logger.info("\n1. Creating admin user...")
            admin_user = await create_admin_user(session)
            
            logger.info("\n2. Creating demo users...")
            demo_users = await create_demo_users(session)
            
            logger.info("\n3. Creating sample templates...")
            sample_templates = await create_sample_templates(session, admin_user)
            
            logger.info("\n" + "=" * 60)
            logger.info("Database seeding completed successfully!")
            logger.info("=" * 60)
            logger.info(f"\nCreated:")
            logger.info(f"  - 1 admin user")
            logger.info(f"  - {len(demo_users)} demo users")
            logger.info(f"  - {len(sample_templates)} sample templates")
            logger.info("\nDefault credentials:")
            logger.info("  Admin: admin@routix.dev / admin123")
            logger.info("  Demo User: user@demo.com / demo123")
            logger.info("  Creator: creator@demo.com / demo123")
            logger.info("  Free User: free@demo.com / demo123")
            logger.info("\n⚠️  IMPORTANT: Change passwords in production!")
            logger.info("=" * 60)
            
            break
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
