# Solana RFP Database

A modern web application for managing and querying RFP knowledge base with AI-powered question extraction from PDFs.

## Features

- **Knowledge Base Management**: Add, edit, delete, and search knowledge base entries
- **Question Processing**: Submit text questions or upload PDFs for automatic question extraction
- **AI-Powered PDF Processing**: Extract questions from RFP documents using OpenAI GPT-4
- **Confidence Scoring**: Shows match quality for each answer
- **Arena-Inspired Design**: Modern, dark-themed UI inspired by Colosseum Arena
- **Real-time Search**: Fast search through knowledge base with filtering

## Architecture

- **Backend**: FastAPI with SQLAlchemy and PostgreSQL
- **Frontend**: React with TypeScript and Tailwind CSS
- **AI Integration**: OpenAI GPT-4 for PDF question extraction only
- **Search**: TF-IDF + cosine similarity for knowledge base retrieval

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (optional, SQLite for development)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your settings
```

5. Import existing knowledge base:
```bash
python import_kb.py ../../kb/rfp_kb.json
```

6. Start the server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## API Endpoints

### Knowledge Base
- `GET /api/v1/knowledge/entries` - Get all entries
- `POST /api/v1/knowledge/entries` - Add new entry
- `PUT /api/v1/knowledge/entries/{id}` - Update entry
- `DELETE /api/v1/knowledge/entries/{id}` - Delete entry
- `GET /api/v1/knowledge/search` - Search entries
- `GET /api/v1/knowledge/stats` - Get statistics

### Question Processing
- `POST /api/v1/questions/process-text` - Process text questions
- `POST /api/v1/questions/process-pdf` - Process PDF questions
- `GET /api/v1/questions/submissions` - Get recent submissions

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./solana_rfp.db
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your-secret-key-change-in-production
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

## Usage

### Adding Knowledge Base Entries

1. Go to the Admin page
2. Fill in the question, answer, tags, and category
3. Click "Add Entry"

### Processing Questions

1. Go to the Home page
2. Choose "Text Input" or "PDF Upload"
3. Submit your questions or upload a PDF
4. View the results with confidence scores

### Searching Knowledge Base

1. Go to the Knowledge Base page
2. Use the search bar to find specific entries
3. Filter by category or browse all entries

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm start
```

### Database Migrations
```bash
cd backend
alembic upgrade head
```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
1. Build frontend: `npm run build`
2. Serve backend with production WSGI server
3. Configure reverse proxy (nginx)
4. Set up SSL certificates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
