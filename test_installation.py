#!/usr/bin/env python3
"""
Test script to verify OCR installation and functionality
"""

import sys
import subprocess
from pathlib import Path

def check_python_packages():
    """Check if required Python packages are installed."""
    required_packages = ['pytesseract', 'PIL', 'pdf2image']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_tesseract():
    """Check if Tesseract is installed and accessible."""
    try:
        import pytesseract
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract is installed (version: {version})")
        
        # Check available languages
        langs = pytesseract.get_languages()
        required_langs = {'eng', 'hin', 'mar', 'kan'}
        available_required = required_langs.intersection(set(langs))
        
        print(f"Available required languages: {', '.join(sorted(available_required))}")
        
        if len(available_required) < len(required_langs):
            missing_langs = required_langs - available_required
            print(f"⚠ Missing language packs: {', '.join(sorted(missing_langs))}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Tesseract error: {e}")
        return False

def check_poppler():
    """Check if Poppler is installed for PDF processing."""
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image can be imported")
        
        # Try to check if poppler utilities are available
        try:
            subprocess.run(['pdftoppm', '-h'], 
                         capture_output=True, check=True)
            print("✓ Poppler utilities are accessible")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ Poppler utilities not found in PATH")
            print("  PDF processing may not work properly")
            return False
            
    except ImportError as e:
        print(f"✗ pdf2image import error: {e}")
        return False

def test_sample_file():
    """Test with the sample file if it exists."""
    sample_file = Path("file samples/Maharastra.pdf")
    
    if sample_file.exists():
        print(f"\n📄 Found sample file: {sample_file}")
        print("You can test the OCR tool with:")
        print(f'python ocr_extractor.py --file "{sample_file}" --lang mar')
    else:
        print(f"\n⚠ Sample file not found: {sample_file}")

def main():
    """Run all checks."""
    print("Electricity Bill OCR - Installation Test")
    print("=" * 50)
    
    all_good = True
    
    print("\n1. Checking Python packages...")
    if not check_python_packages():
        all_good = False
        print("   Run: pip install -r requirements.txt")
    
    print("\n2. Checking Tesseract OCR...")
    if not check_tesseract():
        all_good = False
        print("   Install Tesseract and required language packs")
    
    print("\n3. Checking Poppler (PDF support)...")
    if not check_poppler():
        all_good = False
        print("   Install Poppler utilities for PDF support")
    
    test_sample_file()
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All checks passed! The OCR tool should work properly.")
    else:
        print("⚠ Some issues found. Please address them before using the tool.")
    
    print("\nFor installation help, see README.md")

if __name__ == "__main__":
    main()
