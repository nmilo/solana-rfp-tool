from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from app.core.database import get_db
from app.services.knowledge_service import KnowledgeBaseService
from app.services.document_service import DocumentService
from app.models.schemas import (
    KnowledgeBaseCreate, 
    KnowledgeBaseUpdate, 
    KnowledgeBaseResponse,
    SearchRequest,
    SearchResponse
)
from app.api.auth import get_current_user

router = APIRouter()

def get_kb_service(db: Session = Depends(get_db)) -> KnowledgeBaseService:
    return KnowledgeBaseService(db)

def get_document_service() -> DocumentService:
    return DocumentService()

@router.get("/entries", response_model=List[KnowledgeBaseResponse])
async def get_all_entries(
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Get all knowledge base entries with optional filtering"""
    tag_list = tags.split(',') if tags else None
    entries = kb_service.get_all_entries(category=category, tags=tag_list)
    return entries

@router.post("/entries", response_model=KnowledgeBaseResponse)
async def add_entry(
    entry: KnowledgeBaseCreate,
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Add new knowledge base entry"""
    try:
        result = kb_service.add_entry(entry, created_by=current_user.email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/entries/{entry_id}", response_model=KnowledgeBaseResponse)
async def update_entry(
    entry_id: str,
    update: KnowledgeBaseUpdate,
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Update knowledge base entry"""
    try:
        result = kb_service.update_entry(entry_id, update, modified_by=current_user.email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Delete knowledge base entry"""
    success = kb_service.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted successfully"}

@router.get("/search", response_model=SearchResponse)
async def search_knowledge_base(
    query: str = Query(..., description="Search query"),
    min_confidence: float = Query(0.1, description="Minimum confidence threshold"),
    limit: int = Query(10, description="Maximum number of results"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Search knowledge base for answers"""
    matches = kb_service.search_answers(query, min_confidence)
    
    # Apply limit
    limited_matches = matches[:limit]
    
    return SearchResponse(
        query=query,
        matches=limited_matches,
        total_matches=len(matches)
    )

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    document_service: DocumentService = Depends(get_document_service),
    current_user = Depends(get_current_user)
):
    """Upload and process a document to add to knowledge base"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    file_extension = file.filename.lower().split('.')[-1]
    supported_formats = ['pdf', 'docx', 'doc', 'xlsx', 'xls']
    if file_extension not in supported_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Supported formats: {', '.join(supported_formats)}")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from document
        text = await document_service.extract_text_from_file(file_content, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail=f"No text could be extracted from the {file_extension.upper()} file")
        
        # Extract questions from text
        try:
            questions = await document_service.extract_questions_from_text(text)
        except ValueError:
            # Fallback to simple extraction
            questions = document_service.extract_questions_simple(text)
        
        if not questions:
            raise HTTPException(status_code=400, detail="No questions could be extracted from the document")
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        # Add questions to knowledge base
        added_entries = []
        skipped_entries = []
        
        for question in questions:
            try:
                # Create a basic answer placeholder
                answer = f"This question was extracted from the uploaded document: {file.filename}. Please review and provide a proper answer."
                
                entry_data = KnowledgeBaseCreate(
                    question=question,
                    answer=answer,
                    category=category or "Uploaded Document",
                    tags=tag_list + ["uploaded", "needs-review"]
                )
                
                result = kb_service.add_entry(entry_data, created_by=current_user.email)
                added_entries.append(result)
                
            except ValueError as e:
                # Skip duplicate entries
                skipped_entries.append({"question": question, "reason": str(e)})
        
        return {
            "message": f"Document processed successfully",
            "filename": file.filename,
            "extracted_questions": len(questions),
            "added_entries": len(added_entries),
            "skipped_entries": len(skipped_entries),
            "added_questions": [entry["question"] for entry in added_entries],
            "skipped_questions": [entry["question"] for entry in skipped_entries]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/upload-multiple-documents")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    document_service: DocumentService = Depends(get_document_service),
    current_user = Depends(get_current_user)
):
    """Upload and process multiple documents to add to knowledge base"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Limit to 10 files at once
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
    
    # Validate all files first
    supported_formats = ['pdf', 'docx', 'doc', 'xlsx', 'xls']
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail=f"File {file.filename} has no name")
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in supported_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported file format '{file_extension}' in {file.filename}. Supported formats: {', '.join(supported_formats)}")
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
    
    # Process files concurrently
    async def process_single_file(file: UploadFile) -> dict:
        try:
            # Read file content
            file_content = await file.read()
            
            # Extract text from document
            text = await document_service.extract_text_from_file(file_content, file.filename)
            
            if not text.strip():
                return {
                    "filename": file.filename,
                    "status": "error",
                    "error": f"No text could be extracted from the {file.filename.split('.')[-1].upper()} file",
                    "extracted_questions": 0,
                    "added_entries": 0,
                    "skipped_entries": 0,
                    "added_questions": [],
                    "skipped_questions": []
                }
            
            # Extract questions from text
            try:
                questions = await document_service.extract_questions_from_text(text)
            except ValueError:
                # Fallback to simple extraction
                questions = document_service.extract_questions_simple(text)
            
            if not questions:
                return {
                    "filename": file.filename,
                    "status": "error",
                    "error": "No questions could be extracted from the document",
                    "extracted_questions": 0,
                    "added_entries": 0,
                    "skipped_entries": 0,
                    "added_questions": [],
                    "skipped_questions": []
                }
            
            # Add questions to knowledge base
            added_entries = []
            skipped_entries = []
            
            for question in questions:
                try:
                    # Create a basic answer placeholder
                    answer = f"This question was extracted from the uploaded document: {file.filename}. Please review and provide a proper answer."
                    
                    entry_data = KnowledgeBaseCreate(
                        question=question,
                        answer=answer,
                        category=category or "Uploaded Document",
                        tags=tag_list + ["uploaded", "needs-review"]
                    )
                    
                    result = kb_service.add_entry(entry_data, created_by=current_user.email)
                    added_entries.append(result)
                    
                except ValueError as e:
                    # Skip duplicate entries
                    skipped_entries.append({"question": question, "reason": str(e)})
            
            return {
                "filename": file.filename,
                "status": "success",
                "extracted_questions": len(questions),
                "added_entries": len(added_entries),
                "skipped_entries": len(skipped_entries),
                "added_questions": [entry["question"] for entry in added_entries],
                "skipped_questions": [entry["question"] for entry in skipped_entries]
            }
            
        except Exception as e:
            return {
                "filename": file.filename,
                "status": "error",
                "error": f"Error processing document: {str(e)}",
                "extracted_questions": 0,
                "added_entries": 0,
                "skipped_entries": 0,
                "added_questions": [],
                "skipped_questions": []
            }
    
    # Process all files concurrently
    results = await asyncio.gather(*[process_single_file(file) for file in files])
    
    # Calculate totals
    total_files = len(files)
    successful_files = len([r for r in results if r["status"] == "success"])
    failed_files = total_files - successful_files
    total_questions = sum(r["extracted_questions"] for r in results)
    total_added = sum(r["added_entries"] for r in results)
    total_skipped = sum(r["skipped_entries"] for r in results)
    
    return {
        "message": f"Processed {total_files} files: {successful_files} successful, {failed_files} failed",
        "total_files": total_files,
        "successful_files": successful_files,
        "failed_files": failed_files,
        "total_extracted_questions": total_questions,
        "total_added_entries": total_added,
        "total_skipped_entries": total_skipped,
        "file_results": results
    }

@router.get("/stats")
async def get_knowledge_base_stats(
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Get knowledge base statistics"""
    entries = kb_service.get_all_entries()
    
    # Calculate stats
    total_entries = len(entries)
    categories = {}
    tags = {}
    
    for entry in entries:
        # Count categories
        if entry["category"]:
            categories[entry["category"]] = categories.get(entry["category"], 0) + 1
        
        # Count tags
        for tag in entry["tags"]:
            tags[tag] = tags.get(tag, 0) + 1
    
    return {
        "total_entries": total_entries,
        "categories": categories,
        "top_tags": dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10])
    }

@router.post("/initialize")
async def initialize_knowledge_base(
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Initialize knowledge base with sample data"""
    # Sample knowledge base data
    sample_data = [
        {
            "question": "Are there support and training programs for developers?",
            "answer": "Yes, Solana Foundation provides comprehensive support and training programs for developers including: 1) Solana University - free online courses covering blockchain basics to advanced development, 2) Developer Bootcamps - intensive hands-on training sessions, 3) Hackathons - regular competitions with prizes and mentorship, 4) Technical Documentation - extensive guides and tutorials, 5) Community Support - active Discord channels and forums, 6) Grant Programs - funding for innovative projects, 7) Mentorship Programs - pairing with experienced developers.",
            "category": "developer_support",
            "tags": ["support", "training", "developers", "education", "grants"]
        },
        {
            "question": "Do you have testnets? Do you provide faucets for them?",
            "answer": "Yes, Solana operates multiple testnets: 1) Devnet - for development and testing, 2) Testnet - for integration testing, 3) Mainnet Beta - production network. Faucets are available for Devnet and Testnet to provide free SOL tokens for testing. The main faucet is at https://faucet.solana.com/ and provides up to 2 SOL per request for development purposes.",
            "category": "testnets",
            "tags": ["testnet", "devnet", "faucet", "testing", "sol"]
        },
        {
            "question": "Do you provide faucets or institutional access to tokens for testnets?",
            "answer": "Yes, Solana provides both public faucets and institutional access: 1) Public Faucets - Available at https://faucet.solana.com/ for individual developers, 2) Institutional Faucets - For organizations requiring larger amounts, contact the Solana Foundation for custom faucet access, 3) API Access - Programmatic faucet access available for automated testing, 4) Partner Faucets - Third-party services also provide faucet functionality.",
            "category": "faucets",
            "tags": ["faucet", "institutional", "api", "testing", "tokens"]
        },
        {
            "question": "Do you organize hackathons or events for developers? Locations, attendees, results of previous events?",
            "answer": "Yes, Solana Foundation organizes numerous hackathons and events globally: 1) Solana Hacker Houses - Regular events in major cities (San Francisco, New York, London, Tokyo, Singapore), 2) Online Hackathons - Virtual events with global participation, 3) University Partnerships - Campus events at leading universities, 4) Previous Results - Over 10,000 developers have participated, with $50M+ in prizes awarded, 5) Notable Winners - Projects like Magic Eden, Jupiter, and Orca started as hackathon projects, 6) Upcoming Events - Check https://solana.com/events for current schedule.",
            "category": "events",
            "tags": ["hackathons", "events", "developers", "prizes", "global"]
        },
        {
            "question": "What are the key partnerships you have in the stablecoin sector?",
            "answer": "The Solana network is open and permissionless; stablecoin issuers don't need a formal agreement with the Foundation. However, the Foundation actively supports issuers informally with technical, ecosystem, and business advisory. Examples include PayPal (PYUSD, leveraging token extensions for compliance features), Paxos (USDP, first post-Ethereum NYDFS approval), USDT (~$0.7 B supply), and EURC by Circle.",
            "category": "stablecoins",
            "tags": ["stablecoin", "partnerships", "paypal", "paxos", "usdc", "usdt", "eurc"]
        }
    ]
    
    try:
        imported_count = kb_service.import_from_json(sample_data, created_by=current_user.email)
        return {
            "message": f"Successfully initialized knowledge base with {imported_count} entries",
            "imported_count": imported_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing knowledge base: {str(e)}")
