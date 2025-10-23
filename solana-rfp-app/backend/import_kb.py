#!/usr/bin/env python3
"""
Script to import existing knowledge base from JSON file
"""
import json
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.database import KnowledgeBase

def import_knowledge_base(json_file_path: str):
    """Import knowledge base from JSON file"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        kb_data = json.load(f)
    
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(KnowledgeBase).delete()
        db.commit()
        
        # Import new data
        imported_count = 0
        for item in kb_data:
            kb_entry = KnowledgeBase(
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                category=item.get("category"),
                created_by="import_script",
                last_modified_by="import_script"
            )
            kb_entry.set_tags(item.get("tags", []))
            db.add(kb_entry)
            imported_count += 1
        
        db.commit()
        print(f"Successfully imported {imported_count} knowledge base entries")
        
    except Exception as e:
        print(f"Error importing knowledge base: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_kb.py <path_to_json_file>")
        print("Example: python import_kb.py ../../kb/rfp_kb.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    if not Path(json_file).exists():
        print(f"File not found: {json_file}")
        sys.exit(1)
    
    import_knowledge_base(json_file)
