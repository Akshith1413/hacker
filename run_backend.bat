@echo off
echo ========================================================================
echo  HackHub Complete Platform v3.0
echo  ML + RunAnywhere + Enhanced Analysis
echo ========================================================================
echo.

cd backend

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo [1/4] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found!
    echo Please create it first: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo [2/4] Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing/updating dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM Check Docker status (optional)
echo [3/4] Checking Docker (optional for execution features)...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker is not running!
    echo   - RunAnywhere execution features will be disabled
    echo   - All other features will work normally
    echo.
    echo   To enable execution features:
    echo   1. Install Docker Desktop
    echo   2. Start Docker Desktop
    echo   3. Run: pip install docker
    echo.
) else (
    echo [OK] Docker is running - Full features available!
)

echo [4/4] Starting FastAPI server...
echo.
echo ========================================================================
echo  Server starting on http://0.0.0.0:8000
echo.
echo  Documentation: http://localhost:8000/docs
echo  Health Check:  http://localhost:8000/health
echo  Root Endpoint: http://localhost:8000/
echo.
echo  Features Available:
echo    - ML-powered repository search
echo    - Quality scoring (0-100)
echo    - Tech stack detection
echo    - Semantic search
echo    - Smart recommendations
echo    - README validation
echo    - Configuration analysis
echo    - Performance profiling
echo    - Comprehensive health scoring
echo    - Code execution (if Docker available)
echo    - Repository testing (if Docker available)
echo.
echo  Press Ctrl+C to stop the server
echo ========================================================================
echo.

python -m uvicorn main_v2:app --host 0.0.0.0 --port 8000 --reload

