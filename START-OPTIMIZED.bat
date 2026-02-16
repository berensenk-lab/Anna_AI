@echo off
REM ========================================
REM Anna AI Optimized Startup Script
REM ========================================
REM
REM Enhanced startup with GPU support, error recovery, and diagnostics
REM
REM ========================================

title Anna AI - Starting...
color 0A

@echo off
setlocal enabledelayedexpansion

REM ========================================
REM CONFIGURATION
REM ========================================

REM GPU Configuration for RTX 4060
set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1"
set "CUDNN_PATH=C:\Program Files\NVIDIA\CUDNN\v9.16\bin\13.0"
set "GPU_DEVICE=0"

REM Store original directory
set "ORIGINAL_DIR=%CD%"

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM ========================================
REM PRE-STARTUP CHECKS
REM ========================================

cd /d "%SCRIPT_DIR%"

echo.
echo ========================================
echo Anna AI Pre-Startup Checks
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo [ERROR] Virtual environment not found!
    echo.
    echo Create virtual environment with:
    echo   py -3.11 -m venv venv
    echo.
    echo Then install dependencies:
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if BASE directory exists
if not exist "BASE" (
    color 0C
    echo [ERROR] BASE directory not found!
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Check if GUI interface exists
if not exist "BASE\interface\gui_interface.py" (
    color 0C
    echo [ERROR] gui_interface.py not found!
    echo Expected: BASE\interface\gui_interface.py
    echo.
    pause
    exit /b 1
)

REM ========================================
REM GPU & CUDA SETUP
REM ========================================

echo [1/5] Configuring GPU acceleration...

REM Set CUDA paths for RTX 4060 with CUDA 13.1
if exist "%CUDA_PATH%" (
    set "PATH=%CUDA_PATH%\bin;!PATH!"
    color 0A
    echo [OK] CUDA 13.1 toolkit found
    color 0A
) else (
    color 0E
    echo [WARNING] CUDA toolkit not found at %CUDA_PATH%
    echo GPU acceleration may not work
    color 0A
)

REM Set CUDNN path
if exist "%CUDNN_PATH%" (
    set "PATH=%CUDNN_PATH%;!PATH!"
) else (
    color 0E
    echo [WARNING] CUDNN not found at %CUDNN_PATH%
    color 0A
)

REM Set GPU memory growth to prevent VRAM exhaustion
set "CUDA_VISIBLE_DEVICES=%GPU_DEVICE%"
set "TF_FORCE_GPU_ALLOW_GROWTH=true"
set "PYTORCH_ENABLE_MPS_FALLBACK=1"

echo [2/5] Activating virtual environment...

REM Activate virtual environment
call "venv\Scripts\activate.bat"

REM Verify activation
python -c "import sys; print('Python:', sys.executable)" >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

color 0A
echo [OK] Virtual environment active
color 0A

REM ========================================
REM ENVIRONMENT SETUP
REM ========================================

echo [3/5] Setting up environment...

REM Set Python environment variables
set "PYTHONIOENCODING=utf-8"
set "PYTHONUNBUFFERED=1"
set "PYTHONPATH=%CD%;!PYTHONPATH!"

REM Set memory optimization
set "OMP_NUM_THREADS=4"
set "MKL_NUM_THREADS=4"

echo [4/5] Verifying dependencies...

REM Verify core dependencies
python -c "import torch, discord, requests, pygame" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [WARNING] Some dependencies may be missing
    echo Run: pip install -r requirements.txt
    color 0A
) else (
    color 0A
    echo [OK] All core dependencies installed
    color 0A
)

REM Check GPU/CUDA availability
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')" >nul 2>&1

REM ========================================
REM OLLAMA CHECK
REM ========================================

echo [5/5] Checking Ollama API...

python -c "import requests; requests.get('http://localhost:11434/api/version', timeout=2)" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [WARNING] Ollama API not responding at http://localhost:11434
    echo.
    echo Make sure Ollama is running in another terminal:
    echo   ollama serve
    echo.
    echo Continuing anyway - check Ollama if startup fails
    color 0A
) else (
    color 0A
    echo [OK] Ollama API is responding
    color 0A
)

echo.
echo ========================================
echo Startup checks complete!
echo ========================================
echo.

REM ========================================
REM STARTUP
REM ========================================

echo Starting Anna AI GUI interface...
echo Current working directory: %CD%
echo.

REM Clear screen and show header
cls
color 0A
echo.
echo ========================================
echo              Anna AI Interface
echo ========================================
echo.

REM Start GUI with error handling
python -u "BASE\interface\gui_interface.py"

REM Check exit code
if errorlevel 1 (
    color 0C
    echo.
    echo ========================================
    echo GUI exited with error code: %errorlevel%
    echo ========================================
    echo.
    echo Troubleshooting steps:
    echo   1. Run system-check.bat to validate setup
    echo   2. Check Ollama is running: ollama serve
    echo   3. Review logs in BASE\logs\
    echo   4. See DEVELOPMENT.md for detailed troubleshooting
    echo.
    pause
) else (
    color 0A
    echo.
    echo ========================================
    echo Anna AI GUI closed normally
    echo ========================================
    echo.
)

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

REM Exit
exit /b 0
