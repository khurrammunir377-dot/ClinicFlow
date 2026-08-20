@echo off
setlocal
cd /d "%~dp0"
title ClinicFlow Demo Setup

echo.
echo =============================================
echo        ClinicFlow Demo Setup and Start
echo =============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python launcher "py" was not found.
    echo Install Python 3.12 or newer and enable Add Python to PATH.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [1/5] Creating virtual environment...
    py -m venv venv
    if errorlevel 1 goto :failed
) else (
    echo [1/5] Virtual environment already exists.
)

echo [2/5] Installing requirements...
"venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

echo [3/5] Applying database migrations...
"venv\Scripts\python.exe" manage.py migrate
if errorlevel 1 goto :failed

echo [4/5] Creating safe synthetic demo data...
"venv\Scripts\python.exe" manage.py seed_demo
if errorlevel 1 goto :failed

echo [5/5] Running system checks...
"venv\Scripts\python.exe" manage.py check
if errorlevel 1 goto :failed

echo.
echo =============================================
echo ClinicFlow is ready.
echo Open: http://127.0.0.1:8000
echo Username: admin
echo Password: ClinicFlow2026!
echo Press Ctrl+C to stop the server.
echo =============================================
echo.
start "" http://127.0.0.1:8000
"venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
exit /b 0

:failed
echo.
echo SETUP FAILED. Review the error shown above.
echo See TESTING_INSTRUCTIONS.md for troubleshooting.
pause
exit /b 1
