#!/usr/bin/env python3
"""
Script to correctly extract Q&A pairs from the MXNB Questions Excel file
"""
import pandas as pd
import requests
import json
from pathlib import Path

def get_excel_file_path():
    """Get the path to the MXNB Questions Excel file"""
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent.parent
    excel_file = project_root / "Kb raw" / "(MXNB) Questions (1).xlsx"
    return excel_file

def extract_qa_pairs():
    """Extract Q&A pairs from the Excel file"""
    excel_path = get_excel_file_path()
    
    if not excel_path.exists():
        print(f"❌ Excel file not found: {excel_path}")
        return []
    
    print(f"📊 Processing Excel file: {excel_path}")
    
    try:
        # Read the Excel file
        excel_file = pd.ExcelFile(excel_path)
        print(f"📋 Found sheets: {excel_file.sheet_names}")
        
        all_qa_pairs = []
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n📄 Processing sheet: {sheet_name}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            print(f"📊 Sheet dimensions: {df.shape}")
            print(f"📊 Columns: {list(df.columns)}")
            
            # Based on the analysis, questions are in column 3 (Unnamed: 3) and answers in column 5 (Unnamed: 5)
            question_col = 'Unnamed: 3'
            answer_col = 'Unnamed: 5'
            
            if question_col in df.columns and answer_col in df.columns:
                print(f"✅ Found Q&A columns: '{question_col}' -> '{answer_col}'")
                
                # Extract Q&A pairs
                for index, row in df.iterrows():
                    question = str(row[question_col]).strip() if pd.notna(row[question_col]) else ""
                    answer = str(row[answer_col]).strip() if pd.notna(row[answer_col]) else ""
                    
                    # Skip empty, NaN, or header rows
                    if (question and answer and 
                        question != 'nan' and answer != 'nan' and
                        question != 'Item' and answer != 'Answer' and
                        len(question) > 10 and len(answer) > 20):
                        
                        # Clean up the question and answer
                        question = question.replace('\n', ' ').replace('\r', ' ')
                        answer = answer.replace('\n', ' ').replace('\r', ' ')
                        
                        all_qa_pairs.append({
                            'question': question,
                            'answer': answer,
                            'sheet': sheet_name,
                            'row': index + 1
                        })
                        
                        print(f"📝 Found Q&A pair {len(all_qa_pairs)}:")
                        print(f"   Q: {question[:80]}...")
                        print(f"   A: {answer[:80]}...")
                        print()
            else:
                print(f"❌ Could not find expected Q&A columns")
                print(f"   Available columns: {list(df.columns)}")
        
        print(f"\n🎉 Total extracted Q&A pairs: {len(all_qa_pairs)}")
        return all_qa_pairs
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def upload_qa_pairs_to_api(qa_pairs):
    """Upload Q&A pairs to the API"""
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    successful_uploads = 0
    failed_uploads = 0
    
    for i, qa_pair in enumerate(qa_pairs):
        print(f"📤 Uploading {i+1}/{len(qa_pairs)}: {qa_pair['question'][:50]}...")
        
        try:
            data = {
                "question": qa_pair['question'],
                "answer": qa_pair['answer'],
                "category": "MXNB Q&A Pairs",
                "tags": ["mxnb", "excel", "qa-pairs", "original-answers"]
            }
            
            response = requests.post(
                f"{api_url}/api/v1/knowledge/entries",
                json=data,
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            if response.status_code == 200:
                successful_uploads += 1
                print(f"  ✅ Success")
            else:
                failed_uploads += 1
                print(f"  ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            failed_uploads += 1
            print(f"  ❌ Error: {str(e)}")
    
    print(f"\n📊 Upload Summary:")
    print(f"  ✅ Successful: {successful_uploads}")
    print(f"  ❌ Failed: {failed_uploads}")
    print(f"  📊 Total: {len(qa_pairs)}")

if __name__ == "__main__":
    # Extract Q&A pairs from Excel
    qa_pairs = extract_qa_pairs()
    
    if qa_pairs:
        # Upload to API
        upload_qa_pairs_to_api(qa_pairs)
    else:
        print("❌ No Q&A pairs found to upload")
