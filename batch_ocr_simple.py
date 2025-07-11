#!/usr/bin/env python3
"""
Simple Batch OCR Processing Script
Processes all files in the file samples directory and generates summary files only
No individual file outputs - just CSV and JSON summary reports
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import csv

# Add the current directory to Python path to import our OCR module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_extractor_simple import OCRExtractor


def process_all_files():
    """Process all files in the file samples directory and generate summary reports only."""
    
    # Define paths
    samples_dir = Path("file samples")
    
    # Results storage
    results = []
    
    print("Starting simple batch OCR processing...")
    print("=" * 70)
    
    # Get all files in samples directory
    if not samples_dir.exists():
        print(f"Error: Directory '{samples_dir}' not found!")
        return
    
    files = [f for f in samples_dir.iterdir() if f.is_file()]
    
    if not files:
        print(f"No files found in '{samples_dir}' directory!")
        return
    
    # Initialize simple OCR tool
    ocr_tool = OCRExtractor()
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        print(f"\nProcessing {i}/{len(files)}: {file_path.name}")
        
        try:
            # Extract text from file
            extraction_result = ocr_tool.extract_text_from_file(str(file_path))
            
            raw_text = extraction_result['text']
            text_length = len(raw_text)
            
            # Create preview (first 100 characters)
            text_preview = raw_text.replace('\n', ' ').replace('\r', ' ')[:100] + "..." if len(raw_text) > 100 else raw_text
            
            # Store result
            result = {
                'sr_no': i,
                'file_name': file_path.name,
                'text_length': text_length,
                'status': 'success',
                'raw_text': raw_text,
                'raw_text_preview': text_preview,
                'processed_at': datetime.now().isoformat()
            }
            
            results.append(result)
            
            print(f"✓ Successfully extracted {text_length} characters")
            
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            
            # Store error result
            result = {
                'sr_no': i,
                'file_name': file_path.name,
                'text_length': 0,
                'status': 'failed',
                'raw_text': '',
                'raw_text_preview': f"Error: {str(e)}",
                'processed_at': datetime.now().isoformat()
            }
            
            results.append(result)
    
    # Generate summary files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate CSV summary
    csv_filename = f"ocr_batch_summary_{timestamp}.csv"
    generate_csv_summary(results, csv_filename)
    
    # Generate JSON summary
    json_filename = f"ocr_batch_summary_{timestamp}.json"
    generate_json_summary(results, json_filename)
    
    # Print final summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    
    print(f"Total files processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"\nSummary files generated:")
    print(f"  • CSV: {csv_filename}")
    print(f"  • JSON: {json_filename}")


def generate_csv_summary(results, filename):
    """Generate CSV summary file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Sr_No', 'File_Name', 'Text_Length', 'Status', 'Raw_Text_Preview']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'Sr_No': result['sr_no'],
                    'File_Name': result['file_name'],
                    'Text_Length': result['text_length'],
                    'Status': result['status'],
                    'Raw_Text_Preview': result['raw_text_preview']
                })
        
        print(f"✓ CSV summary saved: {filename}")
        
    except Exception as e:
        print(f"✗ Failed to generate CSV summary: {e}")


def generate_json_summary(results, filename):
    """Generate JSON summary file."""
    try:
        summary_data = {
            "batch_info": {
                "processed_at": datetime.now().isoformat(),
                "total_files": len(results),
                "successful_files": sum(1 for r in results if r['status'] == 'success'),
                "failed_files": sum(1 for r in results if r['status'] == 'failed'),
                "ocr_engine": "tesseract"
            },
            "results": []
        }
        
        for result in results:
            file_result = {
                "sr_no": result['sr_no'],
                "file_name": result['file_name'],
                "text_length": result['text_length'],
                "status": result['status'],
                "raw_text": result['raw_text'],
                "raw_text_preview": result['raw_text_preview'],
                "processed_at": result['processed_at']
            }
            summary_data["results"].append(file_result)
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(summary_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON summary saved: {filename}")
        
    except Exception as e:
        print(f"✗ Failed to generate JSON summary: {e}")


if __name__ == "__main__":
    process_all_files()
