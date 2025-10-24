#!/usr/bin/env python3
"""
Quick Supabase migration script
"""

import os
import requests
import json
import time

# Configuration
HEROKU_DATABASE_URL = os.getenv('DATABASE_URL')  # Current Heroku database
SUPABASE_URL = os.getenv('SUPABASE_URL')  # New Supabase database
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def export_from_heroku():
    """Export all data from Heroku PostgreSQL"""
    print("📤 Exporting data from Heroku...")
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Connect to Heroku database
        conn = psycopg2.connect(HEROKU_DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Export knowledge base entries
        cur.execute("""
            SELECT id, question, answer, category, tags, created_at, 
                   created_by, is_active, confidence_threshold, embedding
            FROM knowledge_base
            ORDER BY created_at
        """)
        
        knowledge_entries = []
        for row in cur.fetchall():
            knowledge_entries.append({
                'id': str(row['id']),
                'question': row['question'],
                'answer': row['answer'],
                'category': row['category'],
                'tags': row['tags'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'created_by': row['created_by'],
                'is_active': row['is_active'],
                'confidence_threshold': float(row['confidence_threshold']) if row['confidence_threshold'] else 0.1,
                'embedding': row['embedding']
            })
        
        # Export users
        cur.execute("""
            SELECT id, email, name, is_active, created_at
            FROM users
            ORDER BY created_at
        """)
        
        users = []
        for row in cur.fetchall():
            users.append({
                'id': str(row['id']),
                'email': row['email'],
                'name': row['name'],
                'is_active': row['is_active'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None
            })
        
        cur.close()
        conn.close()
        
        print(f"✅ Exported {len(knowledge_entries)} knowledge entries")
        print(f"✅ Exported {len(users)} users")
        
        return {
            'knowledge_entries': knowledge_entries,
            'users': users
        }
        
    except Exception as e:
        print(f"❌ Error exporting from Heroku: {str(e)}")
        return None

def create_supabase_tables():
    """Create tables in Supabase"""
    print("🏗️ Creating tables in Supabase...")
    
    try:
        import psycopg2
        
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
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Tables created successfully in Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def import_to_supabase(data):
    """Import data to Supabase"""
    print("📥 Importing data to Supabase...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(SUPABASE_URL)
        cur = conn.cursor()
        
        # Import users
        for user in data['users']:
            cur.execute("""
                INSERT INTO users (id, email, name, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                user['id'],
                user['email'],
                user['name'],
                user['is_active'],
                user['created_at']
            ))
        
        # Import knowledge base entries
        for entry in data['knowledge_entries']:
            cur.execute("""
                INSERT INTO knowledge_base (
                    id, question, answer, category, tags, 
                    created_at, created_by, is_active, confidence_threshold, embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                entry['id'],
                entry['question'],
                entry['answer'],
                entry['category'],
                entry['tags'],
                entry['created_at'],
                entry['created_by'],
                entry['is_active'],
                entry['confidence_threshold'],
                entry['embedding']
            ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Data imported successfully to Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Error importing to Supabase: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting quick migration from Heroku to Supabase...")
    
    # Check environment variables
    if not HEROKU_DATABASE_URL:
        print("❌ HEROKU_DATABASE_URL not set")
        return
    
    if not SUPABASE_URL:
        print("❌ SUPABASE_URL not set")
        return
    
    # Step 1: Export data from Heroku
    data = export_from_heroku()
    if not data:
        print("❌ Failed to export data from Heroku")
        return
    
    # Step 2: Create tables in Supabase
    if not create_supabase_tables():
        print("❌ Failed to create tables in Supabase")
        return
    
    # Step 3: Import data to Supabase
    if not import_to_supabase(data):
        print("❌ Failed to import data to Supabase")
        return
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your Heroku config vars with Supabase DATABASE_URL")
    print("2. Redeploy your backend")
    print("3. Test all functionality")

if __name__ == "__main__":
    main()
