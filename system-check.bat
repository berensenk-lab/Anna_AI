@echo off
REM ========================================
REM Anna AI System Optimization & Diagnostics
REM ========================================
REM
REM This script checks, validates, and optimizes your Anna AI installation
REM
REM ========================================

title Anna AI System Checker
color 0B

echo.
echo ========================================
echo Anna AI System Diagnostics
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check Python
echo [1/10] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
    color 0A
    echo [OK] %PYTHON_VERSION%
    color 0B
) else (
    color 0C
    echo [ERROR] Python not found in PATH
    color 0B
    goto error
)

REM Check virtual environment
echo [2/10] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    color 0A
    echo [OK] Virtual environment exists
    color 0B
) else (
    color 0C
    echo [ERROR] Virtual environment not found at venv\Scripts\activate.bat
    echo Run: py -3.11 -m venv venv
    color 0B
    goto error
)

REM Check requirements
echo [3/10] Checking Python dependencies...
call "venv\Scripts\activate.bat" >nul 2>&1
python -c "import torch; import discord; import requests; import pygame" >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo [OK] Core dependencies installed
    color 0B
) else (
    color 0E
    echo [WARNING] Some dependencies missing
    echo Run: pip install -r requirements.txt
    color 0B
)

REM Check CUDA/GPU
echo [4/10] Checking GPU support...
python -c "import torch; print('CUDA Available: ' + str(torch.cuda.is_available())); print('GPU: ' + torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'Using CPU')" >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python -c "import torch; print('CUDA: ' + str(torch.cuda.is_available()))"') do set "CUDA_STATUS=%%i"
    if "!CUDA_STATUS!"=="CUDA: True" (
        color 0A
        echo [OK] CUDA enabled
        color 0B
    ) else (
        color 0E
        echo [WARNING] Using CPU-only PyTorch (GPU not available)
        color 0B
    )
) else (
    color 0C
    echo [ERROR] PyTorch check failed
    color 0B
)

REM Check Ollama
echo [5/10] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('ollama --version 2^>^&1') do set "OLLAMA_VERSION=%%i"
    color 0A
    echo [OK] %OLLAMA_VERSION%
    color 0B
) else (
    color 0C
    echo [ERROR] Ollama not found in PATH
    echo Download from: https://ollama.ai/
    color 0B
    goto error
)

REM Check Ollama connectivity
echo [6/10] Checking Ollama API connectivity...
python -c "import requests; requests.get('http://localhost:11434/api/version', timeout=2)" >nul 2>&1
if %errorlevel% equ 0 (
    color 0A
    echo [OK] Ollama API responding
    color 0B
) else (
    color 0E
    echo [WARNING] Ollama API not responding
    echo Start Ollama with: ollama serve
    color 0B
)

REM Check config files
echo [7/10] Checking configuration files...
if exist "personality\config.json" (
    color 0A
    echo [OK] config.json found
    color 0B
) else (
    color 0C
    echo [ERROR] personality\config.json not found
    color 0B
    goto error
)

if exist "personality\controls.py" (
    color 0A
    echo [OK] controls.py found
    color 0B
) else (
    color 0C
    echo [ERROR] personality\controls.py not found
    color 0B
    goto error
)

REM Check .env file
echo [8/10] Checking environment configuration...
if exist ".env" (
    color 0A
    echo [OK] .env file found
    color 0B
) else (
    color 0E
    echo [WARNING] .env file not found (using defaults)
    echo Create one by copying .env.template
    color 0B
)

REM Check memory directory
echo [9/10] Checking memory system...
if exist "personality\memory" (
    if exist "personality\base_memory" (
        color 0A
        echo [OK] Memory system ready
        color 0B
    ) else (
        color 0E
        echo [WARNING] Base memory not initialized (will create on first run)
        color 0B
    )
) else (
    color 0C
    echo [ERROR] Memory directory not found
    color 0B
)

REM Check GUI interface
echo [10/10] Checking GUI interface...
if exist "BASE\interface\gui_interface.py" (
    color 0A
    echo [OK] GUI interface found
    color 0B
) else (
    color 0C
    echo [ERROR] BASE\interface\gui_interface.py not found
    color 0B
    goto error
)

REM Success
echo.
echo ========================================
color 0A
echo All checks complete!
color 0B
echo ========================================
echo.
echo Next steps:
echo   1. Ensure Ollama is running: ollama serve
echo   2. Configure your Discord/Twitch/YouTube tokens in .env
echo   3. Start Anna AI: START.bat
echo.
echo For detailed setup, see:
echo   - SETUP.md (installation guide)
echo   - DEVELOPMENT.md (troubleshooting)
echo   - QUICK_START.md (getting started)
echo.
pause
exit /b 0

:error
echo.
color 0C
echo System check FAILED
color 0B
echo Please fix errors above and try again.
echo.
pause
exit /b 1
