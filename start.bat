@echo off
setlocal
cd /d "%~dp0"
title TRACER // Operations Command Center
color 0B

echo ======================================================================
echo   TRACER // AI TRAFFIC & CROWD MANAGEMENT OPERATIONS SYSTEM
echo ======================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Starting operations server and launching Command Center...
    echo.
    python main.py
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo Starting operations server using py launcher...
        echo.
        py main.py
    ) else (
        echo [ERROR] Python was not found in your system PATH.
        echo Please ensure Python 3.10+ is installed and added to PATH.
        pause
    )
)

echo.
pause
