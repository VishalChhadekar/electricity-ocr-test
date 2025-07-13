#!/usr/bin/env python3
"""
Simple Visual Field Comparison
Just shows expected vs extracted fields - no matching logic
Usage: python visual_comparison.py <llm_extracted_data_file.json>
"""

import json
import sys
import os

def load_data(extraction_file):
    """Load ground truth and extraction results"""
    # Fixed ground truth file
    with open('final_expected_vs_extracted.json', 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
    
    # Dynamic extraction file
    if not os.path.exists(extraction_file):
        print(f"❌ Error: Extraction file '{extraction_file}' not found!")
        sys.exit(1)
        
    with open(extraction_file, 'r', encoding='utf-8') as f:
        extraction_data = json.load(f)
    
    return ground_truth, extraction_data['extracted_data']

def find_extraction_result(filename, extraction_data):
    """Find extraction result for a given filename"""
    for item in extraction_data:
        if filename in item['file_info']['file_name']:
            return item['invoice_data']['data']
    return None

def extract_field_value(data, field_path):
    """Extract field value from nested structure"""
    if not data:
        return ""
    
    field_data = data.get(field_path, {})
    if isinstance(field_data, dict) and 'parsed' in field_data:
        return field_data['parsed'] or ""
    return str(field_data) if field_data else ""

def create_simple_comparison(extraction_file):
    """Create simple HTML comparison - just show values"""
    ground_truth, extraction_data = load_data(extraction_file)
    
    # Extract filename for display
    extraction_filename = os.path.basename(extraction_file)
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Expected vs Extracted Fields</title>
<style>
body{{font:12px Arial;margin:15px;background:#f5f7fa}}
.container{{max-width:98%;margin:0 auto;background:white;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden}}
.header{{background:#2c3e50;color:white;padding:12px;text-align:center}}
.info{{background:#ecf0f1;padding:8px 15px;font-size:11px;border-bottom:1px solid #bdc3c7}}
.table-container{{overflow-x:auto}}
.comparison-table{{width:100%;border-collapse:collapse;font-size:11px}}
.comparison-table th{{background:#34495e;color:white;padding:8px 6px;text-align:center;font-weight:600;border-right:1px solid #2c3e50;position:sticky;top:0;z-index:10}}
.comparison-table td{{padding:6px;text-align:center;border-right:1px solid #ecf0f1;border-bottom:1px solid #ecf0f1;max-width:100px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.file-name{{background:#34495e;color:white;font-weight:600;position:sticky;left:0;z-index:5;min-width:120px;text-align:left;padding-left:8px}}
.expected{{background:#e8f5e8}}
.extracted{{background:#fff3e0}}
.empty{{color:#95a5a6;font-style:italic}}
.row-excellent{{background-color:#d5f4e6}}
.row-good{{background-color:#fef9e7}}
.row-poor{{background-color:#fadbd8}}
tr:hover td{{background-color:#f8f9fa !important}}
.last-col{{border-right:none}}
</style></head>
<body>
<div class="container">
<div class="header"><h3>📊 Expected vs Extracted Fields Comparison</h3></div>
<div class="info">📁 Extraction File: {extraction_filename} | 📋 Ground Truth: final_expected_vs_extracted.json</div>
<div class="table-container">
<table class="comparison-table">
<thead>
<tr>
<th class="file-name">File Name</th>
<th>Invoice Number<br><small>(Expected)</small></th>
<th>Invoice Number<br><small>(Extracted)</small></th>
<th>Previous Date<br><small>(Expected)</small></th>
<th>Previous Date<br><small>(Extracted)</small></th>
<th>Current Date<br><small>(Expected)</small></th>
<th>Current Date<br><small>(Extracted)</small></th>
<th>Meter Number<br><small>(Expected)</small></th>
<th>Meter Number<br><small>(Extracted)</small></th>
<th>Consumption<br><small>(Expected)</small></th>
<th class="last-col">Consumption<br><small>(Extracted)</small></th>
</tr>
</thead>
<tbody>
"""
    
    # Simple field mappings
    field_mappings = {
        'Invoice Number': ('expected_invoice_number', 'invoiceNumber'),
        'Previous Reading Date': ('expected_previous_reading_date', 'previousReadingDate'), 
        'Current Reading Date': ('expected_current_reading_date', 'presentReadingDate')
    }
    
    # Add data rows in spreadsheet style
    for item in ground_truth:
        filename = item['file_name']
        extracted = find_extraction_result(filename, extraction_data)
        
        # Clean filename for display
        display_name = filename.replace('.pdf', '').replace('.jpg', '').replace('.jpeg', '')
        
        # Determine row color based on some basic logic (you can customize this)
        row_class = "row-excellent"  # Default
        
        row = f'<tr class="{row_class}"><td class="file-name">{display_name}</td>'
        
        # Add all field pairs in order
        for field_display, (expected_key, extracted_key) in field_mappings.items():
            expected = item.get(expected_key, '') or '-'
            extracted_val = extract_field_value(extracted, extracted_key) or '-'
            
            # Truncate if too long
            if len(str(expected)) > 20:
                expected = str(expected)[:17] + '...'
            if len(str(extracted_val)) > 20:
                extracted_val = str(extracted_val)[:17] + '...'
            
            row += f'<td class="expected">{expected}</td><td class="extracted">{extracted_val}</td>'
        
        # Add meter details
        meter_details = item.get('meter_details', [])
        if meter_details:
            meter = meter_details[0]
            expected_meter = meter.get('expected_meter_number', '') or '-'
            expected_consumption = meter.get('expected_unit_consumption', '') or '-'
        else:
            expected_meter = '-'
            expected_consumption = '-'
        
        meter_extracted = "-"
        consumption_extracted = "-"
        if extracted and 'meterReadings' in extracted and extracted['meterReadings']:
            meter_reading = extracted['meterReadings'][0]
            meter_extracted = meter_reading.get('meterNumber', '') or '-'
            consumption_extracted = str(meter_reading.get('unitsConsumed', '')) or '-'
        
        # Truncate meter values if needed
        if len(str(expected_meter)) > 15:
            expected_meter = str(expected_meter)[:12] + '...'
        if len(str(meter_extracted)) > 15:
            meter_extracted = str(meter_extracted)[:12] + '...'
        
        row += f'<td class="expected">{expected_meter}</td><td class="extracted">{meter_extracted}</td>'
        row += f'<td class="expected">{expected_consumption}</td><td class="extracted last-col">{consumption_extracted}</td>'
        
        row += '</tr>'
        html += row
    
    html += '</tbody></table></div></div></body></html>'
    
    # Save report
    with open('simple_comparison.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Simple visual comparison created: simple_comparison.html")
    print(f"� Used extraction file: {extraction_filename}")
    print("�👀 Just shows expected vs extracted - you decide what matches!")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) != 2:
        print("❌ Usage: python visual_comparison.py <llm_extracted_data_file.json>")
        print("📝 Example: python visual_comparison.py llm_extracted_data_20250712_224335.json")
        sys.exit(1)
    
    extraction_file = sys.argv[1]
    create_simple_comparison(extraction_file)

if __name__ == "__main__":
    main()
