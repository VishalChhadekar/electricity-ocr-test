#!/usr/bin/env python3
"""
Simple Accuracy Comparison Script
Compares ground truth vs extracted data with fuzzy date matching
"""

import json
import re
import subprocess
from datetime import datetime

def get_git_branch():
    """Get current git branch name"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"

def load_data():
    """Load ground truth and extracted data"""
    with open('final_expected_vs_extracted.json', 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
    
    with open('llm_extracted_data_20250712_224335.json', 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    return ground_truth, extracted_data['extracted_data']

def find_extracted_data(filename, extraction_data):
    """Find extracted data for a specific file"""
    for item in extraction_data:
        if filename in item['file_info']['file_name']:
            return item['invoice_data']['data']
    return None

def normalize_date_fuzzy(date_str):
    """Fuzzy date normalization - extract day, month, year regardless of format"""
    if not date_str:
        return None
    
    # Remove common separators and convert to string
    clean_date = str(date_str).upper().replace('-', '').replace('/', '').replace(' ', '').replace('.', '')
    
    # Month name mapping
    month_map = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
        'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }
    
    # Replace month names with numbers
    for month_name, month_num in month_map.items():
        clean_date = clean_date.replace(month_name, month_num)
    
    # Extract all digits
    digits = re.findall(r'\d+', clean_date)
    if not digits:
        return None
    
    # Join all digits
    all_digits = ''.join(digits)
    
    if len(all_digits) == 6:  # DDMMYY or MMDDYY
        day, month, year = all_digits[:2], all_digits[2:4], '20' + all_digits[4:6]
    elif len(all_digits) == 8:  # DDMMYYYY or YYYYMMDD
        if all_digits.startswith('20'):  # YYYYMMDD
            year, month, day = all_digits[:4], all_digits[4:6], all_digits[6:8]
        else:  # DDMMYYYY
            day, month, year = all_digits[:2], all_digits[2:4], all_digits[4:8]
    else:
        return None
    
    # Return normalized format: DDMMYYYY
    return f"{day.zfill(2)}{month.zfill(2)}{year}"

def fuzzy_match(expected, extracted):
    """Fuzzy matching for different field types"""
    if not expected and not extracted:
        return True
    if not expected or not extracted:
        return False
    
    expected_str = str(expected).strip()
    extracted_str = str(extracted).strip()
    
    # Exact match
    if expected_str == extracted_str:
        return True
    
    # Remove spaces and special characters for loose comparison
    expected_clean = re.sub(r'[^\w]', '', expected_str.upper())
    extracted_clean = re.sub(r'[^\w]', '', extracted_str.upper())
    
    return expected_clean == extracted_clean

def fuzzy_date_match(expected, extracted):
    """Fuzzy date matching"""
    norm_expected = normalize_date_fuzzy(expected)
    norm_extracted = normalize_date_fuzzy(extracted)
    
    if norm_expected is None and norm_extracted is None:
        return True
    if norm_expected is None or norm_extracted is None:
        return False
    
    return norm_expected == norm_extracted

def create_accuracy_report():
    """Create simple HTML accuracy report"""
    ground_truth, extraction_data = load_data()
    git_branch = get_git_branch()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Accuracy Report - {git_branch}</title>
<style>
body{{font:12px Arial;margin:15px;background:#f5f7fa}}
.container{{max-width:98%;margin:0 auto;background:white;border-radius:6px;padding:15px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
.header{{background:#2c3e50;color:white;padding:10px;text-align:center;border-radius:4px;margin-bottom:15px}}
.summary{{background:#ecf0f1;padding:10px;border-radius:4px;margin-bottom:15px}}
table{{width:100%;border-collapse:collapse;font-size:10px;table-layout:fixed}}
th{{background:#34495e;color:white;padding:8px;text-align:center;font-size:11px}}
td{{padding:6px;border:1px solid #ddd;text-align:center;vertical-align:top;word-wrap:break-word;overflow-wrap:break-word}}
.match{{background:#d4edda;color:#155724}}
.mismatch{{background:#f8d7da;color:#721c24}}
.missing{{background:#fff3cd;color:#856404}}
.file-name{{background:#e9ecef;font-weight:bold;text-align:left;width:12%;word-wrap:break-word}}
.accuracy-good{{color:#28a745;font-weight:bold}}
.accuracy-fair{{color:#ffc107;font-weight:bold}}
.accuracy-poor{{color:#dc3545;font-weight:bold}}
small{{font-size:9px;line-height:1.2;display:block;text-align:left;margin:2px 0}}
th:nth-child(1){{width:12%}}
th:nth-child(2){{width:8%}}
th:nth-child(3){{width:20%}}
th:nth-child(4){{width:20%}}
th:nth-child(5){{width:20%}}
th:nth-child(6){{width:10%}}
th:nth-child(7){{width:10%}}
</style></head>
<body>
<div class="container">
<div class="header"><h2>🎯 Accuracy Analysis Report</h2><p style="margin:5px 0;font-size:14px;opacity:0.9">Branch: {git_branch} | Generated: {timestamp}</p></div>
"""
    
    total_files = len(ground_truth)
    total_matches = 0
    total_fields = 0
    file_results = []
    
    # Field mappings
    field_mappings = [
        ('Invoice Number', 'expected_invoice_number', 'invoiceNumber'),
        ('Previous Date', 'expected_previous_reading_date', 'previousReadingDate'),
        ('Current Date', 'expected_current_reading_date', 'presentReadingDate'),
        ('Meter Number', 'meter_number', 'meter_number'),
        ('Consumption', 'unit_consumption', 'unit_consumption')
    ]
    
    for item in ground_truth:
        filename = item['file_name']
        extracted = find_extracted_data(filename, extraction_data)
        
        file_matches = 0
        file_total = 0
        results = {}
        
        # Check main fields
        for field_name, expected_key, extracted_key in field_mappings[:3]:  # First 3 are main fields
            expected_val = item.get(expected_key, '')
            
            if extracted_key == 'invoiceNumber':
                extracted_val = extracted.get('invoiceNumber', {}).get('parsed', '') if extracted else ''
            elif extracted_key == 'previousReadingDate':
                extracted_val = extracted.get('previousReadingDate', {}).get('parsed', '') if extracted else ''
            elif extracted_key == 'presentReadingDate':
                extracted_val = extracted.get('presentReadingDate', {}).get('parsed', '') if extracted else ''
            else:
                extracted_val = ''
            
            # Use fuzzy date matching for date fields
            if 'Date' in field_name:
                is_match = fuzzy_date_match(expected_val, extracted_val)
            else:
                is_match = fuzzy_match(expected_val, extracted_val)
            
            results[field_name] = {
                'expected': expected_val or '-',
                'extracted': extracted_val or '-',
                'match': is_match
            }
            
            if expected_val:  # Only count if we have expected data
                file_total += 1
                if is_match:
                    file_matches += 1
        
        # Check meter details
        meter_details = item.get('meter_details', [])
        if meter_details:
            meter = meter_details[0]
            expected_meter = meter.get('expected_meter_number', '')
            expected_consumption = meter.get('expected_unit_consumption', '')
            
            # Get extracted meter data
            extracted_meter = ''
            extracted_consumption = ''
            if extracted and 'meterReadings' in extracted and extracted['meterReadings']:
                meter_reading = extracted['meterReadings'][0]
                extracted_meter = meter_reading.get('meterNumber', '')
                extracted_consumption = str(meter_reading.get('unitsConsumed', ''))
            
            # Check meter number
            meter_match = fuzzy_match(expected_meter, extracted_meter)
            consumption_match = fuzzy_match(expected_consumption, extracted_consumption)
            
            results['Meter Number'] = {
                'expected': expected_meter or '-',
                'extracted': extracted_meter or '-',
                'match': meter_match
            }
            
            results['Consumption'] = {
                'expected': expected_consumption or '-',
                'extracted': extracted_consumption or '-',
                'match': consumption_match
            }
            
            if expected_meter:
                file_total += 1
                if meter_match:
                    file_matches += 1
            
            if expected_consumption:
                file_total += 1
                if consumption_match:
                    file_matches += 1
        
        # Calculate file accuracy
        file_accuracy = (file_matches / file_total * 100) if file_total > 0 else 0
        
        file_results.append({
            'filename': filename,
            'accuracy': file_accuracy,
            'matches': file_matches,
            'total': file_total,
            'results': results
        })
        
        total_matches += file_matches
        total_fields += file_total
    
    # Calculate overall accuracy
    overall_accuracy = (total_matches / total_fields * 100) if total_fields > 0 else 0
    
    # Add summary
    html += f"""
<div class="summary">
<h3>📊 Summary</h3>
<p><strong>Overall Accuracy:</strong> <span class="{'accuracy-good' if overall_accuracy >= 80 else 'accuracy-fair' if overall_accuracy >= 60 else 'accuracy-poor'}">{overall_accuracy:.1f}%</span></p>
<p><strong>Total Fields Matched:</strong> {total_matches}/{total_fields}</p>
<p><strong>Files Processed:</strong> {total_files}</p>
</div>
"""
    
    # Add detailed table
    html += """
<table>
<thead>
<tr>
<th>File Name</th>
<th>Accuracy</th>
<th>Invoice Number</th>
<th>Previous Date</th>
<th>Current Date</th>
<th>Meter Number</th>
<th>Consumption</th>
</tr>
</thead>
<tbody>
"""
    
    for result in file_results:
        accuracy_class = 'accuracy-good' if result['accuracy'] >= 80 else 'accuracy-fair' if result['accuracy'] >= 60 else 'accuracy-poor'
        
        html += f'<tr><td class="file-name">{result["filename"]}</td>'
        html += f'<td class="{accuracy_class}">{result["accuracy"]:.1f}%</td>'
        
        field_order = ['Invoice Number', 'Previous Date', 'Current Date', 'Meter Number', 'Consumption']
        for field in field_order:
            if field in result['results']:
                field_result = result['results'][field]
                status_class = 'match' if field_result['match'] else 'mismatch'
                status_icon = '✅' if field_result['match'] else '❌'
                
                # Show actual values (full length)
                html += f'<td class="{status_class}">{status_icon}<br/><small><b>Exp:</b> {field_result["expected"]}<br/><b>Got:</b> {field_result["extracted"]}</small></td>'
            else:
                html += '<td class="missing">-</td>'
        
        html += '</tr>'
    
    html += '</tbody></table></div></body></html>'
    
    # Save report with branch name
    report_filename = f'accuracy_report_{git_branch}.html'
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Accuracy report created: {report_filename}")
    print(f"🌿 Git branch: {git_branch}")
    print(f"📊 Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"🎯 Fields Matched: {total_matches}/{total_fields}")
    print(f"📁 Files Processed: {total_files}")

if __name__ == "__main__":
    create_accuracy_report()
