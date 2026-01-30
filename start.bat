@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Time Tracking App - Startup Script
echo ========================================
echo.

REM Parse theme argument (default: dark)
set THEME=dark
if "%1"=="light" set THEME=light
if "%1"=="dark" set THEME=dark

REM Read ports from ports.conf
set FRONTEND_PORT=5173
for /f "tokens=2 delims==" %%i in ('findstr "FRONTEND_PORT" ports.conf 2^>nul') do set FRONTEND_PORT=%%i

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker daemon is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.
echo Starting Time Tracking App with %THEME% theme...
echo.
echo The app will be available at: http://localhost:%FRONTEND_PORT%
echo Press Ctrl+C to stop the app
echo.

REM Set theme environment variable for Docker
set VITE_THEME=%THEME%

REM Build and start containers
docker-compose up --build -d

REM Wait for containers to be ready
echo.
echo Waiting for app to start...
timeout /t 5 /nobreak >nul

REM Open browser
echo Opening browser...
start http://localhost:%FRONTEND_PORT%

echo.
echo App is running! Close this window or press Ctrl+C to stop.
pause
