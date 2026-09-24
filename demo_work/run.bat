@echo off
echo ===================================================
echo     OnboardIQ — Enterprise React + Python Platform
echo ===================================================
echo.

echo [1/3] Running automated unit tests...
python -m pytest tests/ -v
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Tests failed.
    pause
    exit /b %ERRORLEVEL%
)
echo.

echo [2/3] Starting Python FastAPI Backend Server on port 8000...
start "OnboardIQ Backend API (Port 8000)" cmd /k "python server.py"

echo [3/3] Starting React 19 Frontend on port 5173...
cd frontend
start "OnboardIQ React Frontend (Port 5173)" cmd /k "npm run dev"
cd ..

echo.
echo ===================================================
echo  Services launched successfully!
echo  - React Frontend: http://localhost:5173
echo  - Python Backend: http://localhost:8000/docs
echo ===================================================
