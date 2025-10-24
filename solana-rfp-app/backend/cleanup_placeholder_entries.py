#!/usr/bin/env python3
"""
Script to delete all placeholder entries from the knowledge base
"""
import requests
import json

def get_all_entries():
    """Get all entries from the knowledge base"""
    api_url = "https://solana-rfp-271974794838.herokuapp.com"
    auth_token = "mock-jwt-token-demo"
    
    try:
        response = requests.get(
            f"{api_url}/api/v1/knowledge/entries",
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get entries: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting entries: {str(e)}")
        return []

def delete_entry(entry_id: str):
    """Delete an entry from the knowledge base"""
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

def main():
    """Delete all placeholder entries"""
    print("🔍 Getting all entries from knowledge base...")
    entries = get_all_entries()
    
    if not entries:
        print("❌ No entries found")
        return
    
    print(f"📊 Found {len(entries)} total entries")
    
    # Identify placeholder entries
    placeholder_entries = []
    real_entries = []
    
    for entry in entries:
        answer = entry.get('answer', '')
        if "This question was extracted from the uploaded document:" in answer:
            placeholder_entries.append(entry)
        else:
            real_entries.append(entry)
    
    print(f"📊 Found {len(placeholder_entries)} placeholder entries to delete")
    print(f"📊 Found {len(real_entries)} real entries to keep")
    
    if not placeholder_entries:
        print("✅ No placeholder entries found to delete")
        return
    
    # Delete placeholder entries
    deleted_count = 0
    failed_count = 0
    
    for i, entry in enumerate(placeholder_entries):
        entry_id = entry.get('id', '')
        question = entry.get('question', '')[:50]
        
        print(f"🗑️  Deleting {i+1}/{len(placeholder_entries)}: {question}...")
        
        if delete_entry(entry_id):
            deleted_count += 1
            print(f"  ✅ Deleted")
        else:
            failed_count += 1
            print(f"  ❌ Failed")
    
    print(f"\n🎉 Cleanup Summary:")
    print(f"  ✅ Deleted: {deleted_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📊 Total placeholder entries: {len(placeholder_entries)}")
    print(f"  📊 Real entries kept: {len(real_entries)}")

if __name__ == "__main__":
    main()
