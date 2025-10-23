from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.knowledge_service import KnowledgeBaseService
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
