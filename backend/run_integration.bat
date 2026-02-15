@echo off
echo ========================================
echo  RunAnywhere + HackHub Integration
echo ========================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker is not running!
    echo Please start Docker Desktop first.
    echo.
    echo Some features will be disabled without Docker:
    echo   - Code execution in sandboxes
    echo   - Repository testing
    echo   - README instruction validation
    echo.
    pause
)

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found!
    echo Please create it first: python -m venv venv
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import docker" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo.
echo Starting RunAnywhere Integration API on port 8001...
echo.
echo API Documentation: http://localhost:8001/docs
echo Health Check: http://localhost:8001/health
echo.
echo Press Ctrl+C to stop the server
echo.

python main_integration.py
