@echo off
echo ========================================
echo AceStep Music Generator - .env Setup
echo ========================================
echo.

REM Check if .env already exists
if exist ".env" (
    echo .env file already exists!
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 (
        echo Setup cancelled.
        pause
        exit /b 0
    )
)

REM Copy .env.example to .env
echo Creating .env file from template...
copy .env.example .env >nul

if errorlevel 1 (
    echo Failed to create .env file!
    pause
    exit /b 1
)

echo .env file created successfully!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Get your API key from: https://fal.ai/dashboard/keys
echo.
echo 2. Open the .env file (opening in notepad now...)
echo.
echo 3. Replace 'your_fal_api_key_here' with your actual API key
echo.
echo 4. Save and close the file
echo.
echo 5. Run: start.bat
echo.

REM Open .env in notepad
notepad .env

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo After saving your API key in .env, run:
echo   start.bat
echo.
pause
