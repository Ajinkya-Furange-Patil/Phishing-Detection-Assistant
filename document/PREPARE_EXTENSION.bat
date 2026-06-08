@echo off
title PhishGuard Extension Preparer
echo ==========================================================
echo           PHISHGUARD - EXTENSION PREPARER
echo ==========================================================
echo.

set "SOURCE_DIR=%~dp0frontend"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "ONEDRIVE_DESKTOP=%USERPROFILE%\OneDrive\Desktop"

:: Check if OneDrive Desktop exists, otherwise use standard Desktop
if exist "%ONEDRIVE_DESKTOP%" (
    set "DEST_DIR=%ONEDRIVE_DESKTOP%\PhishGuard_Extension"
) else (
    set "DEST_DIR=%DESKTOP_DIR%\PhishGuard_Extension"
)

echo Source folder:      "%SOURCE_DIR%"
echo Destination folder: "%DEST_DIR%"
echo.

:: Create destination folder
if exist "%DEST_DIR%" (
    echo [INFO] Destination folder already exists. Cleaning it...
    rd /s /q "%DEST_DIR%"
)
mkdir "%DEST_DIR%"

:: Copy files
echo [INFO] Copying extension files to your Desktop...
xcopy /s /e /y "%SOURCE_DIR%\*" "%DEST_DIR%\" > nul

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==========================================================
    echo [SUCCESS] Extension folder prepared successfully!
    echo ==========================================================
    echo.
    echo Next Steps:
    echo   1. We are opening chrome://extensions/ in your browser...
    echo   2. Enable "Developer mode" in the top-right corner.
    echo   3. Click "Load unpacked" in the top-left corner.
    echo   4. Select the new folder on your Desktop:
    echo      "PhishGuard_Extension"
    echo.
    
    :: Open chrome extensions page
    start chrome chrome://extensions/
) else (
    echo.
    echo [ERROR] Failed to copy files. Please make sure the folder "%SOURCE_DIR%" exists.
)

echo.
pause
