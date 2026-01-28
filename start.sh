#!/bin/bash

echo "========================================"
echo "  Time Tracking App - Startup Script"
echo "========================================"
echo ""

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
echo "Starting Time Tracking App..."
echo ""
echo "The app will be available at: http://localhost:5173"
echo "Press Ctrl+C to stop the app"
echo ""

# Build and start containers
docker-compose up --build
