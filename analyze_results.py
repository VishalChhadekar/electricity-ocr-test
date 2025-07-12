#!/usr/bin/env python3
"""
Result Analysis Tool for LLM Extraction Results
Compares extracted data with expected values and generates status report
"""

import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

def load_results():
    """Load the extraction results from JSON and CSV files."""
    
    # Find the latest result files
    json_files = list(Path('.').glob('llm_extracted_data_*.json'))
    csv_files = list(Path('.').glob('llm_extraction_summary_*.csv'))
    
    if not json_files or not csv_files:
        print("❌ No result files found!")
        return None, None
    
    # Get the latest files
    latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
    latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📊 Loading results from:")
    print(f"   JSON: {latest_json}")
    print(f"   CSV: {latest_csv}")
    
    # Load JSON data
    with open(latest_json, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Load CSV data
    csv_data = pd.read_csv(latest_csv)
    
    return json_data, csv_data

def define_expected_values():
    """Define expected values for each file based on manual verification."""
    
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
            "units_consumed": "486"  # Expected based on screenshot
        },
        "Multiple-Meters.pdf": {
            "invoice_number": "404022323107",
            "previous_reading_date": "10.05.2024",
            "present_reading_date": "01.09.2024",
            "meter_number": "TG000253,IT008695",  # Multiple meters
            "units_consumed": "22103,8914"  # Multiple meter readings
        }
    }
    
    return expected_data

