#!/usr/bin/env python3
"""
Create initial backup of knowledge base
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.core.database_persistence import DatabasePersistence
from app.core.logger import main_logger

def main():
    """Create initial backup of knowledge base"""
    try:
        print("🔄 Creating initial backup of knowledge base...")
        
        # Get database session
        db = next(get_db())
        
        # Create persistence manager
        persistence = DatabasePersistence(db)
        
        # Create backup
        backup_file = persistence.backup_knowledge_base()
        
        print(f"✅ Initial backup created: {backup_file}")
        print("📊 This backup will be used to restore the knowledge base if it gets reset")
        
    except Exception as e:
        print(f"❌ Failed to create backup: {str(e)}")
        main_logger.error(f"Failed to create initial backup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
