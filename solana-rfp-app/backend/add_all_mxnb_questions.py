#!/usr/bin/env python3
"""
Add all MXNB questions and answers to the knowledge base
"""

import requests
import json
import time
import os

# Heroku backend URL
BASE_URL = "https://solana-rfp-271974794838.herokuapp.com"
AUTH_TOKEN = "mock-jwt-token-demo"

def add_knowledge_entry(question, answer, category="MXNB Q&A Pairs", tags=None):
    """Add a knowledge base entry"""
    if tags is None:
        tags = ["mxnb", "rfp", "solana", "blockchain"]
    
    url = f"{BASE_URL}/api/v1/knowledge/entries"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "question": question,
        "answer": answer,
        "category": category,
        "tags": tags
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Added: {question[:60]}...")
            return result
        else:
            print(f"❌ Failed to add: {question[:60]}... - {response.status_code}")
            if response.status_code == 409:  # Conflict - entry already exists
                print(f"   (Entry already exists, skipping)")
                return None
            else:
                print(f"   Response: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Error adding: {question[:60]}... - {str(e)}")
        return None

def load_mxnb_qa_pairs():
    """Load Q&A pairs from the JSON file"""
    try:
        with open('/Users/manda/solana-rfp-tool/mxnb_qa_pairs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ mxnb_qa_pairs.json not found. Please run the extraction script first.")
        return None
    except Exception as e:
        print(f"❌ Error loading Q&A pairs: {str(e)}")
        return None

def main():
    """Add all MXNB Q&A pairs to knowledge base"""
    
    print("🚀 Adding all MXNB questions and answers to knowledge base...")
    
    # Load Q&A pairs
    qa_pairs = load_mxnb_qa_pairs()
    if not qa_pairs:
        return
    
    print(f"📊 Total Q&A pairs to add: {len(qa_pairs)}")
    
    success_count = 0
    skipped_count = 0
    
    for i, qa in enumerate(qa_pairs, 1):
        print(f"\n[{i}/{len(qa_pairs)}] Adding question...")
        
        # Clean up the question and answer
        question = qa["question"].strip()
        answer = qa["answer"].strip()
        
        # Skip if question or answer is too short
        if len(question) < 10 or len(answer) < 5:
            print(f"⏭️ Skipping short entry: {question[:30]}...")
            skipped_count += 1
            continue
        
        result = add_knowledge_entry(
            question=question,
            answer=answer,
            category="MXNB Q&A Pairs",
            tags=["mxnb", "rfp", "solana", "blockchain", "stablecoin"]
        )
        
        if result:
            success_count += 1
        elif result is None and "already exists" in str(result):
            skipped_count += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.3)
    
    print(f"\n🎯 Summary:")
    print(f"✅ Successfully added: {success_count}")
    print(f"⏭️ Skipped (already exists): {skipped_count}")
    print(f"❌ Failed: {len(qa_pairs) - success_count - skipped_count}")
    print(f"📊 Total processed: {len(qa_pairs)}")
    
    if success_count > 0:
        print("\n🎉 MXNB questions successfully added to knowledge base!")
        print("🔍 You can now test the questions in your RFP tool.")
    else:
        print("\n⚠️ No new questions were added. They may already exist in the knowledge base.")

if __name__ == "__main__":
    main()
