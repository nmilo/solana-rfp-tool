#!/bin/bash

# Initialize database with sample data
cd solana-rfp-app/backend
python init_sample_data.py

# Start backend in background
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend
cd ../frontend
npm run server

# Kill backend when frontend stops
kill $BACKEND_PID
