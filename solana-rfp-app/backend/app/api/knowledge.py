from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.knowledge_service import KnowledgeBaseService
from app.services.pdf_service import PDFService
from app.models.schemas import (
    KnowledgeBaseCreate, 
    KnowledgeBaseUpdate, 
    KnowledgeBaseResponse,
    SearchRequest,
    SearchResponse
)
from app.api.auth import get_current_user

router = APIRouter()

def get_kb_service(db: Session = Depends(get_db)) -> KnowledgeBaseService:
    return KnowledgeBaseService(db)

def get_pdf_service() -> PDFService:
    return PDFService()

@router.get("/entries", response_model=List[KnowledgeBaseResponse])
async def get_all_entries(
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Get all knowledge base entries with optional filtering"""
    tag_list = tags.split(',') if tags else None
    entries = kb_service.get_all_entries(category=category, tags=tag_list)
    return entries

@router.post("/entries", response_model=KnowledgeBaseResponse)
async def add_entry(
    entry: KnowledgeBaseCreate,
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Add new knowledge base entry"""
    try:
        result = kb_service.add_entry(entry, created_by=current_user.email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/entries/{entry_id}", response_model=KnowledgeBaseResponse)
async def update_entry(
    entry_id: str,
    update: KnowledgeBaseUpdate,
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Update knowledge base entry"""
    try:
        result = kb_service.update_entry(entry_id, update, modified_by=current_user.email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Delete knowledge base entry"""
    success = kb_service.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted successfully"}

@router.get("/search", response_model=SearchResponse)
async def search_knowledge_base(
    query: str = Query(..., description="Search query"),
    min_confidence: float = Query(0.1, description="Minimum confidence threshold"),
    limit: int = Query(10, description="Maximum number of results"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Search knowledge base for answers"""
    matches = kb_service.search_answers(query, min_confidence)
    
    # Apply limit
    limited_matches = matches[:limit]
    
    return SearchResponse(
        query=query,
        matches=limited_matches,
        total_matches=len(matches)
    )

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    pdf_service: PDFService = Depends(get_pdf_service),
    current_user = Depends(get_current_user)
):
    """Upload and process a document to add to knowledge base"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        text = await pdf_service.extract_text_from_pdf(file_content)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        # Extract questions from text
        try:
            questions = await pdf_service.extract_questions_from_text(text)
        except ValueError:
            # Fallback to simple extraction
            questions = pdf_service.extract_questions_simple(text)
        
        if not questions:
            raise HTTPException(status_code=400, detail="No questions could be extracted from the document")
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        # Add questions to knowledge base
        added_entries = []
        skipped_entries = []
        
        for question in questions:
            try:
                # Create a basic answer placeholder
                answer = f"This question was extracted from the uploaded document: {file.filename}. Please review and provide a proper answer."
                
                entry_data = KnowledgeBaseCreate(
                    question=question,
                    answer=answer,
                    category=category or "Uploaded Document",
                    tags=tag_list + ["uploaded", "needs-review"]
                )
                
                result = kb_service.add_entry(entry_data, created_by=current_user.email)
                added_entries.append(result)
                
            except ValueError as e:
                # Skip duplicate entries
                skipped_entries.append({"question": question, "reason": str(e)})
        
        return {
            "message": f"Document processed successfully",
            "filename": file.filename,
            "extracted_questions": len(questions),
            "added_entries": len(added_entries),
            "skipped_entries": len(skipped_entries),
            "added_questions": [entry["question"] for entry in added_entries],
            "skipped_questions": [entry["question"] for entry in skipped_entries]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/stats")
async def get_knowledge_base_stats(
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Get knowledge base statistics"""
    entries = kb_service.get_all_entries()
    
    # Calculate stats
    total_entries = len(entries)
    categories = {}
    tags = {}
    
    for entry in entries:
        # Count categories
        if entry["category"]:
            categories[entry["category"]] = categories.get(entry["category"], 0) + 1
        
        # Count tags
        for tag in entry["tags"]:
            tags[tag] = tags.get(tag, 0) + 1
    
    return {
        "total_entries": total_entries,
        "categories": categories,
        "top_tags": dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10])
    }
