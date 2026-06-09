@echo off
echo ============================================
echo  PolicyBot - Windows Setup Script
echo ============================================

:: Step 1 - create venv
echo [1/4] Creating virtual environment...
py -3.11 -c "import sys" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
	py -3.11 -m venv venv
) else (
	echo Python 3.11 not found, using default python interpreter...
	python -m venv venv
)
call venv\Scripts\activate

:: Step 2 - upgrade pip
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip

:: Step 3 - install dependencies
echo [3/4] Installing dependencies...
pip install -r requirements.txt

:: Step 4 - run ingestion
echo [4/4] Building local index...
python rag\ingest.py

echo.
echo ============================================
echo  Setup complete! Now run:  python app.py
echo ============================================
pause
