#!/bin/bash

# Start backend in background
cd solana-rfp-app/backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend
cd ../frontend
npm run server

# Kill backend when frontend stops
kill $BACKEND_PID
