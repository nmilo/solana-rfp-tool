# Solana RFP Database - Revised Architecture (Knowledge Base Focus)

## Core Philosophy
- **No AI for answer generation** - Only retrieve from curated knowledge base
- **AI only for question extraction** from PDFs
- **High confidence matching** - If no good match, return "No answer found"
- **Full knowledge base management** - Add, edit, delete, search entries

## Revised Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with full-text search
- **Vector Search**: Your existing TF-IDF + cosine similarity (proven to work)
- **AI Usage**: OpenAI GPT-4 **ONLY** for PDF question extraction
- **File Storage**: Local filesystem or S3 for PDFs

### Frontend
- **Framework**: React.js + TypeScript
- **UI**: Tailwind CSS + Headless UI
- **State Management**: Zustand (lightweight)
- **File Upload**: React Dropzone

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Knowledge     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Base (DB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   PDF Processing│
                    │   (OpenAI GPT-4)│
                    └─────────────────┘
```

## Database Schema (Simplified)

### knowledge_base
```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tags TEXT[],
    category VARCHAR(100),
    confidence_threshold FLOAT DEFAULT 0.1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    last_modified_by VARCHAR(100)
);

-- Full-text search index
CREATE INDEX idx_kb_fulltext ON knowledge_base USING gin(to_tsvector('english', question || ' ' || answer));

-- Tags index
CREATE INDEX idx_kb_tags ON knowledge_base USING gin(tags);
```

### question_submissions
```sql
CREATE TABLE question_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    input_type VARCHAR(20) NOT NULL, -- 'text' or 'pdf'
    raw_input TEXT,
    extracted_questions JSONB,
    matched_answers JSONB,
    confidence_scores JSONB,
    processing_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Core Services

### 1. Knowledge Base Service
```python
# app/services/knowledge_service.py
from typing import List, Dict, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class KnowledgeBaseService:
    def __init__(self, db_session):
        self.db = db_session
        self.vectorizer = None
        self.X = None
        self.corpus = None
        self.kb_items = []
        self._rebuild_index()
    
    def _rebuild_index(self):
        """Rebuild TF-IDF index when knowledge base changes"""
        self.kb_items = self.get_all_active_entries()
        if not self.kb_items:
            return
            
        corpus = [
            self._normalize_text(
                item.question + " " + item.answer + " " + " ".join(item.tags or [])
            ) 
            for item in self.kb_items
        ]
        
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        self.X = self.vectorizer.fit_transform(corpus)
        self.corpus = corpus
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing"""
        text = text.lower()
        text = re.sub(r"[^\w\s\-\.]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    
    def search_answers(self, question: str, min_confidence: float = 0.1) -> List[Dict]:
        """Search knowledge base for answers to a question"""
        if not self.kb_items or not self.vectorizer:
            return []
        
        # Normalize question
        qn = self._normalize_text(question)
        qv = self.vectorizer.transform([qn])
        
        # Calculate similarities
        similarities = cosine_similarity(qv, self.X)[0]
        
        # Get matches above threshold
        matches = []
        for i, score in enumerate(similarities):
            if score >= min_confidence:
                kb_item = self.kb_items[i]
                matches.append({
                    "id": kb_item.id,
                    "question": kb_item.question,
                    "answer": kb_item.answer,
                    "confidence": float(score),
                    "tags": kb_item.tags,
                    "category": kb_item.category
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches
    
    def get_best_answer(self, question: str, min_confidence: float = 0.1) -> Optional[Dict]:
        """Get the best matching answer for a question"""
        matches = self.search_answers(question, min_confidence)
        return matches[0] if matches else None
    
    def add_entry(self, question: str, answer: str, tags: List[str] = None, 
                  category: str = None, created_by: str = "admin") -> Dict:
        """Add new knowledge base entry"""
        # Check for duplicates
        existing = self.search_answers(question, min_confidence=0.8)
        if existing:
            raise ValueError("Similar question already exists in knowledge base")
        
        # Add to database
        kb_entry = KnowledgeBase(
            question=question,
            answer=answer,
            tags=tags or [],
            category=category,
            created_by=created_by,
            last_modified_by=created_by
        )
        self.db.add(kb_entry)
        self.db.commit()
        
        # Rebuild index
        self._rebuild_index()
        
        return {
            "id": kb_entry.id,
            "question": kb_entry.question,
            "answer": kb_entry.answer,
            "tags": kb_entry.tags,
            "category": kb_entry.category
        }
    
    def update_entry(self, entry_id: str, question: str = None, answer: str = None,
                    tags: List[str] = None, category: str = None, 
                    modified_by: str = "admin") -> Dict:
        """Update knowledge base entry"""
        kb_entry = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
        if not kb_entry:
            raise ValueError("Knowledge base entry not found")
        
        if question is not None:
            kb_entry.question = question
        if answer is not None:
            kb_entry.answer = answer
        if tags is not None:
            kb_entry.tags = tags
        if category is not None:
            kb_entry.category = category
        
        kb_entry.last_modified_by = modified_by
        self.db.commit()
        
        # Rebuild index
        self._rebuild_index()
        
        return {
            "id": kb_entry.id,
            "question": kb_entry.question,
            "answer": kb_entry.answer,
            "tags": kb_entry.tags,
            "category": kb_entry.category
        }
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete knowledge base entry"""
        kb_entry = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
        if not kb_entry:
            return False
        
        self.db.delete(kb_entry)
        self.db.commit()
        
        # Rebuild index
        self._rebuild_index()
        return True
    
    def get_all_entries(self, category: str = None, tags: List[str] = None) -> List[Dict]:
        """Get all knowledge base entries with optional filtering"""
        query = self.db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
        
        if category:
            query = query.filter(KnowledgeBase.category == category)
        
        if tags:
            query = query.filter(KnowledgeBase.tags.overlap(tags))
        
        entries = query.order_by(KnowledgeBase.created_at.desc()).all()
        
        return [
            {
                "id": entry.id,
                "question": entry.question,
                "answer": entry.answer,
                "tags": entry.tags,
                "category": entry.category,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
                "created_by": entry.created_by,
                "last_modified_by": entry.last_modified_by
            }
            for entry in entries
        ]
```

