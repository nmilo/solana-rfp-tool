#!/usr/bin/env python3
"""
Script to properly extract Q&A pairs from the MXNB Questions Excel file
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
            
            # Display more rows to understand the structure
            print(f"📊 First 10 rows:")
            print(df.head(10))
            
            # Try different approaches to find Q&A pairs
            qa_pairs = []
            
            # Approach 1: Look for columns that might contain questions and answers
            for i, col in enumerate(df.columns):
                print(f"\n🔍 Analyzing column {i}: '{col}'")
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    print(f"   Sample values: {col_data.head(3).tolist()}")
            
            # Approach 2: Look for patterns in the data
            # Check if there are rows that look like questions followed by answers
            for index, row in df.iterrows():
                row_data = [str(cell) for cell in row.values if pd.notna(cell) and str(cell) != 'nan']
                if len(row_data) >= 2:
                    # Check if first item looks like a question
                    first_item = row_data[0].strip()
                    if (len(first_item) > 10 and 
                        ('?' in first_item or 
                         any(keyword in first_item.lower() for keyword in ['what', 'how', 'when', 'where', 'why', 'which', 'who', 'do you', 'can you', 'would you', 'are you', 'is your', 'does your']))):
                        
                        # Look for answer in subsequent columns
                        for j in range(1, len(row_data)):
                            answer = row_data[j].strip()
                            if len(answer) > 20:  # Reasonable answer length
                                qa_pairs.append({
                                    'question': first_item,
                                    'answer': answer,
                                    'sheet': sheet_name,
                                    'row': index + 1,
                                    'method': 'row_analysis'
                                })
                                break
            
            # Approach 3: Look for question-answer patterns across columns
            # Check if we have alternating question/answer columns
            for i in range(0, len(df.columns) - 1, 2):
                col1 = df.columns[i]
                col2 = df.columns[i + 1]
                
                print(f"\n🔍 Checking columns {i} and {i+1}: '{col1}' and '{col2}'")
                
                for index, row in df.iterrows():
                    q_val = str(row[col1]) if pd.notna(row[col1]) else ""
                    a_val = str(row[col2]) if pd.notna(row[col2]) else ""
                    
                    if (q_val != 'nan' and a_val != 'nan' and 
                        len(q_val) > 10 and len(a_val) > 20 and
                        ('?' in q_val or any(keyword in q_val.lower() for keyword in ['what', 'how', 'when', 'where', 'why', 'which', 'who', 'do you', 'can you', 'would you', 'are you', 'is your', 'does your']))):
                        
                        qa_pairs.append({
                            'question': q_val.strip(),
                            'answer': a_val.strip(),
                            'sheet': sheet_name,
                            'row': index + 1,
                            'method': f'columns_{i}_{i+1}'
                        })
            
            # Approach 4: Look for specific patterns in the data
            # Sometimes Q&A might be in a single column separated by patterns
            for col in df.columns:
                col_data = df[col].dropna()
                for index, cell in col_data.items():
                    cell_str = str(cell).strip()
                    if len(cell_str) > 50:  # Long text that might contain Q&A
                        # Look for question patterns followed by answer patterns
                        lines = cell_str.split('\n')
                        for i in range(len(lines) - 1):
                            line1 = lines[i].strip()
                            line2 = lines[i + 1].strip()
                            
                            if (len(line1) > 10 and len(line2) > 20 and
                                ('?' in line1 or any(keyword in line1.lower() for keyword in ['what', 'how', 'when', 'where', 'why', 'which', 'who', 'do you', 'can you', 'would you', 'are you', 'is your', 'does your'])) and
                                not ('?' in line2 or any(keyword in line2.lower() for keyword in ['what', 'how', 'when', 'where', 'why', 'which', 'who', 'do you', 'can you', 'would you', 'are you', 'is your', 'does your']))):
                                
                                qa_pairs.append({
                                    'question': line1,
                                    'answer': line2,
                                    'sheet': sheet_name,
                                    'row': index + 1,
                                    'method': f'single_column_{col}'
                                })
            
            # Remove duplicates
            seen_questions = set()
            unique_qa_pairs = []
            for qa in qa_pairs:
                q_lower = qa['question'].lower().strip()
                if q_lower not in seen_questions and len(qa['question']) > 10 and len(qa['answer']) > 20:
                    seen_questions.add(q_lower)
                    unique_qa_pairs.append(qa)
            
            print(f"📊 Found {len(unique_qa_pairs)} Q&A pairs in sheet '{sheet_name}'")
            all_qa_pairs.extend(unique_qa_pairs)
        
        print(f"\n🎉 Total extracted Q&A pairs: {len(all_qa_pairs)}")
        
        # Display some examples
        print(f"\n📝 Sample Q&A pairs:")
        for i, qa in enumerate(all_qa_pairs[:5]):
            print(f"{i+1}. Q: {qa['question'][:80]}...")
            print(f"   A: {qa['answer'][:80]}...")
            print(f"   Method: {qa['method']}")
            print()
        
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
                "tags": ["mxnb", "excel", "qa-pairs", qa_pair['sheet'].lower().replace(' ', '-'), qa_pair['method']]
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
