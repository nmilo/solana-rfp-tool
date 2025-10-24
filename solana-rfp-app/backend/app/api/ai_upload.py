"""
API endpoints for AI-powered document upload with automatic Q&A extraction
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from app.services.ai_document_processor import AIDocumentProcessor
from app.api.auth import get_current_user
from app.core.logger import main_logger
import tempfile
import os

router = APIRouter()

@router.post("/upload-document-ai")
async def upload_document_with_ai(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a document and automatically extract Q&A pairs using AI
    Supports: TXT, MD, CSV, XLSX, XLS
    """
    try:
        main_logger.info(f"AI document upload: {file.filename}")
        
        # Validate file type
        file_ext = file.filename.split('.')[-1].lower()
        supported_types = ['txt', 'md', 'csv', 'xlsx', 'xls']
        
        if file_ext not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(supported_types)}"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process document with AI
            processor = AIDocumentProcessor()
            result = await processor.process_document(
                file_path=tmp_file_path,
                file_type=file_ext,
                filename=file.filename
            )
            
            return {
                "status": "success" if result['success'] else "error",
                "filename": file.filename,
                "message": result['message'],
                "qa_pairs_found": result['qa_count'],
                "qa_pairs_stored": result['stored_count'],
                "preview": result.get('qa_pairs', [])
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
        
    except Exception as e:
        main_logger.error(f"Error in AI document upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-multiple-documents-ai")
async def upload_multiple_documents_with_ai(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple documents and automatically extract Q&A pairs using AI
    """
    try:
        main_logger.info(f"AI batch upload: {len(files)} files")
        
        temp_files = []
        file_types = []
        filenames = []
        
        # Save all files temporarily
        for file in files:
            file_ext = file.filename.split('.')[-1].lower()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_files.append(tmp_file.name)
                file_types.append(file_ext)
                filenames.append(file.filename)
        
        try:
            # Process all documents
            processor = AIDocumentProcessor()
            result = await processor.batch_process_documents(
                file_paths=temp_files,
                file_types=file_types,
                filenames=filenames
            )
            
            return {
                "status": "success",
                "total_files": result['total_documents'],
                "total_qa_pairs": result['total_qa_pairs'],
                "results": result['results']
            }
            
        finally:
            # Clean up all temporary files
            for tmp_path in temp_files:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
    except Exception as e:
        main_logger.error(f"Error in AI batch upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-qa-preview")
async def extract_qa_preview(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Preview Q&A extraction without storing (for testing)
    """
    try:
        file_ext = file.filename.split('.')[-1].lower()
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            processor = AIDocumentProcessor()
            
            if file_ext in ['xlsx', 'xls']:
                qa_pairs = await processor.extract_qa_from_excel(tmp_file_path, file.filename)
            else:
                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                qa_pairs = await processor.extract_qa_from_text(text_content, file.filename)
            
            return {
                "status": "success",
                "filename": file.filename,
                "qa_count": len(qa_pairs),
                "qa_pairs": qa_pairs
            }
            
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
        
    except Exception as e:
        main_logger.error(f"Error in preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
