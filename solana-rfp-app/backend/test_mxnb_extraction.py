#!/usr/bin/env python3
"""
Test MXNB extraction with the hybrid processor
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_document_processor import AIDocumentProcessor

async def test_mxnb_extraction():
    """Test extraction with MXNB file"""
    print("🧪 Testing MXNB Extraction...")
    
    # Path to MXNB file
    mxnb_file = "/Users/manda/solana-rfp-tool/Kb raw/(MXNB) Questions (1).xlsx"
    
    if not os.path.exists(mxnb_file):
        print(f"❌ MXNB file not found: {mxnb_file}")
        return
    
    try:
        processor = AIDocumentProcessor()
        
        # Extract Q&A pairs
        print("\n📊 Extracting Q&A pairs from MXNB file...")
        qa_pairs = await processor.extract_qa_from_excel(mxnb_file, "(MXNB) Questions (1).xlsx")
        
        print(f"\n✅ Extraction complete!")
        print(f"📈 Total Q&A pairs found: {len(qa_pairs)}")
        
        # Show first 5 pairs
        print("\n📝 Sample Q&A pairs:")
        for i, qa in enumerate(qa_pairs[:5], 1):
            print(f"\n{i}. Question: {qa['question'][:100]}...")
            print(f"   Answer: {qa['answer'][:100]}...")
        
        # Show statistics
        print(f"\n📊 Statistics:")
        print(f"- Total pairs: {len(qa_pairs)}")
        print(f"- Avg question length: {sum(len(qa['question']) for qa in qa_pairs) / len(qa_pairs):.0f} chars")
        print(f"- Avg answer length: {sum(len(qa['answer']) for qa in qa_pairs) / len(qa_pairs):.0f} chars")
        
        # Test embedding generation
        print(f"\n🧠 Testing embedding generation...")
        if qa_pairs:
            embedding = await processor.generate_embedding(qa_pairs[0]['question'])
            if embedding:
                print(f"✅ Embedding generated: {len(embedding)} dimensions")
            else:
                print(f"❌ Failed to generate embedding")
        
        print(f"\n🎉 Test complete! System is ready to process MXNB files!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mxnb_extraction())
