@echo off
REM Create Desktop Shortcuts for Anna AI Optimization Tools
REM Run this script once to create convenient desktop shortcuts

setlocal enabledelayedexpansion

set "ANNA_PATH=C:\Users\beren\Anna_AI"
set "DESKTOP=%USERPROFILE%\Desktop"

echo Creating Anna AI optimization shortcuts on Desktop...
echo.

REM Create VBScript for creating shortcuts (Windows doesn't have native CLI shortcut creation)
set "VBS_FILE=%TEMP%\create_shortcuts.vbs"

(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo.
    echo ' System Check Shortcut
    echo Set oLink = oWS.CreateShortcut("%DESKTOP%\Anna AI - System Check.lnk"^)
    echo oLink.TargetPath = "%ANNA_PATH%\system-check.bat"
    echo oLink.WorkingDirectory = "%ANNA_PATH%"
    echo oLink.IconLocation = "%SystemRoot%\System32\cmd.exe,0"
    echo oLink.Description = "Run Anna AI system diagnostics"
    echo oLink.Save
    echo.
    echo ' Performance Monitor Shortcut
    echo Set oLink = oWS.CreateShortcut("%DESKTOP%\Anna AI - Performance Monitor.lnk"^)
    echo oLink.TargetPath = "%SystemRoot%\System32\cmd.exe"
    echo oLink.Arguments = "/k cd /d %ANNA_PATH% ^& venv\Scripts\python.exe monitor-performance.py --continuous"
    echo oLink.WorkingDirectory = "%ANNA_PATH%"
    echo oLink.IconLocation = "%SystemRoot%\System32\cmd.exe,0"
    echo oLink.Description = "Monitor Anna AI performance metrics"
    echo oLink.Save
    echo.
    echo ' Optimized Startup Shortcut
    echo Set oLink = oWS.CreateShortcut("%DESKTOP%\Anna AI - Start (Optimized).lnk"^)
    echo oLink.TargetPath = "%ANNA_PATH%\START-OPTIMIZED.bat"
    echo oLink.WorkingDirectory = "%ANNA_PATH%"
    echo oLink.IconLocation = "%SystemRoot%\System32\cmd.exe,0"
    echo oLink.Description = "Start Anna AI with GPU optimization"
    echo oLink.Save
) > "%VBS_FILE%"

REM Run the VBScript
cscript.exe "%VBS_FILE%"

REM Clean up
del "%VBS_FILE%"

echo.
echo ========================================
echo Shortcuts created successfully!
echo ========================================
echo.
echo Created shortcuts on Desktop:
echo   1. Anna AI - System Check
echo   2. Anna AI - Performance Monitor
echo   3. Anna AI - Start (Optimized^)
echo.
echo Next steps:
echo   1. Double-click "Anna AI - System Check" to verify installation
echo   2. Configure .env with your API tokens
echo   3. Start Anna AI with "Anna AI - Start (Optimized)"
echo.
pause
