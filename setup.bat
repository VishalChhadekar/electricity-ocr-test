@echo off
echo Installing Python dependencies for Electricity Bill OCR...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install Python packages
echo Installing Python packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Error: Failed to install Python packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ===================================================================
echo Python dependencies installed successfully!
echo.
echo IMPORTANT: You still need to install system dependencies:
echo.
echo 1. Tesseract OCR:
echo    - Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo    - Install and add to PATH
echo    - Make sure to install language packs for Indian languages
echo.
echo 2. Poppler (for PDF support):
echo    - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
echo    - Extract and add to PATH
echo.
echo After installing these, you can test the tool with:
echo python ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar
echo ===================================================================
echo.
pause
