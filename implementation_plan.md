# Solana RFP Database - Implementation Plan

## Quick Start Implementation

Based on your existing `autoresponder.py`, I recommend starting with a **FastAPI backend** that leverages your current code and gradually building the web interface.

## Phase 1: Backend API (Week 1-2)

### 1.1 FastAPI Backend Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # Database models
│   │   └── schemas.py          # Pydantic schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── questions.py        # Question processing endpoints
│   │   ├── knowledge.py        # Knowledge base management
│   │   └── pdf.py             # PDF processing endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py   # OpenAI integration
│   │   ├── pdf_service.py      # PDF processing
│   │   └── knowledge_service.py # Knowledge base operations
│   └── core/
│       ├── __init__.py
│       ├── config.py           # Configuration
│       └── database.py         # Database connection
├── requirements.txt
└── Dockerfile
```

### 1.2 Key Dependencies
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
python-multipart>=0.0.6
openai>=1.3.0
pypdf2>=3.0.0
python-docx>=1.1.0
scikit-learn>=1.3.0
numpy>=1.24.0
pydantic>=2.5.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

## Phase 2: Frontend (Week 3-4)

### 2.1 React Frontend Structure
```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── QuestionInput.tsx
│   │   ├── PDFUploader.tsx
│   │   ├── AnswerDisplay.tsx
│   │   ├── KnowledgeBaseViewer.tsx
│   │   └── AdminPanel.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── AdminPage.tsx
│   │   └── ResultsPage.tsx
│   ├── services/
│   │   └── api.ts
│   ├── hooks/
│   │   └── useQuestions.ts
│   ├── types/
│   │   └── index.ts
│   └── App.tsx
├── package.json
└── Dockerfile
```

## Implementation Code Examples

### Backend: FastAPI Main Application

```python
# app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.api import questions, knowledge, pdf
from app.core.config import settings

