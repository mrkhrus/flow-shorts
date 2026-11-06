@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   Google Flow Shorts Automation - 1-Click Setup
echo   Developed by Ali Noor
echo ========================================================
echo.

:: 1. Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed! Download it from: https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js is installed.

:: 2. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed! Download it from: https://python.org
    pause
    exit /b 1
)
echo [OK] Python is installed.

:: 3. Check FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] FFmpeg not found. Installing via winget...
    winget install Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    echo [NOTE] You may need to reopen terminal for FFmpeg to register in PATH.
) else (
    echo [OK] FFmpeg is installed.
)

:: 4. Check Google Chrome
if not exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    if not exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
        echo [INFO] Google Chrome not found. Installing via winget...
        winget install Google.Chrome -e --accept-source-agreements --accept-package-agreements
    )
)
echo [OK] Google Chrome is ready.

:: 5. Install Node dependencies & Build
echo.
echo [*] Installing Node packages...
call npm install

echo [*] Building TypeScript project...
call npm run build

:: 6. Install Python dependencies (edge-tts for Urdu voiceovers)
echo.
echo [*] Installing Python packages (edge-tts)...
pip install edge-tts

:: 7. Automatically configure Antigravity MCP config
echo.
echo [*] Configuring Antigravity MCP Server...
set "CONFIG_DIR=%USERPROFILE%\.gemini\config"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

set "CURR_DIR=%~dp0"
set "CURR_DIR=%CURR_DIR:~0,-1%"
set "ESC_PATH=%CURR_DIR:\=\\%\\dist\\index.js"

powershell -Command "$cfg = @{ mcpServers = @{ flow = @{ command = 'node'; args = @('%ESC_PATH%') } } }; $cfg | ConvertTo-Json -Depth 5 | Out-File -Encoding utf8 '%CONFIG_DIR%\mcp_config.json'"
echo [OK] Antigravity MCP configured at %CONFIG_DIR%\mcp_config.json

echo.
echo ========================================================
echo   Setup Complete! Opening Google Chrome for Sign-In...
echo ========================================================
echo.
echo 1. Sign in to your Google Account in the Chrome window.
echo 2. Click 'New Project' in Google Flow.
echo 3. Keep Chrome running in the background.
echo.
call npm run login
pause
