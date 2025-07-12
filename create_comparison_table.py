#!/usr/bin/env python3
"""
Excel-style CSV Report Generator
Creates a CSV report matching the exact format from the screenshot
"""

import json
import pandas as pd
from datetime import datetime

def create_excel_style_report():
    """Create Excel-style CSV report matching the screenshot."""
    
    # Load the extraction results
    with open('llm_extracted_data_20250711_185526.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    csv_data = pd.read_csv('llm_extraction_summary_20250711_185526.csv')
    
    # Define expected values from screenshot
    expected_data = {
        "Bihar.pdf": {
            "invoice_number": "20240423720962126",
            "previous_reading_date": "15-MAR-24",
            "present_reading_date": "20-04-2024", 
            "meter_number": "U326173",
            "units_consumed": "536"
        },
        "Goregoan.pdf": {
            "invoice_number": "100580813638", 
            "previous_reading_date": "30-Mar-2024",
            "present_reading_date": "29-Apr-2024",
            "meter_number": "7763000",
            "units_consumed": "1090"
        },
        "Maharastra.pdf": {
            "invoice_number": "000002436874795",
            "previous_reading_date": "11-APR-24", 
            "present_reading_date": "11-MAY-24",
            "meter_number": "06507161895",
            "units_consumed": "486"
        },
        "Multiple-Meters.pdf": {
            "invoice_number": "404022323107",
            "previous_reading_date": "10.05.2024",
            "present_reading_date": "01.09.2024", 
            "meter_number": "M1: TG000253, M2: IT008695",
            "units_consumed": "M1: 22103, M2: 8914"
        }
    }
    
    # Create the comparison data
    report_data = []
    
    for idx, row in csv_data.iterrows():
        file_name = row['File_Name']
        
        if file_name in expected_data:
            expected = expected_data[file_name]
            
            # Get extracted data from JSON
            json_file_data = None
            for item in json_data['extracted_data']:
                if item['file_info']['file_name'] == file_name:
                    json_file_data = item['invoice_data']['data']
                    break
            
            # Extract values
            extracted = {
                'invoice_number': row['Bill_Number_Parsed'] if pd.notna(row['Bill_Number_Parsed']) else '',
                'units_consumed': str(row['Units_Consumed']) if pd.notna(row['Units_Consumed']) else ''
            }
            
            if json_file_data:
                extracted['previous_reading_date'] = json_file_data.get('previousReadingDate', {}).get('parsed', '')
                extracted['present_reading_date'] = json_file_data.get('presentReadingDate', {}).get('parsed', '')
                
                # Get meter number
                meter_readings = json_file_data.get('meterReadings', [])
                if meter_readings:
                    if len(meter_readings) > 1:
                        meter_nums = []
                        for i, m in enumerate(meter_readings, 1):
                            if m.get('meterNumber'):
                                meter_nums.append(f"M{i}: {m['meterNumber']}")
                        extracted['meter_number'] = ', '.join(meter_nums) if meter_nums else ''
                    else:
                        extracted['meter_number'] = meter_readings[0].get('meterNumber', '')
                else:
                    extracted['meter_number'] = ''
            else:
                extracted.update({
                    'previous_reading_date': '',
                    'present_reading_date': '',
                    'meter_number': ''
                })
            
            # Add expected row
            report_data.append({
                'File Name': file_name,
                'Fields': 'Expected',
                'Invoice Number': expected['invoice_number'],
                'Previous Reading Date': expected['previous_reading_date'],
                'Present Reading Date': expected['present_reading_date'],
                'Meter Number': expected['meter_number'],
                'Unit Consumed': expected['units_consumed']
            })
            
            # Add extracted row with status indicators
            def add_status(expected_val, extracted_val):
                if not extracted_val or extracted_val == 'null':
                    return f"❌ null"
                elif str(expected_val).lower().strip() == str(extracted_val).lower().strip():
                    return f"✅ {extracted_val}"
                elif any(char.isdigit() for char in str(expected_val)) and any(char.isdigit() for char in str(extracted_val)):
                    # For numbers, check if digits match
                    exp_digits = ''.join(filter(str.isdigit, str(expected_val)))
                    ext_digits = ''.join(filter(str.isdigit, str(extracted_val)))
                    if exp_digits == ext_digits:
                        return f"✅ {extracted_val}"
                    else:
                        return f"❌ {extracted_val}"
                else:
                    return f"❌ {extracted_val}"
            
            report_data.append({
                'File Name': '',
                'Fields': 'Extracted', 
                'Invoice Number': add_status(expected['invoice_number'], extracted['invoice_number']),
                'Previous Reading Date': add_status(expected['previous_reading_date'], extracted['previous_reading_date']),
                'Present Reading Date': add_status(expected['present_reading_date'], extracted['present_reading_date']),
                'Meter Number': add_status(expected['meter_number'], extracted['meter_number']),
                'Unit Consumed': add_status(expected['units_consumed'], extracted['units_consumed'])
            })
    
    # Create DataFrame and save
    df = pd.DataFrame(report_data)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extraction_comparison_report_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding='utf-8')
    
    print(f"✅ Excel-style report saved: {filename}")
    
    # Also display the table
    print("\\n📊 EXTRACTION COMPARISON TABLE")
    print("="*100)
    print(df.to_string(index=False))
    
    return filename

if __name__ == "__main__":
    create_excel_style_report()
