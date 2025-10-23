from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# Knowledge Base Schemas
class KnowledgeBaseBase(BaseModel):
    question: str
    answer: str
    tags: List[str] = []
    category: Optional[str] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None

class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: UUID
    confidence_threshold: float
    created_at: datetime
    updated_at: datetime
    is_active: bool
    created_by: str
    last_modified_by: str

    class Config:
        from_attributes = True

# Question Processing Schemas
class TextQuestionRequest(BaseModel):
    text: str

class PDFUploadRequest(BaseModel):
    filename: str
    content: bytes

class QuestionResult(BaseModel):
    question: str
    answer: str
    confidence: float
    source_id: Optional[UUID] = None
    source_question: Optional[str] = None

class ProcessingResult(BaseModel):
    questions_processed: int
    answers_found: int
    results: List[QuestionResult]
    processing_time: Optional[float] = None
    submission_id: Optional[str] = None

# Search Schemas
class SearchRequest(BaseModel):
    query: str
    min_confidence: float = 0.1
    limit: int = 10

class SearchResult(BaseModel):
    id: UUID
    question: str
    answer: str
    confidence: float
    tags: List[str]
    category: Optional[str]

class SearchResponse(BaseModel):
    query: str
    matches: List[SearchResult]
    total_matches: int
