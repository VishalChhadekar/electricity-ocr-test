#!/usr/bin/env python3
"""
Simple Accuracy Comparison Script
Compares ground truth vs LLM extraction results and generates CSV report
"""

import json
import csv
import sys
import os

def load_ground_truth():
    """Load ground truth data"""
    with open('ground_truth.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_llm_results(filename):
    """Load LLM extraction results"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('extracted_data', [])

def find_llm_result_by_filename(filename, llm_results):
    """Find LLM result for a specific filename"""
    for result in llm_results:
        llm_filename = result.get('file_info', {}).get('file_name', '')
        # Handle various filename matching scenarios
        if filename == llm_filename or filename in llm_filename or llm_filename in filename:
            return result.get('invoice_data', {}).get('data', {})
    return None

def safe_get_value(data, key, default='-'):
    """Safely get value from nested dictionary"""
    if not data:
        return default
    
    if isinstance(data, dict):
        value = data.get(key, {})
        if isinstance(value, dict):
            return value.get('parsed', default) or value.get('raw', default) or default
        return value or default
    return default

def compare_and_generate_csv(ground_truth_file, llm_results_file):
    """Main comparison function"""
    print(f"📊 Loading ground truth from: {ground_truth_file}")
    print(f"🤖 Loading LLM results from: {llm_results_file}")
    
    # Load data
    ground_truth = load_ground_truth()
    llm_results = load_llm_results(llm_results_file)
    
    # Prepare CSV data
    csv_data = []
    
    # Headers
    headers = [
        'File Name',
        'Invoice Number (Ground Truth)',
        'Invoice Number (LLM Result)',
        'Previous Reading Date (Ground Truth)',
        'Previous Reading Date (LLM Result)',
        'Present Reading Date (Ground Truth)',
        'Present Reading Date (LLM Result)',
        'Meter Number (Ground Truth)',
        'Meter Number (LLM Result)',
        'Units Consumed (Ground Truth)',
        'Units Consumed (LLM Result)',
        'Notes'
    ]
    
    csv_data.append(headers)
    
    # Process each file
    for item in ground_truth:
        filename = item.get('file_name', '')
        
        # Find corresponding LLM result
        llm_data = find_llm_result_by_filename(filename, llm_results)
        
        # Extract ground truth values
        gt_invoice = item.get('invoiceNumber', '-')
        gt_prev_date = item.get('previousReadingDate', '-')
        gt_present_date = item.get('presentReadingDate', '-')
        
        # Extract LLM values
        llm_invoice = safe_get_value(llm_data, 'invoiceNumber')
        llm_prev_date = safe_get_value(llm_data, 'previousReadingDate')
        llm_present_date = safe_get_value(llm_data, 'presentReadingDate')
        
        # Handle meter readings (get first meter reading)
        gt_meter_readings = item.get('meterReadings', [])
        gt_meter_number = '-'
        gt_units_consumed = '-'
        
        if gt_meter_readings:
            first_meter = gt_meter_readings[0]
            gt_meter_number = (first_meter.get('meterNumber') or 
                             first_meter.get('expected_meter_number', '-'))
            gt_units_consumed = (first_meter.get('unitsConsumed') or 
                               first_meter.get('expected_unit_consumption', '-'))
        
        # Extract LLM meter readings
        llm_meter_number = '-'
        llm_units_consumed = '-'
        
        if llm_data and 'meterReadings' in llm_data:
            llm_meter_readings = llm_data.get('meterReadings', [])
            if llm_meter_readings:
                first_llm_meter = llm_meter_readings[0]
                llm_meter_number = first_llm_meter.get('meterNumber', '-')
                llm_units_consumed = str(first_llm_meter.get('unitsConsumed', '-'))
        
        # Create notes
        notes = ''
        if not llm_data:
            notes = 'No LLM result found'
        elif not gt_meter_readings:
            notes = 'No ground truth meter data'
        
        # Create row with text prefix to prevent Excel formatting issues
        row = [
            filename,
            f"'{str(gt_invoice)}" if str(gt_invoice) != '-' else '-',  # Add quote prefix for Excel
            f"'{str(llm_invoice)}" if str(llm_invoice) != '-' else '-',
            str(gt_prev_date),
            str(llm_prev_date),
            str(gt_present_date),
            str(llm_present_date),
            f"'{str(gt_meter_number)}" if str(gt_meter_number) != '-' else '-',
            f"'{str(llm_meter_number)}" if str(llm_meter_number) != '-' else '-',
            str(gt_units_consumed),
            str(llm_units_consumed),
            notes
        ]
        
        csv_data.append(row)
    
    # Generate CSV filename with timestamp to avoid conflicts
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"accuracy_comparison_{timestamp}.csv"
    
    # Write CSV with proper encoding and formatting
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)  # Quote all fields to prevent issues
        for row in csv_data:
            writer.writerow(row)
    
    print(f"✅ CSV report generated: {csv_filename}")
    print(f"📈 Processed {len(ground_truth)} files")
    print(f"🔍 Found LLM results for {len([r for r in csv_data[1:] if r[-1] != 'No LLM result found'])} files")
    
    return csv_filename

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python accuracy_comparison.py <llm_extracted_data_file.json>")
        print("Example: python accuracy_comparison.py llm_extracted_data_20250713_134050_OCR_FineTune_0.1.json")
        sys.exit(1)
    
    llm_file = sys.argv[1]
    
    # Validate files exist
    if not os.path.exists('ground_truth.json'):
        print("❌ Error: ground_truth.json not found!")
        sys.exit(1)
    
    if not os.path.exists(llm_file):
        print(f"❌ Error: {llm_file} not found!")
        sys.exit(1)
    
    # Generate comparison
    try:
        csv_filename = compare_and_generate_csv('ground_truth.json', llm_file)
        print(f"\n🎯 Success! Open {csv_filename} in Excel or any spreadsheet application")
        print("📋 The CSV uses UTF-8-BOM encoding for proper Excel compatibility")
        
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
