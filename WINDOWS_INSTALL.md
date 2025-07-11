# Windows Installation Guide

## Step 1: Install Python Dependencies ✅ (DONE)
```
pip install -r requirements.txt
```

## Step 2: Install Tesseract OCR

### Download and Install Tesseract
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
3. Run the installer and follow these steps:
   - **IMPORTANT**: During installation, make sure to select "Additional language data"
   - Check the boxes for:
     - English (eng) - should be selected by default
     - Hindi (hin)
     - Marathi (mar) 
     - Kannada (kan)
4. Install to the default location (usually `C:\Program Files\Tesseract-OCR`)
5. **Add to PATH**: During installation, check "Add to PATH" or add manually:
   - Add `C:\Program Files\Tesseract-OCR` to your system PATH environment variable

### Verify Tesseract Installation
Open a new command prompt and run:
```
tesseract --version
```

You should see version information. If you get an error, Tesseract is not in your PATH.

### Check Available Languages
```
tesseract --list-langs
```

You should see: eng, hin, mar, kan (among others)

## Step 3: Install Poppler (for PDF support)

### Download Poppler
1. Go to: https://github.com/oschwartz10612/poppler-windows/releases/
2. Download the latest release (e.g., `Release-24.08.0-0.zip`)
3. Extract the ZIP file to a folder like `C:\poppler`
4. Add `C:\poppler\Library\bin` to your system PATH environment variable

### Verify Poppler Installation
Open a new command prompt and run:
```
pdftoppm -h
```

You should see help text. If you get an error, Poppler is not in your PATH.

## How to Add to PATH (if needed)

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click "Environment Variables..."
3. Under "System Variables", find and select "Path", click "Edit..."
4. Click "New" and add the paths:
   - `C:\Program Files\Tesseract-OCR`
   - `C:\poppler\Library\bin`
5. Click "OK" on all dialogs
6. **Restart your command prompt/PowerShell**

## Step 4: Test the Installation

Run the test script:
```
python test_installation.py
```

If everything is installed correctly, you should see all green checkmarks ✓

## Step 5: Try the OCR Tool

Test with the sample file:
```
python ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar
```

## Troubleshooting

### "tesseract is not recognized"
- Make sure Tesseract is installed and added to PATH
- Restart your command prompt after adding to PATH
- Verify with: `tesseract --version`

### "pdftoppm is not recognized" 
- Make sure Poppler is installed and added to PATH
- Restart your command prompt after adding to PATH
- Verify with: `pdftoppm -h`

### Language not found errors
- Make sure you installed the language packs during Tesseract installation
- Check available languages: `tesseract --list-langs`
- If missing languages, reinstall Tesseract with language packs

### Permission errors
- Run command prompt as Administrator if needed
- Make sure the files are not in a restricted directory