def normalize_date(date_str):
    """Normalize date formats for comparison."""
    if not date_str or date_str == "null":
        return None
    
    # Remove extra text and normalize
    date_str = str(date_str).strip()
    
    # Handle different date formats
    date_formats = [
        "%Y-%m-%d", "%d-%m-%Y", "%d-%b-%y", "%d-%B-%Y",
        "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except:
            continue
    
    return date_str

def check_field_accuracy(expected, extracted, field_type="string"):
    """Check if extracted field matches expected value."""
    
    if not expected and not extracted:
        return "✅", "Both empty"
    
    if not expected:
        return "⚠️", "No expected value"
    
    if not extracted or extracted == "null" or extracted == "":
        return "❌", "Not extracted"
    
    # Normalize for comparison
    expected_norm = str(expected).strip().lower()
    extracted_norm = str(extracted).strip().lower()
    
    if field_type == "date":
        expected_norm = normalize_date(expected)
        extracted_norm = normalize_date(extracted)
        if expected_norm and extracted_norm:
            if expected_norm == extracted_norm:
                return "✅", "Exact match"
            else:
                return "❌", f"Date mismatch: {extracted_norm}"
    
    elif field_type == "number":
        # Remove non-numeric characters for comparison
        expected_clean = ''.join(filter(str.isdigit, expected_norm))
        extracted_clean = ''.join(filter(str.isdigit, extracted_norm))
        
        if expected_clean == extracted_clean:
            return "✅", "Exact match"
        else:
            return "❌", f"Number mismatch: {extracted}"
    
    else:  # String comparison
        if expected_norm == extracted_norm:
            return "✅", "Exact match"
        elif expected_norm in extracted_norm or extracted_norm in expected_norm:
            return "✅", "Partial match"
        else:
            return "❌", f"String mismatch: {extracted}"
    
    return "❌", "Unknown error"

def generate_comparison_table(json_data, csv_data):
    """Generate the comparison table as shown in the screenshot."""
    
    expected_data = define_expected_values()
    results = []
    
    print("\\n" + "="*120)
    print("📊 EXTRACTION RESULTS COMPARISON TABLE")
    print("="*120)
    
    # Header
    header = f"{'File Name':<20} {'Fields':<10} {'Invoice Number':<15} {'Previous Reading':<18} {'Present Reading':<17} {'Meter Number':<15} {'Unit':<10}"
    print(header)
    print("-"*120)
    
    # Process each file
    for idx, row in csv_data.iterrows():
        file_name = row['File_Name']
        
        # Get corresponding JSON data for detailed analysis
        json_file_data = None
        for item in json_data['extracted_data']:
            if item['file_info']['file_name'] == file_name:
                json_file_data = item['invoice_data']['data']
                break
        
        if file_name in expected_data:
            expected = expected_data[file_name]
            
            # Extract actual values from results
            extracted = {
                'invoice_number': row['Bill_Number_Parsed'] if pd.notna(row['Bill_Number_Parsed']) else None,
                'previous_reading_date': None,
                'present_reading_date': None,
                'meter_number': None,
                'units_consumed': row['Units_Consumed'] if pd.notna(row['Units_Consumed']) else None
            }
            
            # Get dates and meter info from JSON data if available
            if json_file_data:
                extracted['previous_reading_date'] = json_file_data.get('previousReadingDate', {}).get('parsed')
                extracted['present_reading_date'] = json_file_data.get('presentReadingDate', {}).get('parsed')
                
                # Get meter number from meter readings
                meter_readings = json_file_data.get('meterReadings', [])
                if meter_readings:
                    meter_numbers = [m.get('meterNumber', '') for m in meter_readings if m.get('meterNumber')]
                    extracted['meter_number'] = ','.join(meter_numbers) if meter_numbers else None
            
            # Check each field
            fields_status = []
            
            # Invoice Number
            inv_status, inv_note = check_field_accuracy(
                expected['invoice_number'], 
                extracted['invoice_number'], 
                "string"
            )
            
            # Previous Reading Date
            prev_date_status, prev_note = check_field_accuracy(
                expected['previous_reading_date'],
                extracted['previous_reading_date'],
                "date"
            )
            
            # Present Reading Date  
            pres_date_status, pres_note = check_field_accuracy(
                expected['present_reading_date'],
                extracted['present_reading_date'], 
                "date"
            )
            
            # Meter Number
            meter_status, meter_note = check_field_accuracy(
                expected['meter_number'],
                extracted['meter_number'],
                "string"
            )
            
            # Units Consumed
            units_status, units_note = check_field_accuracy(
                expected['units_consumed'],
                extracted['units_consumed'],
                "number"
            )
            
            # Print Expected row
            exp_row = f"{file_name:<20} {'Expected':<10} {expected['invoice_number']:<15} {expected['previous_reading_date']:<18} {expected['present_reading_date']:<17} {expected['meter_number']:<15} {expected['units_consumed']:<10}"
            print(exp_row)
            
            # Print Extracted row with status
            ext_inv = f"{inv_status}{extracted['invoice_number'] or 'null'}"
            ext_prev = f"{prev_date_status}{extracted['previous_reading_date'] or 'null'}"
            ext_pres = f"{pres_date_status}{extracted['present_reading_date'] or 'null'}"
            ext_meter = f"{meter_status}{extracted['meter_number'] or 'null'}"
            ext_units = f"{units_status}{extracted['units_consumed'] or 'null'}"
            
            ext_row = f"{'':<20} {'Extracted':<10} {ext_inv:<15} {ext_prev:<18} {ext_pres:<17} {ext_meter:<15} {ext_units:<10}"
            print(ext_row)
            print()
            
            # Store results for summary
            results.append({
                'file_name': file_name,
                'invoice_match': inv_status == "✅",
                'prev_date_match': prev_date_status == "✅", 
                'pres_date_match': pres_date_status == "✅",
                'meter_match': meter_status == "✅",
                'units_match': units_status == "✅",
                'overall_accuracy': row['Confidence_Score']
            })
    
    return results

def generate_summary_report(results):
    """Generate summary statistics."""
    
    print("\\n" + "="*80)
    print("📈 ACCURACY SUMMARY REPORT")
    print("="*80)
    
    total_files = len(results)
    
    # Field-wise accuracy
    invoice_correct = sum(1 for r in results if r['invoice_match'])
    prev_date_correct = sum(1 for r in results if r['prev_date_match'])
    pres_date_correct = sum(1 for r in results if r['pres_date_match'])
    meter_correct = sum(1 for r in results if r['meter_match'])
    units_correct = sum(1 for r in results if r['units_match'])
    
    print(f"📊 Field-wise Accuracy (out of {total_files} files):")
    print(f"   📄 Invoice Number:     {invoice_correct}/{total_files} ({invoice_correct/total_files*100:.1f}%)")
    print(f"   📅 Previous Date:      {prev_date_correct}/{total_files} ({prev_date_correct/total_files*100:.1f}%)")
    print(f"   📅 Present Date:       {pres_date_correct}/{total_files} ({pres_date_correct/total_files*100:.1f}%)")
    print(f"   🔢 Meter Number:       {meter_correct}/{total_files} ({meter_correct/total_files*100:.1f}%)")
    print(f"   ⚡ Units Consumed:     {units_correct}/{total_files} ({units_correct/total_files*100:.1f}%)")
    
    # Overall LLM confidence
    avg_confidence = sum(r['overall_accuracy'] for r in results) / total_files
    print(f"\\n🎯 Average LLM Confidence: {avg_confidence:.2f}")
    
    # Best and worst performing files
    best_file = max(results, key=lambda x: x['overall_accuracy'])
    worst_file = min(results, key=lambda x: x['overall_accuracy'])
    
    print(f"\\n🏆 Best Performance:  {best_file['file_name']} ({best_file['overall_accuracy']:.2f})")
    print(f"⚠️  Worst Performance: {worst_file['file_name']} ({worst_file['overall_accuracy']:.2f})")

def save_results_for_team_lead(results, csv_data):
    """Save formatted results for team lead presentation."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"team_lead_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("ELECTRICITY BILL OCR + LLM EXTRACTION RESULTS\\n")
        f.write("="*60 + "\\n\\n")
        
        f.write("📊 EXTRACTION PERFORMANCE SUMMARY\\n")
        f.write("-"*40 + "\\n")
        
        for idx, row in csv_data.iterrows():
            f.write(f"File: {row['File_Name']}\\n")
            f.write(f"  Status: {row['Status']}\\n")
            f.write(f"  Fields Extracted: {row['Fields_Extracted']}/46\\n")
            f.write(f"  Confidence: {row['Confidence_Score']}\\n")
            f.write(f"  Invoice: {row['Bill_Number_Parsed'] or 'Not extracted'}\\n")
            f.write(f"  Customer: {row['Customer_Name_Parsed'] or 'Not extracted'}\\n")
            f.write(f"  Amount: {row['Total_Amount_Parsed'] or 'Not extracted'}\\n")
            f.write("\\n")
        
        # Add technical details
        f.write("\\n🔧 TECHNICAL DETAILS\\n")
        f.write("-"*40 + "\\n")
        f.write("• OCR Engine: Tesseract with multi-language support\\n")
        f.write("• LLM Model: OpenAI GPT-4o-mini\\n")
        f.write("• Processing Method: OCR → LLM structured extraction\\n")
        f.write("• Output Format: Raw + Parsed values with confidence scoring\\n")
        
        avg_confidence = csv_data['Confidence_Score'].mean()
        total_fields = csv_data['Fields_Extracted'].sum()
        f.write(f"\\n📈 OVERALL METRICS\\n")
        f.write(f"• Average Confidence: {avg_confidence:.2f}\\n")
        f.write(f"• Total Fields Extracted: {total_fields}\\n")
        f.write(f"• Success Rate: {len(csv_data[csv_data['Status'] == 'success'])}/{len(csv_data)} files\\n")
    
    print(f"\\n💾 Team lead report saved: {filename}")

def main():
    """Main function to run the analysis."""
    
    print("🔍 EXTRACTION RESULTS ANALYZER")
    print("="*50)
    
    # Load results
    json_data, csv_data = load_results()
    if json_data is None:
        return
    
    # Generate comparison table
    results = generate_comparison_table(json_data, csv_data)
    
    # Generate summary
    generate_summary_report(results)
    
    # Save team lead report
    save_results_for_team_lead(results, csv_data)
    
    print("\\n✅ Analysis complete! Results ready for team lead presentation.")

if __name__ == "__main__":
    main()
