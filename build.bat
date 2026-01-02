@echo off
REM JobPacker Build Script for Windows
REM Creates a standalone .exe using PyInstaller
REM Requires Python 3.12

echo ========================================
echo  JobPacker - Build Script
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Check if venv exists, create if not
if not exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    echo Creating virtual environment with Python 3.12...
    py -3.12 -m venv "%SCRIPT_DIR%venv"
    if errorlevel 1 (
        echo Error: Failed to create virtual environment. Ensure Python 3.12 is installed.
        echo Install it from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo Installing pip...
    "%SCRIPT_DIR%venv\Scripts\python.exe" -m ensurepip --upgrade
)

echo Using virtual environment: %SCRIPT_DIR%venv
echo.

echo Installing dependencies...
"%SCRIPT_DIR%venv\Scripts\python.exe" -m pip install -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Installing PyInstaller...
"%SCRIPT_DIR%venv\Scripts\python.exe" -m pip install pyinstaller

echo.
echo Building executable...
echo (Including tls_client DLLs for job scraping)
"%SCRIPT_DIR%venv\Scripts\python.exe" -m PyInstaller --onefile --console --name "JobPacker" --additional-hooks-dir="%SCRIPT_DIR%" "%SCRIPT_DIR%jobpacker.py"

echo.
echo ========================================
if exist "%SCRIPT_DIR%dist\JobPacker.exe" (
    echo Build successful!
    echo Output: %SCRIPT_DIR%dist\JobPacker.exe
) else (
    echo Build may have failed. Check output above.
)
echo ========================================
echo.
pause
