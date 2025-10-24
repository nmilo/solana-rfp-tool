#!/usr/bin/env python3
"""
Add vector embeddings directly to Supabase
"""

import asyncio
import openai
import json
from app.core.supabase_config import get_supabase_service_client
import os

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def generate_embedding(text: str):
    """Generate OpenAI embedding"""
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {str(e)}")
        return None

async def add_embeddings_to_supabase():
    """Add embeddings to all Supabase entries"""
    print("🚀 Adding vector embeddings to Supabase entries...")
    
    try:
        supabase = get_supabase_service_client()
        
        # Get all entries
        result = supabase.table('knowledge_base').select('*').execute()
        entries = result.data
        
        print(f"📊 Found {len(entries)} entries")
        
        success_count = 0
        for i, entry in enumerate(entries, 1):
            try:
                print(f"[{i}/{len(entries)}] Processing: {entry['question'][:50]}...")
                
                # Generate embedding
                embedding = await generate_embedding(entry['question'])
                
                if embedding:
                    # Update entry with embedding
                    supabase.table('knowledge_base').update({
                        'embedding': json.dumps(embedding)
                    }).eq('id', entry['id']).execute()
                    
                    success_count += 1
                    print(f"✅ Added embedding ({len(embedding)} dimensions)")
                else:
                    print(f"⚠️ Failed to generate embedding")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing entry: {str(e)}")
                continue
        
        print(f"\n🎉 Successfully added embeddings to {success_count}/{len(entries)} entries!")
        print("🎯 Vector search is now ready!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_embeddings_to_supabase())
