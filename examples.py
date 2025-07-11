#!/usr/bin/env python3
"""
Example usage of the Electricity Bill OCR tool
"""

import os
import sys
from pathlib import Path

def run_ocr_example(file_path, language, description):
    """Run OCR on a file and display results."""
    print(f"\n{'='*60}")
    print(f"Example: {description}")
    print(f"File: {file_path}")
    print(f"Language: {language}")
    print('='*60)
    
    if Path(file_path).exists():
        # Import and run the OCR tool
        try:
            from ocr_extractor import ElectricityBillOCR
            
            ocr_tool = ElectricityBillOCR(language=language)
            extracted_text = ocr_tool.process_file(file_path)
            
            if extracted_text:
                print("\nExtracted Text:")
                print("-" * 40)
                # Show first 500 characters
                preview = extracted_text[:500]
                print(preview)
                if len(extracted_text) > 500:
                    print(f"\n... (showing first 500 of {len(extracted_text)} characters)")
            else:
                print("No text extracted.")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"File not found: {file_path}")
        print("This is just an example command. You would run:")
        print(f'python ocr_extractor.py --file "{file_path}" --lang {language}')

def main():
    """Run example demonstrations."""
    print("Electricity Bill OCR - Usage Examples")
    print("====================================")
    
    # Example 1: Marathi PDF (actual file)
    run_ocr_example(
        "file samples/Maharastra.pdf",
        "mar",
        "Extracting text from Marathi electricity bill (PDF)"
    )
    
    # Example 2: English image (hypothetical)
    run_ocr_example(
        "samples/english_bill.jpg", 
        "eng",
        "Extracting text from English electricity bill (Image)"
    )
    
    # Example 3: Hindi PDF (hypothetical)
    run_ocr_example(
        "samples/hindi_bill.pdf",
        "hin", 
        "Extracting text from Hindi electricity bill (PDF)"
    )
    
    # Example 4: Kannada image (hypothetical)
    run_ocr_example(
        "samples/kannada_bill.png",
        "kan",
        "Extracting text from Kannada electricity bill (PNG)"
    )
    
    print(f"\n{'='*60}")
    print("Command Line Usage Examples:")
    print('='*60)
    print("1. Process Marathi PDF:")
    print('   python ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar')
    print()
    print("2. Process English image:")
    print('   python ocr_extractor.py --file "bill.jpg" --lang eng')
    print()
    print("3. Process Hindi PDF with output file:")
    print('   python ocr_extractor.py --file "hindi_bill.pdf" --lang hin --output result.txt')
    print()
    print("4. Process with verbose logging:")
    print('   python ocr_extractor.py --file "bill.png" --lang kan --verbose')
    print()
    print("5. Get help:")
    print('   python ocr_extractor.py --help')

if __name__ == "__main__":
    main()
