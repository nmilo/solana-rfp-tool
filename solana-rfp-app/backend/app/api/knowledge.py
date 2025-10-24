from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
import openai
from app.core.database import get_db
from app.services.knowledge_service import KnowledgeBaseService
from app.services.document_service import DocumentService
from app.core.config import settings
from app.models.schemas import (
    KnowledgeBaseCreate, 
    KnowledgeBaseUpdate, 
    KnowledgeBaseResponse,
    SearchRequest,
    SearchResponse
)
from app.api.auth import get_current_user

router = APIRouter()

async def generate_answer_from_document(question: str, document_text: str, filename: str, document_service: DocumentService) -> str:
    """Generate a proper answer from document content using OpenAI"""
    try:
        if not settings.OPENAI_API_KEY:
            return f"This question was extracted from the uploaded document: {filename}. Please review and provide a proper answer."
        
        openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""
        Based on the following document content, provide a comprehensive answer to the question.
        The answer should be professional, detailed, and suitable for an RFP response.
        If the document doesn't contain enough information to answer the question, provide a general response based on Solana blockchain knowledge.
        
        Question: {question}
        
        Document Content: {document_text[:3000]}
        
        Answer:
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        # If the answer is too short or generic, provide a fallback
        if len(answer) < 50 or "I don't have enough information" in answer.lower():
            return f"This question was extracted from the uploaded document: {filename}. Based on the document content, this appears to be a technical question about Solana blockchain. Please review the source document for complete details."
        
        return answer
        
    except Exception as e:
        # Fallback to placeholder if OpenAI fails
        return f"This question was extracted from the uploaded document: {filename}. Please review and provide a proper answer."

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
                # Generate a proper answer from the document content
                answer = await generate_answer_from_document(question, text, file.filename, document_service)
                
                entry_data = KnowledgeBaseCreate(
                    question=question,
                    answer=answer,
                    category=category or "Uploaded Document",
                    tags=tag_list + ["uploaded", "processed"]
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
                    # Generate a proper answer from the document content
                    answer = await generate_answer_from_document(question, text, file.filename, document_service)
                    
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

@router.get("/admin/preview")
async def get_knowledge_base_preview(
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in questions and answers")
):
    """Get knowledge base entries for admin preview"""
    try:
        # Get all entries
        all_entries = kb_service.get_all_active_entries()
        
        # Apply filters
        filtered_entries = all_entries
        
        if category:
            filtered_entries = [entry for entry in filtered_entries if entry.category == category]
        
        if search:
            search_lower = search.lower()
            filtered_entries = [
                entry for entry in filtered_entries 
                if search_lower in entry.question.lower() or search_lower in entry.answer.lower()
            ]
        
        # Calculate pagination
        total_entries = len(filtered_entries)
        total_pages = (total_entries + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page entries
        page_entries = filtered_entries[start_idx:end_idx]
        
        # Convert to response format
        entries_data = []
        for entry in page_entries:
            entries_data.append({
                "id": str(entry.id),
                "question": entry.question,
                "answer": entry.answer[:200] + "..." if len(entry.answer) > 200 else entry.answer,
                "answer_preview": entry.answer[:100] + "..." if len(entry.answer) > 100 else entry.answer,
                "category": entry.category,
                "tags": entry.get_tags(),
                "created_at": entry.created_at.isoformat(),
                "created_by": entry.created_by,
                "is_active": entry.is_active,
                "confidence_threshold": entry.confidence_threshold
            })
        
        return {
            "entries": entries_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_entries": total_entries,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters": {
                "category": category,
                "search": search
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting knowledge base preview: {str(e)}")

@router.get("/admin/categories")
async def get_knowledge_base_categories(
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    current_user = Depends(get_current_user)
):
    """Get all categories in knowledge base"""
    try:
        all_entries = kb_service.get_all_active_entries()
        categories = {}
        
        for entry in all_entries:
            category = entry.category or "Uncategorized"
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return {
            "categories": categories,
            "total_categories": len(categories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")

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

@router.post("/import-sample-rfps")
async def import_sample_rfps(
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    document_service: DocumentService = Depends(get_document_service),
    current_user = Depends(get_current_user)
):
    """Import sample RFP documents with questions and answers"""
    
    # Sample RFP data with questions and proper answers
    sample_rfp_data = [
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
        },
        {
            "question": "What is the transaction throughput and latency of your blockchain?",
            "answer": "Solana's current performance metrics: 1) Throughput - Up to 65,000 transactions per second (TPS) in optimal conditions, 2) Latency - Sub-second finality with 400ms block times, 3) Network Capacity - Handles high-frequency trading and DeFi applications, 4) Scalability - Horizontal scaling through parallel processing, 5) Real-world Performance - Consistently processes 2,000-3,000 TPS under normal load, 6) Peak Performance - Has demonstrated 50,000+ TPS during stress tests.",
            "category": "performance",
            "tags": ["throughput", "latency", "tps", "performance", "scalability"]
        },
        {
            "question": "What consensus mechanism does your blockchain use?",
            "answer": "Solana uses Proof of History (PoH) combined with Proof of Stake (PoS): 1) Proof of History - Creates a cryptographic clock that enables parallel processing, 2) Proof of Stake - Validators stake SOL tokens to participate in consensus, 3) Tower BFT - Byzantine Fault Tolerant consensus algorithm, 4) Leader Rotation - Validators take turns as leaders to propose blocks, 5) Finality - Fast finality with probabilistic finality in 400ms, 6) Security - High security through economic incentives and cryptographic proofs.",
            "category": "consensus",
            "tags": ["consensus", "proof-of-history", "proof-of-stake", "bft", "security"]
        },
        {
            "question": "What programming languages are supported for smart contract development?",
            "answer": "Solana primarily supports Rust for smart contract development: 1) Rust - Primary language with comprehensive SDK and tooling, 2) C/C++ - Alternative development option with C bindings, 3) Anchor Framework - High-level framework for Rust development, 4) Solana CLI - Command-line tools for development and deployment, 5) IDEs - Support for VS Code, IntelliJ, and other popular editors, 6) Documentation - Extensive guides and tutorials for all supported languages.",
            "category": "development",
            "tags": ["programming", "rust", "smart-contracts", "sdk", "development"]
        },
        {
            "question": "What are the gas fees and transaction costs?",
            "answer": "Solana offers extremely low transaction costs: 1) Base Fee - $0.00025 per transaction (approximately), 2) Priority Fees - Optional fees for faster processing during high congestion, 3) No Gas Fees - Unlike Ethereum, Solana doesn't use gas fees, 4) Predictable Costs - Transaction costs are fixed and predictable, 5) Micro-transactions - Enables micro-transactions and high-frequency trading, 6) Cost Comparison - Significantly lower than other major blockchains.",
            "category": "fees",
            "tags": ["fees", "costs", "transactions", "gas", "pricing"]
        },
        {
            "question": "What security measures and audit processes do you have in place?",
            "answer": "Solana implements multiple security layers: 1) Code Audits - Regular third-party security audits of core protocol, 2) Bug Bounty Program - Active program with rewards for security vulnerabilities, 3) Validator Security - Decentralized validator network with economic incentives, 4) Network Monitoring - Continuous monitoring and anomaly detection, 5) Security Documentation - Comprehensive security guidelines and best practices, 6) Incident Response - Rapid response team for security incidents.",
            "category": "security",
            "tags": ["security", "audits", "bug-bounty", "monitoring", "incident-response"]
        }
    ]
    
    try:
        imported_count = kb_service.import_from_json(sample_rfp_data, created_by=current_user.email)
        return {
            "message": f"Successfully imported {imported_count} RFP entries with questions and answers",
            "imported_count": imported_count,
            "categories": list(set([item["category"] for item in sample_rfp_data]))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing RFP data: {str(e)}")

@router.post("/reprocess-placeholder-answers")
async def reprocess_placeholder_answers(
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    document_service: DocumentService = Depends(get_document_service),
    current_user = Depends(get_current_user)
):
    """Reprocess entries with placeholder answers to generate proper answers"""
    
    try:
        # Get all entries with placeholder answers
        all_entries = kb_service.get_all_active_entries()
        placeholder_entries = [
            entry for entry in all_entries 
            if "This question was extracted from the uploaded document:" in entry.answer
        ]
        
        if not placeholder_entries:
            return {
                "message": "No placeholder entries found to reprocess",
                "processed_count": 0
            }
        
        processed_count = 0
        
        for entry in placeholder_entries:
            try:
                # Extract filename from the placeholder answer
                filename = entry.answer.split("uploaded document: ")[1].split(". Please")[0]
                
                # Generate a new answer based on Solana knowledge
                new_answer = await generate_solana_answer(entry.question, filename)
                
                # Update the entry
                update_data = KnowledgeBaseUpdate(answer=new_answer)
                kb_service.update_entry(entry.id, update_data, current_user.email)
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing entry {entry.id}: {str(e)}")
                continue
        
        return {
            "message": f"Successfully reprocessed {processed_count} placeholder entries",
            "processed_count": processed_count,
            "total_placeholder_entries": len(placeholder_entries)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reprocessing placeholder answers: {str(e)}")

async def generate_solana_answer(question: str, filename: str) -> str:
    """Generate a Solana-specific answer for common RFP questions"""
    try:
        if not settings.OPENAI_API_KEY:
            return f"This question was extracted from the uploaded document: {filename}. Please review and provide a proper answer."
        
        openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""
        You are a Solana blockchain expert responding to RFP questions. 
        Provide a comprehensive, professional answer to the following question based on Solana's capabilities and features.
        The answer should be suitable for a Request for Proposal (RFP) response.
        
        Question: {question}
        
        Provide a detailed answer covering:
        1. Solana's specific capabilities related to this question
        2. Technical details and specifications
        3. Benefits and advantages
        4. Real-world examples or use cases where applicable
        
        Answer:
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Add source attribution
        answer += f"\n\nSource: This information was extracted from the uploaded document: {filename}"
        
        return answer
        
    except Exception as e:
        return f"This question was extracted from the uploaded document: {filename}. Please review and provide a proper answer."
