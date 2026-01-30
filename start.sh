#!/bin/bash

echo "========================================"
echo "  Time Tracking App - Startup Script"
echo "========================================"
echo ""

# Parse theme argument (default: dark)
THEME="dark"
if [ "$1" = "light" ] || [ "$1" = "dark" ]; then
    THEME="$1"
fi

# Read ports from ports.conf
FRONTEND_PORT=5173
BACKEND_PORT=8000
if [ -f "ports.conf" ]; then
    FRONTEND_PORT=$(grep -oP 'FRONTEND_PORT=\K[0-9]+' ports.conf || echo "5173")
    BACKEND_PORT=$(grep -oP 'BACKEND_PORT=\K[0-9]+' ports.conf || echo "8000")
fi
export FRONTEND_PORT
export BACKEND_PORT

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker ps &> /dev/null; then
    echo "[ERROR] Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "[OK] Docker is running"
echo ""
echo "Starting Time Tracking App with $THEME theme..."
echo ""
echo "The app will be available at: http://localhost:$FRONTEND_PORT"
echo "Backend API expected at:    http://localhost:$BACKEND_PORT/api"
echo "Press Ctrl+C to stop the app"
echo ""

# Set theme environment variable for Docker
export VITE_THEME="$THEME"

# Build and start containers
docker-compose up --build -d

# Wait for containers to be ready
echo ""
echo "Waiting for app to start..."
sleep 5

# Open browser based on OS
echo "Opening browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:$FRONTEND_PORT
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:$FRONTEND_PORT 2>/dev/null || echo "Please open http://localhost:$FRONTEND_PORT in your browser"
else
    # Windows WSL
    cmd.exe /c start http://localhost:$FRONTEND_PORT 2>/dev/null || echo "Please open http://localhost:$FRONTEND_PORT in your browser"
fi

echo ""
echo "App is running! Press Ctrl+C to stop."
echo ""

# Keep script running
tail -f /dev/null
