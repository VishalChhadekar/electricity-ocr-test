#!/usr/bin/env python3
"""
Batch OCR Processing Script
Processes all files in the file samples directory with automatic language detection
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import csv

# Add the current directory to Python path to import our OCR module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_extractor import OCRExtractor


def process_all_files():
    """Process all files in the file samples directory with automatic language detection."""
    
    # Define paths
    samples_dir = Path("file samples")
    output_dir = Path("ocr_output")
    output_dir.mkdir(exist_ok=True)
    
    # Results storage
    results = []
    
    print("Starting batch OCR processing with automatic language detection...")
    print("=" * 70)
    
    # Get all files in samples directory
    if not samples_dir.exists():
        print(f"Error: Directory '{samples_dir}' not found!")
        return
    
    files = [f for f in samples_dir.iterdir() if f.is_file()]
    
    if not files:
        print(f"No files found in '{samples_dir}' directory!")
        return
    
    # Initialize OCR with automatic language detection
    ocr_tool = OCRExtractor(language='auto', enable_auto_detection=True)
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        print(f"\nProcessing {i}/{len(files)}: {file_path.name}")
        print("-" * 50)
        
        try:
            # Process the file with automatic language detection
            result = ocr_tool.process_file(str(file_path))
            
            if result['status'] == 'success':
                raw_text = result['data']['rawText']
                text_length = len(raw_text)
                detected_lang = result['data']['detectedLanguage']
                lang_name = result['data']['detectedLanguageName']
                all_detected = result['data']['allDetectedLanguages']
                
                print(f"✅ Success: Extracted {text_length} characters")
                print(f"   Detected language: {detected_lang} ({lang_name})")
                if len(all_detected) > 1:
                    print(f"   All detected languages: {', '.join(all_detected)}")
                
                # Store result
                results.append({
                    'sr_no': i,
                    'file_name': file_path.name,
                    'detected_language': detected_lang,
                    'detected_language_name': lang_name,
                    'all_detected_languages': all_detected,
                    'raw_text': raw_text,
                    'text_length': text_length,
                    'status': 'success',
                    'extraction_id': result['data']['extractionId'],
                    'extracted_at': result['data']['extractedAt']
                })
                
                # Save individual JSON result
                individual_output = output_dir / f"{file_path.stem}_ocr_result.json"
                with open(individual_output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
            else:
                print(f"❌ Failed: {result['error']['errorDetail']}")
                results.append({
                    'sr_no': i,
                    'file_name': file_path.name,
                    'detected_language': 'unknown',
                    'detected_language_name': 'Unknown',
                    'all_detected_languages': [],
                    'raw_text': '',
                    'text_length': 0,
                    'status': 'failed',
                    'extraction_id': result['data']['extractionId'],
                    'extracted_at': result['data']['extractedAt'],
                    'error': result['error']['errorDetail']
                })
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
            results.append({
                'sr_no': i,
                'file_name': file_path.name,
                'detected_language': 'error',
                'detected_language_name': 'Error',
                'all_detected_languages': [],
                'raw_text': '',
                'text_length': 0,
                'status': 'error',
                'extraction_id': 'N/A',
                'extracted_at': datetime.now().isoformat(),
                'error': str(e)
            })
    
    # Create comprehensive output files
    create_output_files(results)
    
    print("\n" + "=" * 70)
    print("Batch processing completed!")
    print(f"Total files processed: {len(results)}")
    print(f"Successful extractions: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed extractions: {sum(1 for r in results if r['status'] != 'success')}")
    
    # Language detection summary
    successful_results = [r for r in results if r['status'] == 'success']
    if successful_results:
        print(f"\nLanguage Detection Summary:")
        lang_counts = {}
        for result in successful_results:
            lang = result['detected_language']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            lang_name = next((r['detected_language_name'] for r in successful_results if r['detected_language'] == lang), lang)
            print(f"  {lang} ({lang_name}): {count} files")


def create_output_files(results):
    """Create various output files with the results."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Create CSV summary report
    csv_file = f"ocr_batch_summary_{timestamp}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Sr_No', 'File_Name', 'Detected_Language', 'Detected_Language_Name', 'All_Detected_Languages', 'Text_Length', 'Status', 'Raw_Text_Preview']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            # Create a preview of raw text (first 100 characters)
            raw_text_preview = result['raw_text'][:100] + "..." if len(result['raw_text']) > 100 else result['raw_text']
            raw_text_preview = raw_text_preview.replace('\n', ' ').replace('\r', ' ')
            
            writer.writerow({
                'Sr_No': result['sr_no'],
                'File_Name': result['file_name'],
                'Detected_Language': result['detected_language'],
                'Detected_Language_Name': result['detected_language_name'],
                'All_Detected_Languages': ', '.join(result['all_detected_languages']),
                'Text_Length': result['text_length'],
                'Status': result['status'],
                'Raw_Text_Preview': raw_text_preview
            })
    
    # 2. Create detailed text report
    txt_file = f"ocr_batch_detailed_{timestamp}.txt"
    with open(txt_file, 'w', encoding='utf-8') as txtfile:
        txtfile.write("OCR BATCH PROCESSING DETAILED REPORT\n")
        txtfile.write("=" * 60 + "\n")
        txtfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        txtfile.write(f"Total files processed: {len(results)}\n")
        txtfile.write(f"Successful extractions: {sum(1 for r in results if r['status'] == 'success')}\n")
        txtfile.write(f"Failed extractions: {sum(1 for r in results if r['status'] != 'success')}\n\n")
        
        for result in results:
            txtfile.write(f"Sr. No: {result['sr_no']}\n")
            txtfile.write(f"File Name: {result['file_name']}\n")
            txtfile.write(f"Detected Language: {result['detected_language']} ({result['detected_language_name']})\n")
            if result['all_detected_languages']:
                txtfile.write(f"All Detected Languages: {', '.join(result['all_detected_languages'])}\n")
            txtfile.write(f"Status: {result['status']}\n")
            txtfile.write(f"Text Length: {result['text_length']} characters\n")
            
            if result['status'] == 'success':
                txtfile.write(f"Raw OCR Output:\n")
                txtfile.write("-" * 40 + "\n")
                txtfile.write(result['raw_text'])
                txtfile.write("\n" + "-" * 40 + "\n\n")
            else:
                txtfile.write(f"Error: {result.get('error', 'Unknown error')}\n\n")
            
            txtfile.write("=" * 60 + "\n\n")
    
    # 3. Create JSON summary
    json_file = f"ocr_batch_results_{timestamp}.json"
    summary_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_files": len(results),
            "successful_extractions": sum(1 for r in results if r['status'] == 'success'),
            "failed_extractions": sum(1 for r in results if r['status'] != 'success'),
            "total_characters_extracted": sum(r['text_length'] for r in results)
        },
        "results": results
    }
    
    with open(json_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(summary_data, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"\nOutput files created:")
    print(f"📄 CSV Summary: {csv_file}")
    print(f"📄 Detailed Report: {txt_file}")
    print(f"📄 JSON Results: {json_file}")
    print(f"📁 Individual results in: ocr_output/ directory")


if __name__ == "__main__":
    process_all_files()
