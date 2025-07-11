#!/usr/bin/env python3
"""
Batch OCR processor for multiple electricity bills
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List
import logging

try:
    from ocr_extractor import ElectricityBillOCR
except ImportError:
    print("Error: Could not import ocr_extractor. Make sure it's in the same directory.")
    sys.exit(1)


def find_files(directory: str, extensions: List[str]) -> List[Path]:
    """
    Find all files with specified extensions in a directory.
    
    Args:
        directory (str): Directory to search in
        extensions (List[str]): List of file extensions to look for
        
    Returns:
        List[Path]: List of found files
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    files = []
    for ext in extensions:
        pattern = f"**/*{ext}"
        files.extend(directory_path.glob(pattern))
    
    return sorted(files)


def process_batch(input_dir: str, output_dir: str, language: str, extensions: List[str]):
    """
    Process multiple files in batch.
    
    Args:
        input_dir (str): Input directory containing files
        output_dir (str): Output directory for text files
        language (str): Language code for OCR
        extensions (List[str]): File extensions to process
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all files
    files = find_files(input_dir, extensions)
    
    if not files:
        print(f"No files found with extensions {extensions} in {input_dir}")
        return
    
    print(f"Found {len(files)} files to process")
    
    # Initialize OCR tool
    ocr_tool = ElectricityBillOCR(language=language)
    
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing: {file_path.name}")
        
        try:
            # Extract text
            extracted_text = ocr_tool.process_file(str(file_path))
            
            if extracted_text:
                # Create output filename
                output_filename = file_path.stem + "_extracted.txt"
                output_file = output_path / output_filename
                
                # Save extracted text
                output_file.write_text(extracted_text, encoding='utf-8')
                print(f"✓ Saved to: {output_file}")
                successful += 1
            else:
                print("✗ No text extracted")
                failed += 1
                
        except Exception as e:
            print(f"✗ Error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Batch processing completed:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(files)}")
    print(f"  Output directory: {output_path.absolute()}")


def main():
    """Main function for batch processing."""
    parser = argparse.ArgumentParser(
        description="Batch OCR processor for electricity bills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_ocr.py --input "bills/" --output "extracted/" --lang mar
  python batch_ocr.py --input "samples/" --output "results/" --lang eng --ext .pdf .jpg
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input directory containing files to process'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for extracted text files'
    )
    
    parser.add_argument(
        '--lang', '-l',
        default='eng',
        choices=['eng', 'hin', 'mar', 'kan'],
        help='Language code for OCR (default: eng)'
    )
    
    parser.add_argument(
        '--ext', '--extensions',
        nargs='*',
        default=['.pdf', '.jpg', '.jpeg', '.png'],
        help='File extensions to process (default: .pdf .jpg .jpeg .png)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        process_batch(
            input_dir=args.input,
            output_dir=args.output,
            language=args.lang,
            extensions=args.ext
        )
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
