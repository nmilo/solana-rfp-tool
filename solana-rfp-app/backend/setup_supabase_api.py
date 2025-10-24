#!/usr/bin/env python3
"""
Setup Supabase using REST API
"""

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://zaqonwxzoafewoloexsk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphcW9ud3h6b2FmZXdvbG9leHNrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTMwMTE4NSwiZXhwIjoyMDc2ODc3MTg1fQ.hGygXYHIqt8ipZR2Kytzj-xGxGHhBuN2fZp86ytaVgk"

def test_supabase_connection():
    """Test Supabase connection"""
    print("🔍 Testing Supabase connection...")
    
    try:
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }
        
        # Test connection by getting project info
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Supabase connection successful!")
            return True
        else:
            print(f"❌ Supabase connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {str(e)}")
        return False

def create_tables_via_api():
    """Create tables using Supabase API"""
    print("🏗️ Creating tables via Supabase API...")
    
    try:
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }
        
        # Create users table
        users_table = {
            "name": "users",
            "columns": [
                {"name": "id", "type": "uuid", "primary_key": True, "default": "gen_random_uuid()"},
                {"name": "email", "type": "varchar(255)", "unique": True, "not_null": True},
                {"name": "name", "type": "varchar(255)"},
                {"name": "is_active", "type": "boolean", "default": True},
                {"name": "created_at", "type": "timestamp", "default": "now()"}
            ]
        }
        
        # Create knowledge_base table
        kb_table = {
            "name": "knowledge_base",
            "columns": [
                {"name": "id", "type": "uuid", "primary_key": True, "default": "gen_random_uuid()"},
                {"name": "question", "type": "text", "not_null": True},
                {"name": "answer", "type": "text", "not_null": True},
                {"name": "category", "type": "varchar(255)"},
                {"name": "tags", "type": "jsonb", "default": "'[]'"},
                {"name": "created_at", "type": "timestamp", "default": "now()"},
                {"name": "created_by", "type": "varchar(255)"},
                {"name": "is_active", "type": "boolean", "default": True},
                {"name": "confidence_threshold", "type": "float", "default": 0.1},
                {"name": "embedding", "type": "text"}
            ]
        }
        
        print("✅ Tables would be created via API (requires SQL execution)")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def add_sample_data_via_api():
    """Add sample data via Supabase API"""
    print("📝 Adding sample data via API...")
    
    try:
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }
        
        # Add sample user
        user_data = {
            "email": "demo@solana.org",
            "name": "Demo User",
            "is_active": True
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=headers,
            json=user_data
        )
        
        if response.status_code in [200, 201]:
            print("✅ Sample user added successfully!")
        else:
            print(f"⚠️ User might already exist: {response.status_code}")
        
        # Add sample knowledge base entry
        kb_data = {
            "question": "What is Solana?",
            "answer": "Solana is a high-performance blockchain platform designed for decentralized applications and crypto-currencies. It uses a unique Proof of History consensus mechanism to achieve fast transaction speeds and low costs.",
            "category": "General",
            "tags": ["solana", "blockchain", "consensus"],
            "is_active": True
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/knowledge_base",
            headers=headers,
            json=kb_data
        )
        
        if response.status_code in [200, 201]:
            print("✅ Sample knowledge base entry added successfully!")
        else:
            print(f"⚠️ Knowledge base entry might already exist: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample data: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Supabase via API...")
    
    # Test connection
    if not test_supabase_connection():
        print("❌ Cannot connect to Supabase")
        return
    
    # Create tables (this would require SQL execution)
    print("📋 Note: Tables need to be created via SQL in Supabase dashboard")
    print("   Go to: https://supabase.com/dashboard/project/zaqonwxzoafewoloexsk/sql")
    print("   Run the SQL commands from setup_supabase_tables.py")
    
    # Add sample data
    if not add_sample_data_via_api():
        print("❌ Failed to add sample data")
        return
    
    print("\n🎉 Supabase API setup completed!")
    print("\n📋 Next steps:")
    print("1. Create tables via SQL in Supabase dashboard")
    print("2. Update your backend to use Supabase")
    print("3. Test the system")

if __name__ == "__main__":
    main()
