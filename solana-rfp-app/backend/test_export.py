#!/usr/bin/env python3
"""
Test script for export functionality
"""
import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.export_service import ExportService
from app.models.schemas import ProcessingResult, QuestionResult
from datetime import datetime

def test_export_functionality():
    """Test the export service with sample data"""
    
    # Create sample data
    sample_results = [
        QuestionResult(
            question="What is Solana's consensus mechanism?",
            answer="Solana uses Proof of History (PoH) combined with Proof of Stake (PoS) for its consensus mechanism. PoH provides a verifiable time source that allows the network to agree on the order of events without having to wait for consensus.",
            confidence=0.95,
            source_id=uuid.uuid4(),
            source_question="How does Solana consensus work?"
        ),
        QuestionResult(
            question="What are Solana's transaction fees?",
            answer="Solana's transaction fees are extremely low, typically around $0.00025 per transaction. This is significantly lower than Ethereum and other major blockchains.",
            confidence=0.88,
            source_id=uuid.uuid4(),
            source_question="What are the costs of using Solana?"
        ),
        QuestionResult(
            question="How does Solana handle scalability?",
            answer="No answer found in knowledge base",
            confidence=0.0,
            source_id=None,
            source_question=None
        ),
        QuestionResult(
            question="What programming languages can be used on Solana?",
            answer="Solana primarily supports Rust for smart contract development, but also supports C and C++. The Solana Program Library (SPL) provides common programs and utilities.",
            confidence=0.92,
            source_id=uuid.uuid4(),
            source_question="What languages are supported for Solana development?"
        )
    ]
    
    processing_result = ProcessingResult(
        questions_processed=4,
        answers_found=3,
        results=sample_results,
        processing_time=2.5
    )
    
    # Initialize export service
    export_service = ExportService()
    
    print("Testing PDF export...")
    try:
        pdf_content = export_service.export_to_pdf(processing_result, "test_rfp_answers")
        print(f"✓ PDF generated successfully ({len(pdf_content)} bytes)")
        
        # Save to file for manual inspection
        with open("test_export.pdf", "wb") as f:
            f.write(pdf_content)
        print("✓ PDF saved as 'test_export.pdf'")
        
    except Exception as e:
        print(f"✗ PDF export failed: {e}")
    
    print("\nTesting DOCX export...")
    try:
        docx_content = export_service.export_to_docx(processing_result, "test_rfp_answers")
        print(f"✓ DOCX generated successfully ({len(docx_content)} bytes)")
        
        # Save to file for manual inspection
        with open("test_export.docx", "wb") as f:
            f.write(docx_content)
        print("✓ DOCX saved as 'test_export.docx'")
        
    except Exception as e:
        print(f"✗ DOCX export failed: {e}")
    
    print("\nTesting filename generation...")
    try:
        pdf_filename = export_service.get_export_filename("pdf", "custom_name")
        docx_filename = export_service.get_export_filename("docx")
        
        print(f"✓ PDF filename: {pdf_filename}")
        print(f"✓ DOCX filename: {docx_filename}")
        
    except Exception as e:
        print(f"✗ Filename generation failed: {e}")
    
    print("\nExport functionality test completed!")

if __name__ == "__main__":
    test_export_functionality()