app = FastAPI(
    title="Solana RFP Database API",
    description="AI-powered RFP question answering system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(pdf.router, prefix="/api/v1/pdf", tags=["pdf"])

@app.get("/")
async def root():
    return {"message": "Solana RFP Database API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Backend: Question Processing Service

```python
# app/services/knowledge_service.py
import json
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from app.core.config import settings

class KnowledgeService:
    def __init__(self):
        self.kb_data = self.load_knowledge_base()
        self.vectorizer, self.X, self.corpus = self.build_retriever()
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def load_knowledge_base(self) -> List[Dict]:
        """Load knowledge base from JSON file"""
        kb_path = Path("kb/rfp_kb.json")
        with open(kb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def build_retriever(self):
        """Build TF-IDF vectorizer for knowledge base"""
        corpus = [
            self.normalize_text(
                item.get("question", "") + " " + 
                item.get("answer", "") + " " + 
                " ".join(item.get("tags", []))
            ) 
            for item in self.kb_data
        ]
        vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        X = vectorizer.fit_transform(corpus)
        return vectorizer, X, corpus
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for processing"""
        import re
        text = text.lower()
        text = re.sub(r"[^\w\s\-\.]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    
    async def process_question(self, question: str) -> Dict[str, Any]:
        """Process a single question and return answer"""
        # Use existing logic from autoresponder.py
        qn = self.normalize_text(question)
        qv = self.vectorizer.transform([qn])
        sims = cosine_similarity(qv, self.X)[0]
        
        # Get best match
        best_idx = sims.argmax()
        best_score = sims[best_idx]
        
        if best_score < 0.1:  # Low confidence threshold
            return {
                "question": question,
                "answer": "I don't have enough information to answer this question accurately.",
                "confidence": float(best_score),
                "source": None
            }
        
        kb_item = self.kb_data[best_idx]
        return {
            "question": question,
            "answer": kb_item["answer"],
            "confidence": float(best_score),
            "source": kb_item
        }
    
    async def enhance_answer_with_openai(self, question: str, kb_answer: str) -> str:
        """Use OpenAI to enhance the knowledge base answer"""
        prompt = f"""
        Based on the following knowledge base answer, provide a comprehensive and professional response to the RFP question.
        
        Question: {question}
        Knowledge Base Answer: {kb_answer}
        
        Please enhance this answer to be more detailed, professional, and suitable for an RFP response while maintaining accuracy.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return kb_answer  # Fallback to original answer
```

### Backend: PDF Processing Service

```python
# app/services/pdf_service.py
import PyPDF2
import io
from typing import List, Dict
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
            raise HTTPException(status_code=400, detail=f"Error extracting PDF text: {str(e)}")
    
    async def extract_questions_from_text(self, text: str) -> List[str]:
        """Use OpenAI to extract questions from PDF text"""
        prompt = f"""
        Extract all questions from the following RFP document text. Return only the questions, one per line, without numbering or bullet points.
        
        Text: {text[:4000]}  # Limit to avoid token limits
        
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
            raise HTTPException(status_code=500, detail=f"Error extracting questions: {str(e)}")
```

### Frontend: Main Question Input Component

```tsx
// src/components/QuestionInput.tsx
import React, { useState } from 'react';
import { useQuestions } from '../hooks/useQuestions';

interface QuestionInputProps {
  onResults: (results: any) => void;
}

export const QuestionInput: React.FC<QuestionInputProps> = ({ onResults }) => {
  const [inputType, setInputType] = useState<'text' | 'pdf'>('text');
  const [textInput, setTextInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const { submitQuestions, uploadPDF } = useQuestions();

  const handleTextSubmit = async () => {
    if (!textInput.trim()) return;
    
    setIsProcessing(true);
    try {
      const results = await submitQuestions(textInput);
      onResults(results);
    } catch (error) {
      console.error('Error processing questions:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePDFUpload = async (file: File) => {
    setIsProcessing(true);
    try {
      const results = await uploadPDF(file);
      onResults(results);
    } catch (error) {
      console.error('Error processing PDF:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Solana RFP Database
        </h1>
        
        {/* Input Type Selection */}
        <div className="mb-6">
          <div className="flex space-x-4">
            <button
              onClick={() => setInputType('text')}
              className={`px-4 py-2 rounded-lg font-medium ${
                inputType === 'text'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Text Input
            </button>
            <button
              onClick={() => setInputType('pdf')}
              className={`px-4 py-2 rounded-lg font-medium ${
                inputType === 'pdf'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              PDF Upload
            </button>
          </div>
        </div>

        {/* Text Input */}
        {inputType === 'text' && (
          <div className="space-y-4">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Enter your RFP questions here..."
              className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleTextSubmit}
              disabled={isProcessing || !textInput.trim()}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? 'Processing...' : 'Submit Questions'}
            </button>
          </div>
        )}

        {/* PDF Upload */}
        {inputType === 'pdf' && (
          <div className="space-y-4">
            <PDFUploader onUpload={handlePDFUpload} isProcessing={isProcessing} />
          </div>
        )}
      </div>
    </div>
  );
};
```

### Frontend: API Service

```typescript
// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface QuestionResult {
  question: string;
  answer: string;
  confidence: number;
  source?: any;
}

export interface ProcessingResult {
  questions: QuestionResult[];
  processing_time: number;
  total_questions: number;
}

export const apiService = {
  async submitQuestions(text: string): Promise<ProcessingResult> {
    const response = await api.post('/api/v1/questions/submit', {
      input_type: 'text',
      content: text,
    });
    return response.data;
  },

  async uploadPDF(file: File): Promise<ProcessingResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/v1/pdf/extract-questions', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async searchKnowledgeBase(query: string): Promise<any[]> {
    const response = await api.get('/api/v1/knowledge/search', {
      params: { query, limit: 10 }
    });
    return response.data;
  },
};
```

## Development Setup

### 1. Backend Setup
```bash
# Create backend directory
mkdir solana-rfp-backend
cd solana-rfp-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
# Create frontend directory
npx create-react-app solana-rfp-frontend --template typescript
cd solana-rfp-frontend

# Install additional dependencies
npm install axios tailwindcss @headlessui/react @heroicons/react
npm install -D @types/node

# Start development server
npm start
```

### 3. Environment Configuration
```bash
# Backend .env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost/solana_rfp
SECRET_KEY=your_secret_key_here

# Frontend .env
REACT_APP_API_URL=http://localhost:8000
```

## Next Steps

1. **Start with Backend**: Implement the FastAPI backend with your existing logic
2. **Add OpenAI Integration**: Enhance answers with GPT-4
3. **Build Frontend**: Create React components for user interaction
4. **Add PDF Processing**: Implement PDF upload and question extraction
5. **Database Integration**: Move from JSON to PostgreSQL
6. **Deploy**: Use Docker for easy deployment

This approach leverages your existing `autoresponder.py` code while building a modern web application that can scale and provide a better user experience.
