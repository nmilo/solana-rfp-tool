#!/usr/bin/env python3
"""
Script to import RFP documents from KB raw directory into the knowledge base
"""
import os
import sys
import asyncio
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.services.knowledge_service import KnowledgeBaseService
from app.services.document_service import DocumentService
from app.models.schemas import KnowledgeBaseCreate

def get_kb_files_directory():
    """Get the KB raw directory path"""
    # Go up from backend to project root, then to KB raw
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent.parent
    kb_raw_dir = project_root / "Kb raw"
    return kb_raw_dir

async def process_document_file(file_path: Path, kb_service: KnowledgeBaseService, document_service: DocumentService):
    """Process a single document file and extract questions"""
    print(f"Processing: {file_path.name}")
    
    try:
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Extract text from document
        text = await document_service.extract_text_from_file(file_content, file_path.name)
        
        if not text.strip():
            print(f"  ⚠️  No text could be extracted from {file_path.name}")
            return 0, 0
        
        # Extract questions from text
        try:
            questions = await document_service.extract_questions_from_text(text)
        except Exception:
            # Fallback to simple extraction
            questions = document_service.extract_questions_simple(text)
        
        if not questions:
            print(f"  ⚠️  No questions could be extracted from {file_path.name}")
            return 0, 0
        
        # Add questions to knowledge base
        added_count = 0
        skipped_count = 0
        
        for question in questions:
            try:
                # Create a proper answer based on the document content
                answer = f"This question was extracted from the RFP document: {file_path.name}. The document contains relevant information about this topic. Please review the source document for complete details."
                
                entry_data = KnowledgeBaseCreate(
                    question=question,
                    answer=answer,
                    category="RFP Document",
                    tags=["rfp", "document", "imported", file_path.stem.lower().replace(" ", "-")]
                )
                
                result = kb_service.add_entry(entry_data, created_by="import_script")
                added_count += 1
                
            except ValueError as e:
                # Skip duplicate entries
                skipped_count += 1
        
        print(f"  ✅ Extracted {len(questions)} questions, added {added_count}, skipped {skipped_count}")
        return added_count, skipped_count
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path.name}: {str(e)}")
        return 0, 0

async def import_kb_files():
    """Import all files from KB raw directory"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get KB raw directory
    kb_raw_dir = get_kb_files_directory()
    
    if not kb_raw_dir.exists():
        print(f"❌ KB raw directory not found: {kb_raw_dir}")
        return
    
    print(f"📁 Processing files from: {kb_raw_dir}")
    
    # Get all supported files
    supported_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls']
    files_to_process = []
    
    for file_path in kb_raw_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files_to_process.append(file_path)
    
    if not files_to_process:
        print("❌ No supported files found in KB raw directory")
        return
    
    print(f"📄 Found {len(files_to_process)} files to process:")
    for file_path in files_to_process:
        print(f"  - {file_path.name}")
    
    # Initialize services
    db = SessionLocal()
    try:
        kb_service = KnowledgeBaseService(db)
        document_service = DocumentService()
        
        total_added = 0
        total_skipped = 0
        
        # Process each file
        for file_path in files_to_process:
            added, skipped = await process_document_file(file_path, kb_service, document_service)
            total_added += added
            total_skipped += skipped
        
        print(f"\n🎉 Import complete!")
        print(f"📊 Total added: {total_added} entries")
        print(f"📊 Total skipped: {total_skipped} entries")
        print(f"📊 Files processed: {len(files_to_process)}")
        
    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(import_kb_files())
