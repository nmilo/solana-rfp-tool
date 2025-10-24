#!/usr/bin/env python3
"""
Fix MXNB answers in knowledge base
Replace incorrect answers with correct ones from MXNB Excel file
"""
import requests
import json
import pandas as pd
from pathlib import Path

def get_mxnb_correct_answers():
    """Get correct answers from MXNB Excel file"""
    excel_file = Path("/Users/manda/solana-rfp-tool/Kb raw/(MXNB) Questions (1).xlsx")
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file, sheet_name='MXNB Questions')
        
        # Find Q&A pairs (columns 3 and 5)
        questions_col = 'Unnamed: 3'
        answers_col = 'Unnamed: 5'
        
        qa_pairs = []
        for idx, row in df.iterrows():
            question = str(row[questions_col]).strip() if pd.notna(row[questions_col]) else ""
            answer = str(row[answers_col]).strip() if pd.notna(row[answers_col]) else ""
            
            if question and answer and question != "nan" and answer != "nan":
                qa_pairs.append({
                    "question": question,
                    "answer": answer
                })
        
        return qa_pairs
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        return []

def get_knowledge_base_entries():
    """Get all entries from knowledge base"""
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    try:
        response = requests.get(
            f"{api_url}/api/v1/knowledge/admin/preview?page=1&page_size=100",
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("entries", [])
        else:
            print(f"❌ Failed to get entries: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting entries: {str(e)}")
        return []

def delete_entry(entry_id: str):
    """Delete an entry from knowledge base"""
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    try:
        response = requests.delete(
            f"{api_url}/api/v1/knowledge/entries/{entry_id}",
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to delete entry {entry_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting entry {entry_id}: {str(e)}")
        return False

def add_correct_entry(question: str, answer: str):
    """Add correct entry to knowledge base"""
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    try:
        entry_data = {
            "question": question,
            "answer": answer,
            "category": "MXNB Q&A Pairs",
            "tags": ["mxnb", "excel", "qa-pairs", "correct-answers"]
        }
        
        response = requests.post(
            f"{api_url}/api/v1/knowledge/entries",
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            },
            json=entry_data
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to add entry: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error adding entry: {str(e)}")
        return False

def main():
    """Fix MXNB answers in knowledge base"""
    print("🔍 Getting correct answers from MXNB Excel file...")
    correct_answers = get_mxnb_correct_answers()
    
    if not correct_answers:
        print("❌ No correct answers found")
        return
    
    print(f"📊 Found {len(correct_answers)} correct Q&A pairs")
    
    print("🔍 Getting current knowledge base entries...")
    current_entries = get_knowledge_base_entries()
    
    if not current_entries:
        print("❌ No current entries found")
        return
    
    print(f"📊 Found {len(current_entries)} current entries")
    
    # Find entries that need to be fixed
    entries_to_fix = []
    
    for correct_qa in correct_answers:
        correct_question = correct_qa["question"].lower().strip()
        correct_answer = correct_qa["answer"]
        
        for entry in current_entries:
            current_question = entry["question"].lower().strip()
            current_answer = entry["answer"]
            
            # Check if this is a match but with wrong answer
            if (correct_question == current_question and 
                correct_answer != current_answer):
                entries_to_fix.append({
                    "entry_id": entry["id"],
                    "question": correct_qa["question"],
                    "current_answer": current_answer,
                    "correct_answer": correct_answer
                })
    
    print(f"🔧 Found {len(entries_to_fix)} entries to fix")
    
    if not entries_to_fix:
        print("✅ No entries need fixing")
        return
    
    # Fix the entries
    fixed_count = 0
    for fix_item in entries_to_fix:
        print(f"\n🔧 Fixing: {fix_item['question'][:50]}...")
        print(f"   Current: {fix_item['current_answer'][:50]}...")
        print(f"   Correct: {fix_item['correct_answer'][:50]}...")
        
        # Delete incorrect entry
        if delete_entry(fix_item["entry_id"]):
            print("   ✅ Deleted incorrect entry")
            
            # Add correct entry
            if add_correct_entry(fix_item["question"], fix_item["correct_answer"]):
                print("   ✅ Added correct entry")
                fixed_count += 1
            else:
                print("   ❌ Failed to add correct entry")
        else:
            print("   ❌ Failed to delete incorrect entry")
    
    print(f"\n🎉 Fixed {fixed_count} entries")

if __name__ == "__main__":
    main()

