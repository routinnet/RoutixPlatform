"""Add pgvector support for template embeddings

Revision ID: pgvector_001
Revises: f3bdaca796a5
Create Date: 2025-10-15 20:00:00.000000

This migration adds pgvector extension support and embedding columns
for advanced template similarity search in PostgreSQL.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'pgvector_001'
down_revision: Union[str, None] = 'f3bdaca796a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade database to support pgvector
    
    This migration:
    1. Creates pgvector extension (PostgreSQL only)
    2. Adds embedding column to templates table
    3. Creates vector similarity index
    4. Converts tags JSON to JSONB for better performance
    5. Converts style_dna JSON to JSONB
    """
    
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
        
        op.execute('''
            ALTER TABLE templates 
            ADD COLUMN IF NOT EXISTS embedding vector(1536)
        ''')
        
        op.execute('''
            CREATE INDEX IF NOT EXISTS idx_templates_embedding_hnsw 
            ON templates 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        ''')
        
        
        op.execute('''
            ALTER TABLE templates 
            ALTER COLUMN tags 
            TYPE JSONB 
            USING tags::jsonb
        ''')
        
        op.execute('''
            ALTER TABLE templates 
            ALTER COLUMN style_dna 
            TYPE JSONB 
            USING style_dna::jsonb
        ''')
        
        op.execute('''
            CREATE INDEX IF NOT EXISTS idx_templates_active 
            ON templates (is_active, category) 
            WHERE is_active = true
        ''')
        
        op.execute('''
            CREATE INDEX IF NOT EXISTS idx_templates_featured 
            ON templates (is_featured, priority DESC) 
            WHERE is_featured = true
        ''')
        
        op.execute('''
            CREATE INDEX IF NOT EXISTS idx_templates_performance 
            ON templates (performance_score DESC, usage_count DESC)
        ''')
        
    else:
        print(f"Skipping pgvector setup for {dialect_name} - only supported on PostgreSQL")
        print("Using SQLite for development - vector search will be limited")


def downgrade() -> None:
    """
    Downgrade database to remove pgvector support
    """
    
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        op.execute('DROP INDEX IF EXISTS idx_templates_embedding_hnsw')
        op.execute('DROP INDEX IF EXISTS idx_templates_embedding_ivfflat')
        op.execute('DROP INDEX IF EXISTS idx_templates_active')
        op.execute('DROP INDEX IF EXISTS idx_templates_featured')
        op.execute('DROP INDEX IF EXISTS idx_templates_performance')
        
        op.execute('ALTER TABLE templates DROP COLUMN IF EXISTS embedding')
        
        op.execute('''
            ALTER TABLE templates 
            ALTER COLUMN tags 
            TYPE TEXT 
            USING tags::text
        ''')
        
        op.execute('''
            ALTER TABLE templates 
            ALTER COLUMN style_dna 
            TYPE JSON 
            USING style_dna::json
        ''')
        
    
    else:
        print(f"Skipping pgvector teardown for {dialect_name}")
