@echo off
setlocal enabledelayedexpansion
title AI Resume Analyzer Launcher

echo =======================================================
echo    AI-Powered Resume & ATS Analyzer (Resume Intelligence)
echo =======================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    py --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is not installed or not added to your system PATH!
        echo Please download Python 3.10+ from https://www.python.org/downloads/
        echo Make sure to check the box: "Add python.exe to PATH" during installation.
        echo.
        pause
        exit /b 1
    ) else (
        set "PY_CMD=py"
    )
) else (
    set "PY_CMD=python"
)

echo [OK] Python detected:
!PY_CMD! --version
echo.

:: 2. Check and initialize .env file from .env.example if missing
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Creating .env file from .env.example...
        copy .env.example .env >nul
        echo [OK] Created .env file.
    )
)

:: 3. Check / create virtual environment (.venv)
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Setting up virtual environment in .venv...
    !PY_CMD! -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)

:: 4. Activate the virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: 5. Install or verify dependencies
echo [INFO] Checking and installing required dependencies...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Encountered an issue installing requirements silently. Retrying with full log...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies. Please check your internet connection.
        pause
        exit /b 1
    )
)
echo [OK] All dependencies are ready.
echo.

:: 6. Launch application
echo =======================================================
echo [STARTING] Launching AI Resume Analyzer...
echo Opening in your default web browser at http://localhost:7860
echo (Press Ctrl+C in this terminal window to stop the server)
echo =======================================================
echo.

:: Automatically open browser after 2 seconds in background
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:7860"

:: Start Gradio App
python app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Server stopped or exited with an error.
    pause
)
