#!/usr/bin/env python3
"""
Script to properly process the MXNB Questions Excel file and extract all Q&A pairs
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

def process_excel_file():
    """Process the Excel file and extract Q&A pairs"""
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
            
            # Display first few rows to understand structure
            print(f"📊 First 5 rows:")
            print(df.head())
            
            # Try to identify question and answer columns
            question_col = None
            answer_col = None
            
            # Look for common column names
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['question', 'q', 'ask', 'inquiry']):
                    question_col = col
                elif any(keyword in col_lower for keyword in ['answer', 'a', 'response', 'reply']):
                    answer_col = col
            
            if question_col and answer_col:
                print(f"✅ Found Q&A columns: '{question_col}' -> '{answer_col}'")
                
                # Extract Q&A pairs
                for index, row in df.iterrows():
                    question = str(row[question_col]).strip()
                    answer = str(row[answer_col]).strip()
                    
                    # Skip empty or NaN values
                    if (question and answer and 
                        question != 'nan' and answer != 'nan' and
                        len(question) > 10 and len(answer) > 10):
                        
                        all_qa_pairs.append({
                            'question': question,
                            'answer': answer,
                            'sheet': sheet_name,
                            'row': index + 1
                        })
            else:
                print(f"⚠️  Could not identify Q&A columns in sheet '{sheet_name}'")
                print(f"   Available columns: {list(df.columns)}")
                
                # Try to process as single column with questions
                for col in df.columns:
                    if df[col].dtype == 'object':  # Text column
                        print(f"📝 Processing column '{col}' as potential questions")
                        for index, row in df.iterrows():
                            text = str(row[col]).strip()
                            if (text and text != 'nan' and len(text) > 10 and 
                                ('?' in text or any(keyword in text.lower() for keyword in ['what', 'how', 'when', 'where', 'why', 'which', 'who']))):
                                all_qa_pairs.append({
                                    'question': text,
                                    'answer': f"This question was extracted from the MXNB Questions Excel file, sheet '{sheet_name}'. Please provide a comprehensive answer based on Solana blockchain capabilities.",
                                    'sheet': sheet_name,
                                    'row': index + 1
                                })
        
        print(f"\n🎉 Extracted {len(all_qa_pairs)} Q&A pairs from Excel file")
        return all_qa_pairs
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
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
                "category": "MXNB Questions",
                "tags": ["mxnb", "excel", "questions", qa_pair['sheet'].lower().replace(' ', '-')]
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
    # Process the Excel file
    qa_pairs = process_excel_file()
    
    if qa_pairs:
        # Upload to API
        upload_qa_pairs_to_api(qa_pairs)
    else:
        print("❌ No Q&A pairs found to upload")
