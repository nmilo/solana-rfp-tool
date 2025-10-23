# Solana RFP Tool

An intelligent RFP (Request for Proposal) question answering system that automatically processes RFP documents and generates responses using a curated knowledge base.

## Features

- **Question Extraction**: Automatically extracts questions from email text or PDF documents
- **Knowledge Base Matching**: Uses TF-IDF and cosine similarity to find relevant answers
- **Multiple Output Formats**: Generates responses in both Markdown and Word document formats
- **Web Application**: Modern React frontend with FastAPI backend (in development)
- **PDF Processing**: Extract questions from PDF documents using AI
- **Admin Interface**: Manage knowledge base entries through web interface

## Quick Start

### Using the Command Line Tool

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Autoresponder**:
   ```bash
   python src/autoresponder.py --kb kb/rfp_kb.json --in samples/mercari_email.txt --out output/response
   ```

3. **View Results**:
   - Check `output/response.md` for the generated response
   - Check `output/response.docx` for the Word document version

### Using the Web Application

1. **Start the Backend**:
   ```bash
   cd solana-rfp-app/backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Start the Frontend**:
   ```bash
   cd solana-rfp-app/frontend
   npm install
   npm start
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Project Structure

```
├── src/
│   └── autoresponder.py          # Core RFP processing logic
├── kb/
│   └── rfp_kb.json              # Knowledge base (questions & answers)
├── samples/
│   ├── mercari_email.txt        # Sample email input
│   └── pjli_bsp.txt            # Sample BSP input
├── output/
│   ├── response.md              # Generated markdown response
│   └── response.docx            # Generated Word document
├── solana-rfp-app/             # Web application
│   ├── backend/                # FastAPI backend
│   └── frontend/               # React frontend
├── architecture.md             # System architecture documentation
├── implementation_plan.md      # Development roadmap
└── revised_architecture.md     # Updated architecture design
```

## Knowledge Base

The system uses a JSON-based knowledge base (`kb/rfp_kb.json`) containing:
- **Questions**: Common RFP questions
- **Answers**: Corresponding responses
- **Tags**: Categorization tags for better matching

## How It Works

1. **Input Processing**: Extracts questions from email text or PDF documents
2. **Question Detection**: Uses pattern matching and AI to identify questions
3. **Knowledge Matching**: Applies TF-IDF vectorization and cosine similarity
4. **Answer Generation**: Retrieves best matching answers from knowledge base
5. **Response Formatting**: Generates professional email responses

## Configuration

### Command Line Options

- `--kb`: Path to knowledge base JSON file
- `--in`: Input file path (email text)
- `--out`: Output file prefix
- `--counterparty`: Name of the RFP sender
- `--min_score`: Minimum similarity score threshold (default: 0.10)
- `--top_answers`: Number of top answers to include (default: 1)
- `--debug`: Enable debug output

### Environment Variables

For the web application:
- `OPENAI_API_KEY`: OpenAI API key for PDF processing
- `DATABASE_URL`: PostgreSQL database connection string
- `SECRET_KEY`: JWT secret key for authentication

## Development

### Adding New Knowledge Base Entries

1. Edit `kb/rfp_kb.json`
2. Add new question-answer pairs with appropriate tags
3. Test with sample inputs

### Web Application Development

The web application is built with:
- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL
- **AI Integration**: OpenAI GPT-4 for PDF processing

See `implementation_plan.md` for detailed development roadmap.

## Architecture

The system follows a hybrid approach:
- **No AI for answer generation** - Only retrieves from curated knowledge base
- **AI only for question extraction** from PDFs
- **High confidence matching** - Returns "No answer found" for low-confidence matches
- **Full knowledge base management** - Add, edit, delete, search entries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open a GitHub issue or contact the development team.

## Roadmap

- [ ] Complete web application development
- [ ] Add user authentication
- [ ] Implement advanced search features
- [ ] Add analytics and reporting
- [ ] Deploy to production environment
