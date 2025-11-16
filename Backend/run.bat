@echo off
echo Starting Australian Super Source Contact Form API...
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure your settings.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Run the Flask app
echo Starting Flask server...
echo Server will be available at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
