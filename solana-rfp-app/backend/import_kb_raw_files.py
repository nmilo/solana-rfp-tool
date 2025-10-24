#!/usr/bin/env python3
"""
Script to properly import RFP documents from KB raw directory with actual content extraction
"""
import os
import sys
import asyncio
import requests
from pathlib import Path

def get_kb_files_directory():
    """Get the KB raw directory path"""
    # Go up from backend to project root, then to KB raw
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent.parent
    kb_raw_dir = project_root / "Kb raw"
    return kb_raw_dir

async def upload_document_to_api(file_path: Path, api_url: str, auth_token: str):
    """Upload a document to the API for processing"""
    print(f"Uploading: {file_path.name}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            data = {
                'category': 'RFP Document',
                'tags': 'rfp,document,imported,' + file_path.stem.lower().replace(' ', '-')
            }
            headers = {'Authorization': f'Bearer {auth_token}'}
            
            response = requests.post(
                f"{api_url}/api/v1/knowledge/upload-document",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"  ✅ Successfully uploaded {file_path.name}")
                return True
            else:
                print(f"  ❌ Failed to upload {file_path.name}: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"  ❌ Error uploading {file_path.name}: {str(e)}")
        return False

async def import_kb_raw_files():
    """Import all files from KB raw directory to the API"""
    
    # Configuration
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    # Get KB raw directory
    kb_raw_dir = get_kb_files_directory()
    
    if not kb_raw_dir.exists():
        print(f"❌ KB raw directory not found: {kb_raw_dir}")
        return
    
    print(f"📁 Processing files from: {kb_raw_dir}")
    
    # Get all supported files
    supported_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls']
    files_to_process = []
    
    for file_path in kb_raw_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files_to_process.append(file_path)
    
    if not files_to_process:
        print("❌ No supported files found in KB raw directory")
        return
    
    print(f"📄 Found {len(files_to_process)} files to process:")
    for file_path in files_to_process:
        print(f"  - {file_path.name}")
    
    # Upload each file
    successful_uploads = 0
    failed_uploads = 0
    
    for file_path in files_to_process:
        success = await upload_document_to_api(file_path, api_url, auth_token)
        if success:
            successful_uploads += 1
        else:
            failed_uploads += 1
    
    print(f"\n🎉 Import complete!")
    print(f"📊 Successful uploads: {successful_uploads}")
    print(f"📊 Failed uploads: {failed_uploads}")
    print(f"📊 Total files: {len(files_to_process)}")
    
    if successful_uploads > 0:
        print(f"\n💡 The documents have been uploaded and will be processed by the AI to extract questions and answers.")
        print(f"💡 This may take a few minutes. You can check the knowledge base stats to see the new entries.")

if __name__ == "__main__":
    asyncio.run(import_kb_raw_files())
