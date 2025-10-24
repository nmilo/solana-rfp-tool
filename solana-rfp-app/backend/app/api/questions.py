from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import time
import json
from app.core.database import get_db
from app.services.knowledge_service import KnowledgeBaseService
from app.services.pdf_service import PDFService
from app.models.schemas import TextQuestionRequest, ProcessingResult, QuestionResult
from app.models.database import QuestionSubmission
from app.api.auth import get_current_user

router = APIRouter()

def get_kb_service(db: Session = Depends(get_db)) -> KnowledgeBaseService:
    return KnowledgeBaseService(db)

def get_pdf_service() -> PDFService:
    return PDFService()

def extract_questions_from_text(text: str) -> list:
    """Extract questions from text using your existing logic"""
    import re
    
    # Your existing question extraction logic from autoresponder.py
    QUESTION_TRIGGERS = [
        "please provide", "please share", "kindly provide", "kindly share",
        "provide a", "provide the", "provide your",
        "please tell us", "let us know", "could you", "can you",
        "we would appreciate", "we'd appreciate", "we would like to request",
        "we'd like to request", "we request", "request if you can share",
        "we'd like to ask", "we would like to ask",
        "how does", "how do", "how is", "how are", "how will",
        "what is", "what are", "what's", "which", "when", "why",
        "justify", "outline", "explain", "describe", "bsp:"
    ]
    
    BULLET_RE = re.compile(r"^\s*(?:[\-\*\u2022]|\d+\)|\d+\.)\s+")
    
    def looks_like_question(s: str) -> bool:
        low = s.lower().strip()
        if low.endswith("?"):
            return True
        if BULLET_RE.match(s) and any(tr in low for tr in QUESTION_TRIGGERS):
            return True
        if any(tr in low for tr in QUESTION_TRIGGERS):
            return True
        if re.match(r"^\s*(provide|outline|explain|describe|justify)\b", low):
            return True
        if re.match(r"^\s*(bsp|regulator)\s*:\s*", low):
            return True
        return False
    
    def split_on_question_marks(s: str):
        # Don't split compound questions - treat the whole text as one question if it contains question marks
        s = s.strip()
        if not s:
            return []
        
        # If it's a single line with multiple question marks, treat as one compound question
        if '\n' not in s and s.count('?') > 1:
            return [s]
        
        # Otherwise, split on question marks as before
        parts = re.split(r"(\?)", s)
        out, acc = [], ""
        for seg in parts:
            acc += seg
            if seg == "?":
                out.append(acc.strip()); acc = ""
        if acc.strip():
            out.append(acc.strip())
        return out
    
    # Clean and extract questions
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates = []
    
    for line in lines:
        for piece in split_on_question_marks(line):
            if looks_like_question(piece):
                candidates.append(piece)
    
    # Remove duplicates and short questions
    seen, questions = set(), []
    for q in candidates:
        qn = q.lower().strip()
        if len(qn) >= 15 and qn not in seen:
            seen.add(qn)
            questions.append(q.strip())
    
    return questions

@router.post("/process-text", response_model=ProcessingResult)
async def process_text_questions(
    request: TextQuestionRequest,
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Process text questions and return answers from knowledge base"""
    start_time = time.time()
    
    # Extract questions from text
    questions = extract_questions_from_text(request.text)
    
    if not questions:
        return ProcessingResult(
            questions_processed=0,
            answers_found=0,
            results=[],
            processing_time=time.time() - start_time
        )
    
    # Find answers using priority system (exact match first, then AI fallback)
    results = []
    for question in questions:
        answer_data = await kb_service.get_answer_with_ai_fallback(question, min_confidence=0.1)
        results.append(QuestionResult(
            question=question,
            answer=answer_data["answer"],
            confidence=answer_data["confidence"],
            source_id=answer_data["source_id"],
            source_question=answer_data["source_question"]
        ))
    
        # Save submission to database
        submission = QuestionSubmission(
            input_type="text",
            raw_input=request.text,
            extracted_questions=json.dumps(questions),
            matched_answers=json.dumps([{
                "question": r.question,
                "answer": r.answer,
                "confidence": r.confidence,
                "source_id": str(r.source_id) if r.source_id else None,
                "source_question": r.source_question
            } for r in results]),
            confidence_scores=json.dumps([r.confidence for r in results]),
            processing_status="completed"
        )
    db.add(submission)
    db.commit()
    
    return ProcessingResult(
        questions_processed=len(questions),
        answers_found=len([r for r in results if r.confidence > 0]),
        results=results,
        processing_time=time.time() - start_time,
        submission_id=submission.id
    )

@router.post("/process-pdf", response_model=ProcessingResult)
async def process_pdf_questions(
    file: UploadFile = File(...),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    pdf_service: PDFService = Depends(get_pdf_service),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Process PDF and return answers from knowledge base"""
    start_time = time.time()
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Extract text from PDF
        file_content = await file.read()
        text = await pdf_service.extract_text_from_pdf(file_content)
        
        # Extract questions using AI (if available) or simple extraction
        try:
            questions = await pdf_service.extract_questions_from_text(text)
        except:
            # Fallback to simple extraction
            questions = pdf_service.extract_questions_simple(text)
        
        if not questions:
            return ProcessingResult(
                questions_processed=0,
                answers_found=0,
                results=[],
                processing_time=time.time() - start_time
            )
        
        # Find answers in knowledge base
        results = []
        for question in questions:
            best_match = kb_service.get_best_answer(question, min_confidence=0.1)
            results.append(QuestionResult(
                question=question,
                answer=best_match["answer"] if best_match else "No answer found in knowledge base",
                confidence=best_match["confidence"] if best_match else 0.0,
                source_id=best_match["id"] if best_match else None,
                source_question=best_match["question"] if best_match else None
            ))
        
        # Save submission to database
        submission = QuestionSubmission(
            input_type="pdf",
            raw_input=f"PDF: {file.filename}",
            extracted_questions=json.dumps(questions),
            matched_answers=json.dumps([{
                "question": r.question,
                "answer": r.answer,
                "confidence": r.confidence,
                "source_id": str(r.source_id) if r.source_id else None,
                "source_question": r.source_question
            } for r in results]),
            confidence_scores=json.dumps([r.confidence for r in results]),
            processing_status="completed"
        )
        db.add(submission)
        db.commit()
        
        return ProcessingResult(
            questions_processed=len(questions),
            answers_found=len([r for r in results if r.confidence > 0]),
            results=results,
            processing_time=time.time() - start_time,
            submission_id=submission.id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.get("/submissions")
async def get_recent_submissions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent question submissions"""
    submissions = db.query(QuestionSubmission).order_by(
        QuestionSubmission.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": sub.id,
            "input_type": sub.input_type,
            "raw_input": sub.raw_input[:100] + "..." if len(sub.raw_input) > 100 else sub.raw_input,
            "questions_count": len(json.loads(sub.extracted_questions)) if sub.extracted_questions else 0,
            "answers_found": len([c for c in json.loads(sub.confidence_scores) if c > 0]) if sub.confidence_scores else 0,
            "created_at": sub.created_at.isoformat(),
            "status": sub.processing_status
        }
        for sub in submissions
    ]
