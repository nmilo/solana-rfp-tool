#!/bin/bash

# 🚀 Supabase Setup Script for Solana RFP Tool

echo "🚀 Setting up Supabase for your RFP tool..."

# Check if user is logged in
if ! command -v supabase &> /dev/null; then
    echo "📦 Installing Supabase CLI..."
    npm install -g supabase
fi

# Create new Supabase project
echo "🏗️ Creating new Supabase project..."
echo "Please go to https://supabase.com and:"
echo "1. Create a new project"
echo "2. Note down your project URL and API keys"
echo "3. Run the following commands:"

echo ""
echo "📋 Environment Variables to Set:"
echo "export SUPABASE_URL='https://your-project.supabase.co'"
echo "export SUPABASE_ANON_KEY='your-anon-key'"
echo "export SUPABASE_SERVICE_ROLE_KEY='your-service-role-key'"
echo ""

echo "🔧 Database Connection String:"
echo "export DATABASE_URL='postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres'"
echo ""

echo "📝 Next Steps:"
echo "1. Set the environment variables above"
echo "2. Run: python3 solana-rfp-app/backend/migrate_to_supabase.py"
echo "3. Update your Heroku config vars"
echo "4. Redeploy your backend"
echo ""

echo "✅ Setup instructions complete!"
echo "📖 See MIGRATE_TO_SUPABASE.md for detailed instructions"
