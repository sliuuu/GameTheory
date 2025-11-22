#!/bin/bash

# Start script for Geopolitical Market Game Tracker

echo "🚀 Starting Geopolitical Market Game Tracker..."
echo ""

# Check if ports are already in use
if lsof -ti:8001 > /dev/null 2>&1; then
    echo "⚠️  Port 8001 is already in use. Backend may already be running."
else
    echo "📡 Starting backend API server on port 8001..."
    cd "$(dirname "$0")"
    python3 -m uvicorn api_backend:app --host 0.0.0.0 --port 8001 --reload &
    BACKEND_PID=$!
    echo "   Backend started with PID: $BACKEND_PID"
    sleep 2
fi

# Check if ports are already in use
if lsof -ti:5173 > /dev/null 2>&1; then
    echo "⚠️  Port 5173 is already in use. Frontend may already be running."
else
    echo "🎨 Starting frontend development server on port 5173..."
    cd "$(dirname "$0")/frontend"
    npm run dev &
    FRONTEND_PID=$!
    echo "   Frontend started with PID: $FRONTEND_PID"
    sleep 2
fi

echo ""
echo "✅ Servers should be running!"
echo ""
echo "📍 Backend API: http://localhost:8001"
echo "📍 Frontend:    http://localhost:5173"
echo "📍 API Docs:    http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
wait

