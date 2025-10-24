#!/usr/bin/env python3
"""
Final migration script to move all data to Supabase
"""

import requests
import json
import time
import asyncio
from app.core.supabase_config import get_supabase_service_client
from app.services.vector_search_service import VectorSearchService
from app.core.database import get_db

# Heroku backend URL for getting current data
HEROKU_BACKEND_URL = "https://solana-rfp-271974794838.herokuapp.com"
AUTH_TOKEN = "mock-jwt-token-demo"

def get_current_knowledge_base():
    """Get current knowledge base from Heroku"""
    print("📤 Getting current knowledge base from Heroku...")
    
    try:
        # Get all knowledge base entries
        response = requests.get(
            f"{HEROKU_BACKEND_URL}/api/v1/knowledge/admin/preview?page=1&page_size=100",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            print(f"✅ Retrieved {len(entries)} knowledge base entries")
            return entries
        else:
            print(f"❌ Failed to get knowledge base: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting knowledge base: {str(e)}")
        return []

def add_to_supabase(entries):
    """Add entries to Supabase"""
    print("📥 Adding entries to Supabase...")
    
    try:
        supabase = get_supabase_service_client()
        
        success_count = 0
        for entry in entries:
            try:
                # Prepare data for Supabase
                data = {
                    'id': entry['id'],
                    'question': entry['question'],
                    'answer': entry['answer'],
                    'category': entry.get('category'),
                    'tags': entry.get('tags', []),
                    'created_at': entry.get('created_at'),
                    'created_by': entry.get('created_by', 'migration'),
                    'is_active': entry.get('is_active', True),
                    'confidence_threshold': entry.get('confidence_threshold', 0.1),
                    'embedding': None  # Will be added later
                }
                
                # Insert into Supabase
                result = supabase.table('knowledge_base').insert(data).execute()
                
                if result.data:
                    success_count += 1
                    print(f"✅ Added: {entry['question'][:50]}...")
                else:
                    print(f"⚠️ Failed to add: {entry['question'][:50]}...")
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error adding entry: {str(e)}")
                continue
        
        print(f"✅ Successfully added {success_count}/{len(entries)} entries to Supabase")
        return success_count
        
    except Exception as e:
        print(f"❌ Error adding to Supabase: {str(e)}")
        return 0

async def add_embeddings_to_supabase():
    """Add vector embeddings to Supabase entries"""
    print("🧠 Adding vector embeddings to Supabase entries...")
    
    try:
        # Get database session
        db = next(get_db())
        vector_service = VectorSearchService(db)
        
        # Get all entries from Supabase
        supabase = get_supabase_service_client()
        result = supabase.table('knowledge_base').select('*').execute()
        
        entries = result.data
        print(f"📊 Found {len(entries)} entries to add embeddings to")
        
        success_count = 0
        for entry in entries:
            try:
                # Generate embedding
                embedding = await vector_service.generate_embedding(entry['question'])
                
                if embedding:
                    # Update entry with embedding
                    supabase.table('knowledge_base').update({
                        'embedding': json.dumps(embedding)
                    }).eq('id', entry['id']).execute()
                    
                    success_count += 1
                    print(f"✅ Added embedding for: {entry['question'][:50]}...")
                else:
                    print(f"⚠️ Failed to generate embedding for: {entry['question'][:50]}...")
                
                time.sleep(0.5)  # Rate limiting for OpenAI API
                
            except Exception as e:
                print(f"❌ Error adding embedding: {str(e)}")
                continue
        
        print(f"✅ Successfully added embeddings to {success_count}/{len(entries)} entries")
        return success_count
        
    except Exception as e:
        print(f"❌ Error adding embeddings: {str(e)}")
        return 0

def test_supabase_connection():
    """Test Supabase connection"""
    print("🔍 Testing Supabase connection...")
    
    try:
        supabase = get_supabase_service_client()
        
        # Test by getting a simple query
        result = supabase.table('knowledge_base').select('count').execute()
        
        print("✅ Supabase connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

async def main():
    """Main migration function"""
    print("🚀 Starting final migration to Supabase...")
    
    # Test connection
    if not test_supabase_connection():
        print("❌ Cannot connect to Supabase")
        return
    
    # Get current data
    entries = get_current_knowledge_base()
    if not entries:
        print("❌ No data to migrate")
        return
    
    # Add to Supabase
    success_count = add_to_supabase(entries)
    if success_count == 0:
        print("❌ Failed to add data to Supabase")
        return
    
    # Add embeddings
    embedding_count = await add_embeddings_to_supabase()
    
    print(f"\n🎉 Migration completed successfully!")
    print(f"📊 Migrated {success_count} entries")
    print(f"🧠 Added embeddings to {embedding_count} entries")
    print("\n📋 Next steps:")
    print("1. Update your backend to use Supabase DATABASE_URL")
    print("2. Test the vector search functionality")
    print("3. Deploy the updated system")

if __name__ == "__main__":
    asyncio.run(main())
