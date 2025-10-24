#!/usr/bin/env python3
"""
Migration script to move from Heroku PostgreSQL to Supabase
"""

import os
import requests
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration
HEROKU_DATABASE_URL = os.getenv('DATABASE_URL')  # Current Heroku database
SUPABASE_URL = os.getenv('SUPABASE_URL')  # New Supabase database
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def export_from_heroku():
    """Export all data from Heroku PostgreSQL"""
    print("📤 Exporting data from Heroku...")
    
    try:
        # Connect to Heroku database
        engine = create_engine(HEROKU_DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Export knowledge base entries
        result = session.execute(text("""
            SELECT id, question, answer, category, tags, created_at, 
                   created_by, is_active, confidence_threshold
            FROM knowledge_base
            ORDER BY created_at
        """))
        
        knowledge_entries = []
        for row in result:
            knowledge_entries.append({
                'id': str(row[0]),
                'question': row[1],
                'answer': row[2],
                'category': row[3],
                'tags': json.loads(row[4]) if row[4] else [],
                'created_at': row[5].isoformat() if row[5] else None,
                'created_by': row[6],
                'is_active': row[7],
                'confidence_threshold': float(row[8]) if row[8] else 0.1
            })
        
        # Export users
        result = session.execute(text("""
            SELECT id, email, name, is_active, created_at
            FROM users
            ORDER BY created_at
        """))
        
        users = []
        for row in result:
            users.append({
                'id': str(row[0]),
                'email': row[1],
                'name': row[2],
                'is_active': row[3],
                'created_at': row[4].isoformat() if row[4] else None
            })
        
        session.close()
        
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
        
        # Create knowledge_base table
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
                confidence_threshold FLOAT DEFAULT 0.1
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
                    created_at, created_by, is_active, confidence_threshold
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                entry['id'],
                entry['question'],
                entry['answer'],
                entry['category'],
                json.dumps(entry['tags']),
                entry['created_at'],
                entry['created_by'],
                entry['is_active'],
                entry['confidence_threshold']
            ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Data imported successfully to Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Error importing to Supabase: {str(e)}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    print("🔍 Verifying migration...")
    
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check knowledge base count
        cur.execute("SELECT COUNT(*) as count FROM knowledge_base")
        kb_count = cur.fetchone()['count']
        
        # Check users count
        cur.execute("SELECT COUNT(*) as count FROM users")
        users_count = cur.fetchone()['count']
        
        # Check sample entries
        cur.execute("""
            SELECT question, answer, category, tags 
            FROM knowledge_base 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        sample_entries = cur.fetchall()
        
        cur.close()
        conn.close()
        
        print(f"✅ Knowledge base entries: {kb_count}")
        print(f"✅ Users: {users_count}")
        print("✅ Sample entries:")
        for entry in sample_entries:
            print(f"   - {entry['question'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting migration from Heroku to Supabase...")
    
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
    
    # Step 4: Verify migration
    if not verify_migration():
        print("❌ Migration verification failed")
        return
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your backend DATABASE_URL to point to Supabase")
    print("2. Update environment variables in Heroku")
    print("3. Redeploy your backend")
    print("4. Test all functionality")
    print("5. Update frontend if needed")

if __name__ == "__main__":
    main()
