#!/bin/bash

echo "🚀 Setting up Solana RFP Database..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Created .env file. Please edit it with your settings."
fi

# Import knowledge base if it exists
if [ -f "../../kb/rfp_kb.json" ]; then
    echo "📚 Importing existing knowledge base..."
    python import_kb.py ../../kb/rfp_kb.json
    echo "✅ Knowledge base imported successfully"
else
    echo "⚠️  Knowledge base file not found at ../../kb/rfp_kb.json"
fi

cd ..

# Setup Frontend
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies
npm install

cd ..

echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or use Docker: docker-compose up"
echo ""
echo "🌐 Frontend will be available at http://localhost:3000"
echo "🔧 Backend API will be available at http://localhost:8000"
echo "📖 API docs will be available at http://localhost:8000/docs"
