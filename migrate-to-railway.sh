#!/bin/bash

echo "🚀 Migrating Solana RFP Tool to Railway..."
echo "=========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project
echo "🏗️  Creating Railway project..."
railway init

# Set environment variables
echo "⚙️  Setting environment variables..."
echo "Please enter your environment variables:"

read -p "OpenAI API Key: " OPENAI_API_KEY
read -p "Secret Key: " SECRET_KEY
read -p "Google Client ID: " GOOGLE_CLIENT_ID
read -p "Google Client Secret: " GOOGLE_CLIENT_SECRET

railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID"
railway variables set GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET"
railway variables set BACKEND_CORS_ORIGINS="https://solana-rfp-tool.vercel.app"

# Add PostgreSQL database
echo "🗄️  Adding PostgreSQL database..."
railway add postgresql

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Migration complete!"
echo "🌐 Your app will be available at: https://your-app-name.railway.app"
echo "📊 Database will be automatically configured"
echo "🔧 No timeout limits - large file uploads will work!"

