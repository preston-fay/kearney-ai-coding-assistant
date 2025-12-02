@echo off
echo.
echo ========================================
echo   KEARNEY AI CODING ASSISTANT
echo   Environment Setup for Windows
echo ========================================
echo.

:: 1. Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from Kearney Software Center.
    echo.
    pause
    exit /b 1
)
echo         Python found.

:: 2. Create virtual environment
echo [2/4] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo         Virtual environment already exists.
)

:: 3. Install dependencies
echo [3/4] Installing KDS tools...
call .venv\Scripts\pip install -q -r bootstrap\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 4. Verify installation
echo [4/4] Verifying installation...
.venv\Scripts\python -c "import pandas, matplotlib, pptx, yaml, PIL; print('All modules OK')"
if %errorlevel% neq 0 (
    echo [ERROR] Module verification failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS! Environment Ready.
echo ========================================
echo.
echo Next steps:
echo   1. Open Claude Desktop
echo   2. File ^> Open Folder ^> Select this directory
echo   3. Type: /project:help
echo.
pause
