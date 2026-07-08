@echo off
set "SCRIPT=%~dp0dos.py"

where python >nul 2>&1
if %errorlevel% equ 0 (set "PY=python") else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (set "PY=py") else (
        echo [ERROR] Python not found
        pause
        exit /b 1
    )
)

"%PY%" -m pip show aiohttp >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing aiohttp...
    "%PY%" -m pip install aiohttp --quiet
)

"%PY%" "%SCRIPT%" %*
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Script exited with code %errorlevel%
    pause
)
