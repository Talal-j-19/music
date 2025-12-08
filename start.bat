@echo off
echo Starting AceStep Music Generator API...
echo.

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo.
    echo Please create a .env file with your FAL_KEY:
    echo 1. Copy .env.example to .env
    echo 2. Edit .env and add your API key from https://fal.ai/dashboard/keys
    echo.
    echo Example:
    echo   copy .env.example .env
    echo   notepad .env
    echo.
    pause
    exit /b 1
)

echo Configuration file found (.env)
echo Starting server on http://localhost:8000
echo.
echo API Documentation will be available at:
echo - Web Interface: http://localhost:8000
echo - Swagger UI: http://localhost:8000/docs
echo - ReDoc: http://localhost:8000/redoc
echo.

REM Activate virtual environment and run the server
call venv\Scripts\activate.bat
python main.py
