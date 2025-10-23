from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import json
import io

from app.core.database import get_db
from app.models.schemas import ProcessingResult, QuestionResult
from app.models.database import QuestionSubmission
from app.services.export_service import ExportService
from app.api.auth import get_current_user

router = APIRouter()

def get_export_service() -> ExportService:
    return ExportService()

@router.post("/pdf")
async def export_to_pdf(
    submission_id: str = Query(..., description="Submission ID"),
    custom_filename: Optional[str] = Query(None, description="Custom filename"),
    db: Session = Depends(get_db),
    export_service: ExportService = Depends(get_export_service),
    current_user = Depends(get_current_user)
):
    """Export Q&A results to PDF format"""
    try:
        # Get submission from database
        submission = db.query(QuestionSubmission).filter(
            QuestionSubmission.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Parse the stored data
        questions = json.loads(submission.extracted_questions) if submission.extracted_questions else []
        matched_answers = json.loads(submission.matched_answers) if submission.matched_answers else []
        confidence_scores = json.loads(submission.confidence_scores) if submission.confidence_scores else []
        
        # Create ProcessingResult object
        results = []
        for i, question in enumerate(questions):
            answer_data = matched_answers[i] if i < len(matched_answers) else {}
            confidence = confidence_scores[i] if i < len(confidence_scores) else 0.0
            
            results.append(QuestionResult(
                question=question,
                answer=answer_data.get("answer", "No answer found in knowledge base"),
                confidence=confidence,
                source_id=answer_data.get("source_id"),
                source_question=answer_data.get("source_question")
            ))
        
        processing_result = ProcessingResult(
            questions_processed=len(questions),
            answers_found=len([r for r in results if r.confidence > 0]),
            results=results
        )
        
        # Generate PDF
        pdf_content = export_service.export_to_pdf(processing_result, custom_filename)
        filename = export_service.get_export_filename("pdf", custom_filename)
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.post("/docx")
async def export_to_docx(
    submission_id: str = Query(..., description="Submission ID"),
    custom_filename: Optional[str] = Query(None, description="Custom filename"),
    db: Session = Depends(get_db),
    export_service: ExportService = Depends(get_export_service),
    current_user = Depends(get_current_user)
):
    """Export Q&A results to DOCX format"""
    try:
        # Get submission from database
        submission = db.query(QuestionSubmission).filter(
            QuestionSubmission.id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Parse the stored data
        questions = json.loads(submission.extracted_questions) if submission.extracted_questions else []
        matched_answers = json.loads(submission.matched_answers) if submission.matched_answers else []
        confidence_scores = json.loads(submission.confidence_scores) if submission.confidence_scores else []
        
        # Create ProcessingResult object
        results = []
        for i, question in enumerate(questions):
            answer_data = matched_answers[i] if i < len(matched_answers) else {}
            confidence = confidence_scores[i] if i < len(confidence_scores) else 0.0
            
            results.append(QuestionResult(
                question=question,
                answer=answer_data.get("answer", "No answer found in knowledge base"),
                confidence=confidence,
                source_id=answer_data.get("source_id"),
                source_question=answer_data.get("source_question")
            ))
        
        processing_result = ProcessingResult(
            questions_processed=len(questions),
            answers_found=len([r for r in results if r.confidence > 0]),
            results=results
        )
        
        # Generate DOCX
        docx_content = export_service.export_to_docx(processing_result, custom_filename)
        filename = export_service.get_export_filename("docx", custom_filename)
        
        # Return DOCX as streaming response
        return StreamingResponse(
            io.BytesIO(docx_content),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating DOCX: {str(e)}")

@router.post("/pdf/direct")
async def export_to_pdf_direct(
    results: ProcessingResult,
    custom_filename: Optional[str] = Query(None, description="Custom filename"),
    export_service: ExportService = Depends(get_export_service),
    current_user = Depends(get_current_user)
):
    """Export Q&A results directly to PDF format (for immediate export)"""
    try:
        # Generate PDF
        pdf_content = export_service.export_to_pdf(results, custom_filename)
        filename = export_service.get_export_filename("pdf", custom_filename)
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.post("/docx/direct")
async def export_to_docx_direct(
    results: ProcessingResult,
    custom_filename: Optional[str] = Query(None, description="Custom filename"),
    export_service: ExportService = Depends(get_export_service),
    current_user = Depends(get_current_user)
):
    """Export Q&A results directly to DOCX format (for immediate export)"""
    try:
        # Generate DOCX
        docx_content = export_service.export_to_docx(results, custom_filename)
        filename = export_service.get_export_filename("docx", custom_filename)
        
        # Return DOCX as streaming response
        return StreamingResponse(
            io.BytesIO(docx_content),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating DOCX: {str(e)}")
