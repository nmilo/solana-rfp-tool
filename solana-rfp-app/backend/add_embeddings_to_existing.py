#!/usr/bin/env python3
"""
Add vector embeddings to existing knowledge base entries
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.vector_search_service import VectorSearchService

async def main():
    """Add embeddings to existing knowledge base entries"""
    print("🚀 Adding vector embeddings to existing knowledge base entries...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create vector search service
        vector_service = VectorSearchService(db)
        
        # Add embeddings to existing entries
        await vector_service.add_existing_knowledge_base_embeddings()
        
        print("✅ Successfully added embeddings to all existing entries!")
        print("🎯 Vector search is now ready!")
        
    except Exception as e:
        print(f"❌ Error adding embeddings: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