### 2. PDF Question Extraction Service
```python
# app/services/pdf_service.py
import PyPDF2
import io
from typing import List
import openai
from app.core.config import settings

class PDFService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")
    
    async def extract_questions_from_text(self, text: str) -> List[str]:
        """Use OpenAI to extract questions from PDF text - ONLY for question extraction"""
        prompt = f"""
        Extract all questions from the following RFP document text. 
        Return ONLY the questions, one per line, without numbering or bullet points.
        Do not provide answers or explanations.
        
        Text: {text[:4000]}
        
        Questions:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            questions_text = response.choices[0].message.content
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            return questions
        except Exception as e:
            raise ValueError(f"Error extracting questions: {str(e)}")
```

## API Endpoints

### Knowledge Base Management
```python
# app/api/knowledge.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.knowledge_service import KnowledgeBaseService
from app.models.schemas import KnowledgeBaseEntry, KnowledgeBaseUpdate

router = APIRouter()

@router.get("/entries")
async def get_all_entries(
    category: str = None,
    tags: str = None,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Get all knowledge base entries with optional filtering"""
    tag_list = tags.split(',') if tags else None
    return kb_service.get_all_entries(category=category, tags=tag_list)

@router.post("/entries")
async def add_entry(
    entry: KnowledgeBaseEntry,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Add new knowledge base entry"""
    try:
        return kb_service.add_entry(
            question=entry.question,
            answer=entry.answer,
            tags=entry.tags,
            category=entry.category,
            created_by="admin"  # TODO: Get from auth
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/entries/{entry_id}")
async def update_entry(
    entry_id: str,
    update: KnowledgeBaseUpdate,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Update knowledge base entry"""
    try:
        return kb_service.update_entry(
            entry_id=entry_id,
            question=update.question,
            answer=update.answer,
            tags=update.tags,
            category=update.category,
            modified_by="admin"  # TODO: Get from auth
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Delete knowledge base entry"""
    success = kb_service.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted successfully"}

@router.get("/search")
async def search_knowledge_base(
    query: str,
    min_confidence: float = 0.1,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Search knowledge base for answers"""
    matches = kb_service.search_answers(query, min_confidence)
    return {
        "query": query,
        "matches": matches,
        "total_matches": len(matches)
    }
```

