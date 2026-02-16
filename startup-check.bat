@echo off
REM ========================================
REM Anna_AI Startup Validation Script
REM ========================================
REM
REM This script validates that all dependencies and configurations
REM are in place before starting Anna_AI agent.
REM
REM Run before START.bat if you encounter issues
REM
REM Usage: startup-check.bat
REM
REM ========================================

setlocal enabledelayedexpansion

echo.
echo ======================================
echo Anna_AI Startup Validation
echo ======================================
echo.

REM Colors for output
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set NC=[0m

echo 1. Directory Structure Check
echo ---

if exist "venv\Scripts\activate.bat" (
    echo %GREEN%[OK]%NC% Virtual environment found at venv\
) else (
    echo %RED%[ERROR]%NC% Virtual environment not found at venv\
    echo Run: py -3.11 -m venv venv
    exit /b 1
)

if exist "BASE" (
    echo %GREEN%[OK]%NC% BASE directory found
) else (
    echo %RED%[ERROR]%NC% BASE directory not found
    exit /b 1
)

if exist "BASE\interface\gui_interface.py" (
    echo %GREEN%[OK]%NC% GUI interface found at BASE\interface\gui_interface.py
) else (
    echo %YELLOW%[WARN]%NC% GUI interface not found - may cause issues
)

if exist "personality\bot_info.py" (
    echo %GREEN%[OK]%NC% Bot personality config found
) else (
    echo %RED%[ERROR]%NC% personality\bot_info.py not found
    exit /b 1
)

if exist "config.json" (
    echo %GREEN%[OK]%NC% config.json found
) else (
    echo %YELLOW%[WARN]%NC% config.json not found - using defaults
)

if exist ".env" (
    echo %GREEN%[OK]%NC% .env file found
) else (
    echo %YELLOW%[INFO]%NC% .env file not found - will use .env.example if available
)

echo.
echo 2. Python & Virtual Environment Check
echo ---

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python not found in PATH
    echo Install Python 3.11.9 from: https://www.python.org/downloads/
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYVER=%%i
    echo %GREEN%[OK]%NC% Python installed: !PYVER!
)

REM Activate venv and check
call venv\Scripts\activate.bat >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to activate virtual environment
    exit /b 1
) else (
    echo %GREEN%[OK]%NC% Virtual environment activated
)

REM Check critical packages
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARN]%NC% PyTorch not installed
    echo Run: pip install -r requirements.txt
) else (
    for /f "tokens=*" %%i in ('python -c "import torch; print(torch.__version__)"') do set TORCHVER=%%i
    echo %GREEN%[OK]%NC% PyTorch: !TORCHVER!
)

python -c "import transformers" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARN]%NC% Transformers not installed
    echo Run: pip install -r requirements.txt
) else (
    for /f "tokens=*" %%i in ('python -c "import transformers; print(transformers.__version__)"') do set TFVER=%%i
    echo %GREEN%[OK]%NC% Transformers: !TFVER!
)

echo.
echo 3. Ollama Service Check
echo ---

REM Check if Ollama service is running
tasklist | findstr /i "ollama" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARN]%NC% Ollama process not running
    echo Start with: ollama serve
) else (
    echo %GREEN%[OK]%NC% Ollama process is running
)

REM Test Ollama API connectivity
for /f "tokens=*" %%i in ('powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/version' -TimeoutSec 2 -ErrorAction Stop; Write-Host 'OK' } catch { Write-Host 'FAIL' }" 2^>nul') do set OLLAMATEST=%%i

if "!OLLAMATEST!"=="OK" (
    echo %GREEN%[OK]%NC% Ollama API responding at http://localhost:11434
) else (
    echo %YELLOW%[WARN]%NC% Ollama API not responding
    echo Check: ollama serve is running
    echo Check: .env OLLAMA_HOST=0.0.0.0:11434
)

REM Check for required models
echo Checking for required models...
for /f "tokens=*" %%i in ('ollama list 2^>nul ^| findstr /i "gemma"') do (
    echo %GREEN%[OK]%NC% Gemma model found
    goto models_ok
)
echo %YELLOW%[WARN]%NC% Gemma model not found - download with: ollama pull gemma3:12b-it-q4_K_M

:models_ok

echo.
echo 4. GPU & CUDA Check
echo ---

REM Check GPU
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARN]%NC% nvidia-smi not found - GPU may not be available
) else (
    echo %GREEN%[OK]%NC% NVIDIA GPU detected
    python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}') if torch.cuda.is_available() else print('CUDA: Not available')" >nul 2>&1
)

echo.
echo 5. Audio Configuration Check
echo ---

REM Check for virtual audio cables
powershell -Command "Get-WmiObject Win32_SoundDevice | findstr /i 'cable'" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARN]%NC% Virtual audio cables not detected
    echo Install VB-Cable from: https://vb-audio.com/Cable/
) else (
    echo %GREEN%[OK]%NC% Virtual audio cable detected
)

echo.
echo 6. Configuration Files Check
echo ---

if exist "personality\bot_info.py" (
    echo %GREEN%[OK]%NC% personality\bot_info.py exists
    REM Check for key configuration
    findstr /i "agentname" "personality\bot_info.py" >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=* delims==" %%i in ('findstr "agentname" "personality\bot_info.py"') do (
            echo        %%i
        )
    )
) else (
    echo %RED%[ERROR]%NC% personality\bot_info.py not found
)

if exist ".env" (
    echo %GREEN%[OK]%NC% .env file configured
    findstr "OLLAMA_HOST" ".env" >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=*" %%i in ('findstr "OLLAMA_HOST" ".env"') do echo        %%i
    )
) else (
    echo %YELLOW%[INFO]%NC% .env file not found - using defaults
)

echo.
echo ======================================
echo Validation Complete!
echo ======================================
echo.

if exist "venv\Scripts\activate.bat" (
    if exist "personality\bot_info.py" (
        if exist "BASE\interface\gui_interface.py" (
            echo %GREEN%Ready to start Anna_AI%NC%
            echo.
            echo Next steps:
            echo 1. Ensure Ollama is running: ollama serve
            echo 2. Run: START.bat
            echo.
        )
    )
)

echo For detailed troubleshooting, see DEVELOPMENT.md
echo.
