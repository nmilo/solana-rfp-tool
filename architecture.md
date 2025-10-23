# Solana RFP Database - Web Application Architecture

## Overview
A comprehensive web application that provides intelligent RFP question answering using a knowledge base, with support for both text input and PDF document processing.

## Technology Stack

### Frontend
- **Framework**: React.js with TypeScript
- **UI Library**: Tailwind CSS + Headless UI
- **State Management**: Zustand or Redux Toolkit
- **File Upload**: React Dropzone
- **PDF Viewer**: React-PDF
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python) - leverages existing autoresponder.py
- **Database**: PostgreSQL with pgvector extension for vector similarity
- **Vector Database**: Pinecone or Weaviate (for semantic search)
- **File Storage**: AWS S3 or local storage
- **PDF Processing**: PyPDF2 + OpenAI API
- **Authentication**: JWT tokens

### AI/ML Services
- **OpenAI API**: GPT-4 for question extraction and answer generation
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Search**: Hybrid approach (TF-IDF + semantic similarity)

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev) / Kubernetes (prod)
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Database      │
                    │   (PostgreSQL)  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Vector DB     │
                    │   (Pinecone)    │
                    └─────────────────┘
```

## Database Schema

### Core Tables

#### knowledge_base
```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tags TEXT[],
    category VARCHAR(100),
    confidence_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

#### user_sessions
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    metadata JSONB
);
```

#### question_submissions
```sql
CREATE TABLE question_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES user_sessions(id),
    input_type ENUM('text', 'pdf'),
    raw_input TEXT,
    extracted_questions JSONB,
    generated_answers JSONB,
    confidence_scores JSONB,
    processing_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### pdf_documents
```sql
CREATE TABLE pdf_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES user_sessions(id),
    filename VARCHAR(255),
    file_path VARCHAR(500),
    file_size BIGINT,
    extracted_text TEXT,
    processing_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Core Endpoints

#### POST /api/v1/questions/submit
```json
{
  "input_type": "text|pdf",
  "content": "string",
  "session_id": "uuid"
}
```

#### POST /api/v1/questions/extract-from-pdf
```json
{
  "file": "multipart/form-data",
  "session_id": "uuid"
}
```

#### GET /api/v1/questions/{submission_id}/status
```json
{
  "status": "processing|completed|failed",
  "progress": 0-100,
  "results": {...}
}
```

#### GET /api/v1/knowledge/search
```json
{
  "query": "string",
  "limit": 10,
  "threshold": 0.7
}
```

### Admin Endpoints

#### POST /api/v1/admin/knowledge/add
#### PUT /api/v1/admin/knowledge/{id}
#### DELETE /api/v1/admin/knowledge/{id}
#### GET /api/v1/admin/analytics

## AI Processing Pipeline

### 1. Question Extraction (PDF)
```
PDF Upload → Text Extraction → OpenAI GPT-4 → Question List
```

### 2. Answer Generation
```
Question → Vector Search → Knowledge Base → OpenAI GPT-4 → Structured Answer
```

### 3. Quality Assurance
```
Generated Answer → Confidence Scoring → Human Review Flag → Final Answer
```

## Frontend Components

### Main Components
- **QuestionInput**: Text area for manual questions
- **PDFUploader**: Drag & drop PDF upload with progress
- **QuestionList**: Display extracted questions
- **AnswerDisplay**: Show generated answers with confidence scores
- **KnowledgeBaseViewer**: Browse/search knowledge base
- **AdminPanel**: Manage knowledge base entries

### User Flow
1. User lands on homepage
2. Chooses input method (text or PDF)
3. Submits questions/documents
4. System processes and extracts questions
5. Generates answers from knowledge base
6. Displays results with confidence scores
7. Option to refine or ask follow-up questions

## Security Considerations

### Authentication & Authorization
- JWT-based session management
- Rate limiting on API endpoints
- Input validation and sanitization
- CORS configuration

### Data Protection
- Encrypted file storage
- Secure PDF processing
- API key management for OpenAI
- Audit logging

## Performance Optimizations

### Caching Strategy
- Redis for session data
- CDN for static assets
- Database query optimization
- Vector search indexing

### Scalability
- Horizontal scaling with load balancers
- Database read replicas
- Async processing for heavy operations
- Queue system for PDF processing

## Deployment Strategy

### Development Environment
```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://...
      - OPENAI_API_KEY=...
  
  database:
    image: postgres:15
    environment:
      - POSTGRES_DB=solana_rfp
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
```

### Production Deployment
- AWS/GCP/Azure cloud deployment
- Kubernetes orchestration
- CI/CD pipeline with GitHub Actions
- Monitoring and alerting setup

## Cost Estimation

### Monthly Costs (Estimated)
- **OpenAI API**: $200-500 (depending on usage)
- **Database**: $50-100 (PostgreSQL hosting)
- **Vector DB**: $100-200 (Pinecone)
- **File Storage**: $20-50 (S3)
- **Hosting**: $100-300 (Cloud instances)
- **Total**: ~$470-1150/month

## Development Timeline

### Phase 1 (2-3 weeks)
- Backend API development
- Database setup and migration
- Basic question processing

### Phase 2 (2-3 weeks)
- Frontend development
- PDF upload and processing
- OpenAI integration

### Phase 3 (1-2 weeks)
- Admin panel
- Analytics and monitoring
- Testing and optimization

### Phase 4 (1 week)
- Deployment and production setup
- Documentation and training

## Next Steps

1. **Environment Setup**: Create development environment with Docker
2. **Database Migration**: Convert existing JSON knowledge base to PostgreSQL
3. **API Development**: Build core FastAPI endpoints
4. **Frontend Development**: Create React application
5. **AI Integration**: Implement OpenAI API calls
6. **Testing**: Comprehensive testing suite
7. **Deployment**: Production deployment and monitoring

## Risk Mitigation

### Technical Risks
- **OpenAI API limits**: Implement caching and fallback mechanisms
- **PDF processing failures**: Robust error handling and retry logic
- **Vector search accuracy**: Hybrid approach with multiple similarity metrics

### Business Risks
- **Cost overruns**: Monitor API usage and implement rate limiting
- **Data privacy**: Ensure compliance with data protection regulations
- **Scalability**: Design for horizontal scaling from the start
