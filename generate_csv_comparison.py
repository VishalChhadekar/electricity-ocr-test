#!/usr/bin/env python3
"""
CSV Generator for Expected vs Extracted Comparison Table
Converts the HTML comparison table to CSV format
"""

import json
import csv
from datetime import datetime
import os

def load_extraction_results(json_file):
    """Load extraction results from JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_expected_values():
    """Define expected values for comparison (manual verification)"""
    return {
        "AJMER-RAJASTHAN.pdf": {
            "invoice_number": "12022203035729",
            "previous_reading_date": "30-03-2024",
            "present_reading_date": "30-04-2024",
            "meter_number": "943262",
            "units_consumed": "0"
        },
        "Bihar.pdf": {
            "invoice_number": "20240423720962126",
            "previous_reading_date": "15-MAR-24",
            "present_reading_date": "20-04-2024",
            "meter_number": "U326173",
            "units_consumed": "536"
        },
        "DAKSHIN-HARIYANA.pdf": {
            "invoice_number": "782622204383",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "8112.5"
        },
        "Goregoan.pdf": {
            "invoice_number": "100580813638",
            "previous_reading_date": "30-Mar-2024",
            "present_reading_date": "29-Apr-2024",
            "meter_number": "7763000",
            "units_consumed": "1090"
        },
        "Gulbarga-Karnataka .jpg": {
            "invoice_number": "0010710/26679",
            "previous_reading_date": "N/A",
            "present_reading_date": "17-05-2024",
            "meter_number": "N/A",
            "units_consumed": "330"
        },
        "Hubli-Karnataka English .jpg": {
            "invoice_number": "225802088708",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "N/A"
        },
        "Hubli-Karnataka.jpg": {
            "invoice_number": "038900230205202401",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "846"
        },
        "Karnataka-Bescom.pdf": {
            "invoice_number": "N/A (Poor Quality)",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "N/A"
        },
        "Maglore-Karnataka .jpg": {
            "invoice_number": "011110202406299071901",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "321"
        },
        "Maharastra.pdf": {
            "invoice_number": "000002436874795",
            "previous_reading_date": "11-APR-24",
            "present_reading_date": "11-MAY-24",
            "meter_number": "06507161895",
            "units_consumed": "486"
        },
        "North-Bihar.pdf": {
            "invoice_number": "10162166951",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "N/A"
        },
        "PASHIMANCHAL-UTTAR-HARIYANA.jpg": {
            "invoice_number": "N/A",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "N/A"
        },
        "pUNJAB.pdf": {
            "invoice_number": "3007647081",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "N/A"
        },
        "TPCODL-ORISSA.pdf": {
            "invoice_number": "2300935262",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "N/A"
        },
        "Uttar-Gujarat.pdf": {
            "invoice_number": "4-2024",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "105850"
        },
        "Uttar-Hariyana.pdf": {
            "invoice_number": "110142107",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "2133.69"
        },
        "Uttarakhand.pdf": {
            "invoice_number": "29486240",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "831"
        },
        "Uttarpradesh-Purvanchal.pdf": {
            "invoice_number": "019591568992",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "7"
        },
        "Uttarpradesh.jpeg": {
            "invoice_number": "136771036626",
            "previous_reading_date": "N/A",
            "present_reading_date": "N/A",
            "meter_number": "N/A",
            "units_consumed": "326"
        }
    }

def determine_match_status(expected, extracted):
    """Determine if values match"""
    if expected == "N/A" and (extracted == "N/A" or extracted is None or extracted == "null"):
        return "Match"
    elif str(expected).strip() == str(extracted).strip():
        return "Match"
    else:
        return "No Match"

def generate_csv_comparison_table(results, output_file):
    """Generate CSV comparison table"""
    
    expected_values = get_expected_values()
    
    # Open CSV file for writing
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'File Name', 'Field Type', 'Invoice Number', 'Previous Reading Date', 
            'Present Reading Date', 'Meter Number', 'Units Consumed',
            'Invoice Match', 'Prev Date Match', 'Curr Date Match', 'Meter Match', 'Units Match'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Process each file
        for file_data in results['extracted_data']:
            file_name = file_data['file_info']['file_name']
            invoice_data = file_data['invoice_data']['data']
            
            # Get expected values for this file
            expected = expected_values.get(file_name, {})
            
            # Extract actual values
            extracted_invoice = invoice_data.get('invoiceNumber', {}).get('parsed')
            extracted_prev_date = invoice_data.get('previousReadingDate', {}).get('parsed')
            extracted_curr_date = invoice_data.get('presentReadingDate', {}).get('parsed')
            
            # Get meter number (first meter if multiple)
            meter_readings = invoice_data.get('meterReadings', [])
            extracted_meter = meter_readings[0].get('meterNumber') if meter_readings else None
            
            # Get units consumed (first meter if multiple)
            extracted_units = meter_readings[0].get('unitsConsumed') if meter_readings else None
            
            # Clean extracted values and format as text to prevent scientific notation
            if extracted_invoice is None:
                extracted_invoice = "null"
            else:
                extracted_invoice = f"'{str(extracted_invoice)}"  # Add single quote to force text format
                
            if extracted_prev_date is None:
                extracted_prev_date = "null"
            if extracted_curr_date is None:
                extracted_curr_date = "null"
            if extracted_meter is None:
                extracted_meter = "null"
            else:
                extracted_meter = f"'{str(extracted_meter)}"  # Add single quote to force text format
                
            if extracted_units is None:
                extracted_units = "null"
            
            # Write expected row
            writer.writerow({
                'File Name': file_name,
                'Field Type': 'Expected',
                'Invoice Number': f"'{expected.get('invoice_number', 'N/A')}",  # Force text format
                'Previous Reading Date': expected.get('previous_reading_date', 'N/A'),
                'Present Reading Date': expected.get('present_reading_date', 'N/A'),
                'Meter Number': f"'{expected.get('meter_number', 'N/A')}",  # Force text format
                'Units Consumed': expected.get('units_consumed', 'N/A'),
                'Invoice Match': '',
                'Prev Date Match': '',
                'Curr Date Match': '',
                'Meter Match': '',
                'Units Match': ''
            })
            
            # Write extracted row with match status
            writer.writerow({
                'File Name': '',  # Empty for extracted row (merged cell effect)
                'Field Type': 'Extracted',
                'Invoice Number': extracted_invoice,
                'Previous Reading Date': extracted_prev_date,
                'Present Reading Date': extracted_curr_date,
                'Meter Number': extracted_meter,
                'Units Consumed': extracted_units,
                'Invoice Match': determine_match_status(expected.get('invoice_number', 'N/A'), extracted_invoice),
                'Prev Date Match': determine_match_status(expected.get('previous_reading_date', 'N/A'), extracted_prev_date),
                'Curr Date Match': determine_match_status(expected.get('present_reading_date', 'N/A'), extracted_curr_date),
                'Meter Match': determine_match_status(expected.get('meter_number', 'N/A'), extracted_meter),
                'Units Match': determine_match_status(expected.get('units_consumed', 'N/A'), extracted_units)
            })
    
    print(f"✓ CSV comparison table generated: {output_file}")

def main():
    """Main function to generate CSV comparison table"""
    
    # Load latest results
    json_file = "llm_extracted_data_20250711_225109.json"
    
    if not os.path.exists(json_file):
        print(f"❌ Error: Results file {json_file} not found!")
        return
    
    print("📊 Generating CSV Expected vs Extracted comparison table...")
    
    # Load results
    results = load_extraction_results(json_file)
    
    # Generate CSV file with new timestamp since original might be open
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f"expected_vs_extracted_table_{timestamp}.csv"
    generate_csv_comparison_table(results, csv_file)
    
    print(f"""
📋 CSV Comparison Table Generated!
================================================================================
File Generated: {csv_file}

Summary:
  📄 Total Files: {len(results['extracted_data'])}
  📈 Avg Confidence: {results['extraction_summary']['average_confidence']:.1%}
  📊 Total Fields: {results['extraction_summary']['total_fields_extracted']}
  ✅ Format: Expected vs Extracted rows with match status columns
================================================================================
    """)

if __name__ == "__main__":
    main()
