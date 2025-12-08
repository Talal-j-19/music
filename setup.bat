@echo off
echo ========================================
echo AceStep Music Generator - Setup Script
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\" (
    echo Virtual environment already exists.
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

echo.
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

if errorlevel 1 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Get your API key from: https://fal.ai/dashboard/keys
echo 2. Set the FAL_KEY environment variable:
echo    set FAL_KEY=your_api_key_here
echo.
echo 3. Install FFmpeg (required for audio conversion):
echo    - Download from: https://ffmpeg.org/download.html
echo    - Or use Chocolatey: choco install ffmpeg
echo.
echo 4. Run the server:
echo    start.bat
echo.
echo    Or manually:
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
pause
