#!/usr/bin/env python3
"""
Setup Supabase tables and add vector search functionality
"""

import psycopg2
import json

# Supabase configuration
SUPABASE_URL = "postgresql://postgres:MandaSolana123%21@db.zaqonwxzoafewoloexsk.supabase.co:5432/postgres"

def setup_supabase():
    """Setup Supabase tables and indexes"""
    print("🚀 Setting up Supabase tables...")
    
    try:
        # Connect to Supabase
        conn = psycopg2.connect(SUPABASE_URL)
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create knowledge_base table with embedding column
        cur.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category VARCHAR(255),
                tags JSONB DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                confidence_threshold FLOAT DEFAULT 0.1,
                embedding TEXT
            );
        """)
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_base_question 
            ON knowledge_base USING gin(to_tsvector('english', question));
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_base_category 
            ON knowledge_base(category);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags 
            ON knowledge_base USING gin(tags);
        """)
        
        # Create question_submissions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS question_submissions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                submission_id VARCHAR(255) UNIQUE NOT NULL,
                questions JSONB NOT NULL,
                answers JSONB,
                processing_time FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Supabase tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Supabase: {str(e)}")
        return False

def add_sample_data():
    """Add sample data to test the system"""
    print("📝 Adding sample data...")
    
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        cur = conn.cursor()
        
        # Add a sample user
        cur.execute("""
            INSERT INTO users (email, name, is_active)
            VALUES ('demo@solana.org', 'Demo User', true)
            ON CONFLICT (email) DO NOTHING;
        """)
        
        # Add a sample knowledge base entry
        cur.execute("""
            INSERT INTO knowledge_base (question, answer, category, tags, is_active)
            VALUES (
                'What is Solana?',
                'Solana is a high-performance blockchain platform designed for decentralized applications and crypto-currencies. It uses a unique Proof of History consensus mechanism to achieve fast transaction speeds and low costs.',
                'General',
                '["solana", "blockchain", "consensus"]',
                true
            )
            ON CONFLICT DO NOTHING;
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Sample data added successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample data: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Supabase for Solana RFP Tool...")
    
    # Setup tables
    if not setup_supabase():
        print("❌ Failed to setup Supabase tables")
        return
    
    # Add sample data
    if not add_sample_data():
        print("❌ Failed to add sample data")
        return
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your backend to use the new Supabase database")
    print("2. Add vector embeddings to existing knowledge base entries")
    print("3. Test the vector search functionality")

if __name__ == "__main__":
    main()
