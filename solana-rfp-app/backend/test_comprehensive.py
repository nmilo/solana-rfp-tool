#!/usr/bin/env python3
"""
Comprehensive test for the export functionality
"""
import sys
import os
import uuid
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.export_service import ExportService
from app.models.schemas import ProcessingResult, QuestionResult
from app.models.database import QuestionSubmission
from datetime import datetime

def test_export_with_empty_answers():
    """Test export with empty answers to ensure proper handling"""
    
    # Create sample data with empty answers
    sample_results = [
        QuestionResult(
            question="What is Solana's consensus mechanism?",
            answer="Solana uses Proof of History (PoH) combined with Proof of Stake (PoS) for its consensus mechanism.",
            confidence=0.95,
            source_id=uuid.uuid4(),
            source_question="How does Solana consensus work?"
        ),
        QuestionResult(
            question="What are Solana's transaction fees?",
            answer="No answer found in knowledge base",
            confidence=0.0,
            source_id=None,
            source_question=None
        ),
        QuestionResult(
            question="How does Solana handle scalability?",
            answer="",  # Empty answer
            confidence=0.0,
            source_id=None,
            source_question=None
        ),
        QuestionResult(
            question="What programming languages can be used on Solana?",
            answer="Solana primarily supports Rust for smart contract development.",
            confidence=0.92,
            source_id=uuid.uuid4(),
            source_question="What languages are supported?"
        )
    ]
    
    processing_result = ProcessingResult(
        questions_processed=4,
        answers_found=2,
        results=sample_results,
        processing_time=2.5
    )
    
    export_service = ExportService()
    
    print("Testing PDF export with empty answers...")
    try:
        pdf_content = export_service.export_to_pdf(processing_result, "test_empty_answers")
        print(f"✓ PDF generated successfully ({len(pdf_content)} bytes)")
        
        # Check if PDF contains expected content
        pdf_text = pdf_content.decode('latin-1', errors='ignore')
        if "Answer to be provided manually" in pdf_text:
            print("✓ PDF correctly marks empty answers")
        else:
            print("⚠ PDF may not be handling empty answers correctly")
            
    except Exception as e:
        print(f"✗ PDF export failed: {e}")
    
    print("\nTesting DOCX export with empty answers...")
    try:
        docx_content = export_service.export_to_docx(processing_result, "test_empty_answers")
        print(f"✓ DOCX generated successfully ({len(docx_content)} bytes)")
        
    except Exception as e:
        print(f"✗ DOCX export failed: {e}")
    
    print("\nTesting filename generation...")
    try:
        pdf_filename = export_service.get_export_filename("pdf", "custom_test")
        docx_filename = export_service.get_export_filename("docx", "custom_test")
        
        print(f"✓ PDF filename: {pdf_filename}")
        print(f"✓ DOCX filename: {docx_filename}")
        
        # Verify filename format
        if pdf_filename.endswith('.pdf') and 'custom_test' in pdf_filename:
            print("✓ PDF filename format is correct")
        else:
            print("⚠ PDF filename format may be incorrect")
            
        if docx_filename.endswith('.docx') and 'custom_test' in docx_filename:
            print("✓ DOCX filename format is correct")
        else:
            print("⚠ DOCX filename format may be incorrect")
        
    except Exception as e:
        print(f"✗ Filename generation failed: {e}")

def test_api_endpoints():
    """Test that API endpoints can be imported and initialized"""
    try:
        from app.api.export import router
        from app.main import app
        print("✓ Export API endpoints can be imported")
        print("✓ Main app can be imported")
        
        # Check if export router is included
        routes = [route.path for route in app.routes]
        export_routes = [route for route in routes if '/export' in route]
        if export_routes:
            print(f"✓ Export routes found: {export_routes}")
        else:
            print("⚠ No export routes found in app")
            
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")

if __name__ == "__main__":
    print("=== Comprehensive Export Functionality Test ===\n")
    
    test_export_with_empty_answers()
    print("\n" + "="*50 + "\n")
    test_api_endpoints()
    
    print("\n=== Test Complete ===")
