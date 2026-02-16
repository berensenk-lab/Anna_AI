@echo off
REM ========================================
REM Anna_AI Agent Startup Script
REM ========================================
REM
REM Starts the Anna_AI GUI interface with Python virtual environment
REM
REM Prerequisites:
REM   - Python 3.11.9 installed
REM   - Virtual environment created: py -3.11 -m venv venv
REM   - Dependencies installed: pip install -r requirements.txt
REM   - Ollama running: ollama serve (in separate terminal)
REM
REM Troubleshooting:
REM   - Run startup-check.bat first to validate setup
REM   - See QUICK_START.md for setup instructions
REM   - See DEVELOPMENT.md for troubleshooting
REM
REM ========================================

title Anna AI GUI - Starting...
color 0A

@echo off
REM Set CUDA paths (adjust if GPU drivers in different location)
set PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64;C:\Program Files\NVIDIA\CUDNN\v9.16\bin\13.0;%PATH%

REM Store original directory
set "ORIGINAL_DIR=%CD%"

REM Get the directory where this batch file is located (Anna_AI/)
set "SCRIPT_DIR=%~dp0"

REM Navigate to the Anna_AI directory (where this script is located)
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists in current directory
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo ERROR: Virtual environment not found at %CD%\venv\Scripts\activate.bat
    echo Current directory: %CD%
    echo.
    echo Please create virtual environment with:
    echo   py -3.11 -m venv venv
    echo.
    echo Then install dependencies:
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment from: %CD%\venv\
call "venv\Scripts\activate.bat"

REM Verify virtual environment is active
python -c "import sys; print('Python executable:', sys.executable)" 2>nul
if errorlevel 1 (
    color 0C
    echo ERROR: Failed to activate virtual environment or Python not found
    pause
    exit /b 1
)

REM Set environment variables for better Python compatibility
set "PYTHONIOENCODING=utf-8"
set "PYTHONUNBUFFERED=1"
set "PYTHONPATH=%CD%;%PYTHONPATH%"

REM Check if BASE directory exists
if not exist "BASE" (
    color 0C
    echo ERROR: BASE directory not found at %CD%\BASE
    echo Current directory: %CD%
    echo.
    echo Directory contents:
    dir /b
    pause
    exit /b 1
)

REM Check if interface directory exists, create if it doesn't
if not exist "BASE\interface" (
    echo Creating interface directory...
    mkdir "BASE\interface"
)

REM Check if GUI interface file exists
if not exist "BASE\interface\gui_interface.py" (
    color 0C
    echo ERROR: gui_interface.py not found at BASE\interface\gui_interface.py
    echo.
    echo Please ensure gui_interface.py is saved in the BASE\interface\ directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Show current working directory and Python info
echo.
echo Current working directory: %CD%
echo Python version:
python --version
echo Virtual environment: %VIRTUAL_ENV%
echo.

REM Check if Ollama is running
echo Checking Ollama connectivity...
python -c "import requests; requests.get('http://localhost:11434/api/version', timeout=2)" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo WARNING: Ollama API not responding at http://localhost:11434
    echo Make sure Ollama is running in another terminal:
    echo   ollama serve
    echo.
    echo Continuing anyway - agent may fail if Ollama doesn't start
    echo.
    timeout /t 3
) else (
    color 0A
    echo [OK] Ollama API is responding
    echo.
)

REM Run the GUI interface
echo Starting GUI interface...
echo If you encounter issues, check the output below:
echo ================================================
python -u "BASE\interface\gui_interface.py"

REM Check exit code
if errorlevel 1 (
    color 0C
    echo.
    echo ================================================
    echo GUI exited with error code: %errorlevel%
    echo.
    echo Troubleshooting steps:
    echo   1. Run: startup-check.bat
    echo   2. Check Ollama is running: ollama serve
    echo   3. Review logs in BASE\logs\
    echo   4. See DEVELOPMENT.md for detailed troubleshooting
) else (
    color 0A
    echo.
    echo ================================================
    echo GUI exited normally
)

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

echo.
echo Press any key to exit...
pause >nul
