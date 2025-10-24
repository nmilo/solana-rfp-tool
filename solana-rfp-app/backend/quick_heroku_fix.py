#!/usr/bin/env python3
"""
Quick fix for Heroku timeout issues
Adds file size limits and better error handling
"""

# Add this to your upload endpoint in knowledge.py

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit for Heroku
MAX_QUESTIONS_PER_FILE = 10  # Limit questions to prevent timeout

def validate_file_size(content: bytes) -> bool:
    """Validate file size for Heroku limits"""
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB. Please use a smaller file or contact support."
        )
    return True

def limit_questions(questions: list) -> list:
    """Limit number of questions to prevent timeout"""
    if len(questions) > MAX_QUESTIONS_PER_FILE:
        return questions[:MAX_QUESTIONS_PER_FILE]
    return questions

# Updated upload endpoint logic:
"""
@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['pdf', 'docx', 'doc', 'xlsx', 'xls']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Supported formats: pdf, docx, doc, xlsx, xls"
            )
        
        # Read and validate file content
        content = await file.read()
        validate_file_size(content)  # Check file size
        
        # Process document
        if file_extension == 'pdf':
            questions = await pdf_service.extract_questions_from_pdf(content)
        elif file_extension in ['docx', 'doc']:
            questions = await pdf_service.extract_questions_from_docx(content)
        elif file_extension in ['xlsx', 'xls']:
            questions = await pdf_service.extract_questions_from_excel(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        if not questions:
            return {
                "message": "No questions found in document",
                "questions_extracted": 0,
                "entries_added": 0
            }
        
        # Limit questions to prevent timeout
        original_count = len(questions)
        questions = limit_questions(questions)
        
        # Add questions to knowledge base
        entries_added = 0
        for question in questions:
            try:
                answer = await generate_answer_from_document(question, content, file_extension)
                
                entry_data = KnowledgeBaseCreate(
                    question=question,
                    answer=answer,
                    tags=["uploaded", "processed"] + (tags.split(',') if tags else []),
                    category=category or "Uploaded Document"
                )
                
                result = kb_service.add_entry(entry_data, created_by=current_user.email)
                if result.get("success"):
                    entries_added += 1
                    
            except Exception as e:
                print(f"Error adding question '{question}': {str(e)}")
                continue
        
        message = f"Document processed successfully"
        if original_count > MAX_QUESTIONS_PER_FILE:
            message += f" (processed first {MAX_QUESTIONS_PER_FILE} of {original_count} questions due to size limits)"
        
        return {
            "message": message,
            "questions_extracted": original_count,
            "entries_added": entries_added,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
"""