### Question Processing
```python
# app/api/questions.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.knowledge_service import KnowledgeBaseService
from app.services.pdf_service import PDFService

router = APIRouter()

@router.post("/process-text")
async def process_text_questions(
    request: TextQuestionRequest,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Process text questions and return answers from knowledge base"""
    questions = extract_questions_from_text(request.text)  # Your existing logic
    results = []
    
    for question in questions:
        best_match = kb_service.get_best_answer(question, min_confidence=0.1)
        results.append({
            "question": question,
            "answer": best_match["answer"] if best_match else "No answer found in knowledge base",
            "confidence": best_match["confidence"] if best_match else 0.0,
            "source": best_match["id"] if best_match else None
        })
    
    return {
        "questions_processed": len(questions),
        "answers_found": len([r for r in results if r["confidence"] > 0]),
        "results": results
    }

@router.post("/process-pdf")
async def process_pdf_questions(
    file: UploadFile = File(...),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """Process PDF and return answers from knowledge base"""
    # Extract text from PDF
    file_content = await file.read()
    text = await pdf_service.extract_text_from_pdf(file_content)
    
    # Extract questions using AI
    questions = await pdf_service.extract_questions_from_text(text)
    
    # Find answers in knowledge base
    results = []
    for question in questions:
        best_match = kb_service.get_best_answer(question, min_confidence=0.1)
        results.append({
            "question": question,
            "answer": best_match["answer"] if best_match else "No answer found in knowledge base",
            "confidence": best_match["confidence"] if best_match else 0.0,
            "source": best_match["id"] if best_match else None
        })
    
    return {
        "filename": file.filename,
        "questions_extracted": len(questions),
        "answers_found": len([r for r in results if r["confidence"] > 0]),
        "results": results
    }
```

## Frontend Components

### Knowledge Base Management Interface
```tsx
// src/components/KnowledgeBaseManager.tsx
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface KnowledgeBaseEntry {
  id: string;
  question: string;
  answer: string;
  tags: string[];
  category: string;
  created_at: string;
  updated_at: string;
}

export const KnowledgeBaseManager: React.FC = () => {
  const [entries, setEntries] = useState<KnowledgeBaseEntry[]>([]);
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [newEntry, setNewEntry] = useState({
    question: '',
    answer: '',
    tags: '',
    category: ''
  });

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    try {
      const data = await apiService.getKnowledgeBaseEntries();
      setEntries(data);
    } catch (error) {
      console.error('Error loading entries:', error);
    }
  };

  const addEntry = async () => {
    try {
      const tags = newEntry.tags.split(',').map(t => t.trim()).filter(t => t);
      await apiService.addKnowledgeBaseEntry({
        question: newEntry.question,
        answer: newEntry.answer,
        tags,
        category: newEntry.category
      });
      setNewEntry({ question: '', answer: '', tags: '', category: '' });
      loadEntries();
    } catch (error) {
      console.error('Error adding entry:', error);
    }
  };

  const deleteEntry = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      try {
        await apiService.deleteKnowledgeBaseEntry(id);
        loadEntries();
      } catch (error) {
        console.error('Error deleting entry:', error);
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">Knowledge Base Management</h1>
      
      {/* Add New Entry */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Add New Entry</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Question
            </label>
            <textarea
              value={newEntry.question}
              onChange={(e) => setNewEntry({...newEntry, question: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg"
              rows={3}
              placeholder="Enter the question..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Answer
            </label>
            <textarea
              value={newEntry.answer}
              onChange={(e) => setNewEntry({...newEntry, answer: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg"
              rows={3}
              placeholder="Enter the answer..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={newEntry.tags}
              onChange={(e) => setNewEntry({...newEntry, tags: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg"
              placeholder="stablecoin, partnerships, etc."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <input
              type="text"
              value={newEntry.category}
              onChange={(e) => setNewEntry({...newEntry, category: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg"
              placeholder="e.g., Technical, Business, Legal"
            />
          </div>
        </div>
        <button
          onClick={addEntry}
          className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Add Entry
        </button>
      </div>

      {/* Entries List */}
      <div className="bg-white rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold p-6 border-b">Knowledge Base Entries ({entries.length})</h2>
        <div className="divide-y">
          {entries.map((entry) => (
            <div key={entry.id} className="p-6">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-lg">{entry.question}</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setIsEditing(entry.id)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteEntry(entry.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <p className="text-gray-700 mb-2">{entry.answer}</p>
              <div className="flex flex-wrap gap-2">
                {entry.tags.map((tag) => (
                  <span key={tag} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                    {tag}
                  </span>
                ))}
                {entry.category && (
                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">
                    {entry.category}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

## Key Benefits of This Approach

1. **No Hallucinations**: Answers come only from curated knowledge base
2. **High Confidence**: Only returns answers with good similarity scores
3. **Full Control**: Complete CRUD operations on knowledge base
4. **Transparency**: Shows confidence scores and source information
5. **Scalable**: Easy to add new entries and categories
6. **Cost Effective**: Minimal AI usage (only for PDF question extraction)

## Migration from Current System

1. **Import existing JSON**: Convert your `rfp_kb.json` to PostgreSQL
2. **Keep existing logic**: Use your proven TF-IDF + cosine similarity
3. **Add management interface**: Build admin panel for knowledge base
4. **Enhance search**: Add full-text search capabilities
5. **Add PDF support**: Use AI only for question extraction

This approach gives you complete control over the knowledge base while leveraging AI only where it adds value (PDF processing) without risking inaccurate information.
