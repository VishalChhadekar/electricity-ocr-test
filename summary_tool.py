#!/usr/bin/env python3
"""
Simple summary tool to show extracted fields from the structured OCR output
"""

import json
import sys
from pathlib import Path

def summarize_extraction(json_file_path):
    """Summarize the extracted fields from JSON output."""
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("🔍 OCR EXTRACTION SUMMARY")
        print("=" * 50)
        
        # Check if extraction was successful
        if data.get('error', {}).get('errorCode'):
            print(f"❌ Error: {data['error']['errorDetail']}")
            return
        
        extracted_data = data.get('data', {})
        
        if not extracted_data:
            print("⚠️  No data extracted")
            return
        
        print(f"📄 File: {data.get('meta', {}).get('fileName', 'Unknown')}")
        print(f"🌐 Language: {data.get('meta', {}).get('language', 'Unknown')}")
        print(f"📊 Pages: {len(data.get('meta', {}).get('pages', []))}")
        print()
        
        # Show extracted fields
        print("✅ EXTRACTED FIELDS:")
        print("-" * 30)
        
        field_mapping = {
            'customerNumber': '👤 Customer Number',
            'invoiceNumber': '🧾 Invoice Number', 
            'meterNumber': '⚡ Meter Number',
            'billDate': '📅 Bill Date',
            'dueDate': '⏰ Due Date',
            'presentReadingDate': '📊 Present Reading Date',
            'previousReadingDate': '📈 Previous Reading Date',
            'totalAmount': '💰 Total Amount',
            'unitsConsumed': '⚡ Units Consumed',
            'currentReading': '📊 Current Reading',
            'previousReading': '📈 Previous Reading'
        }
        
        for field_key, field_name in field_mapping.items():
            if field_key in extracted_data:
                field_data = extracted_data[field_key]
                raw_value = field_data.get('raw', 'N/A')
                parsed_value = field_data.get('parsed', 'N/A')
                confidence = field_data.get('confidence', 0.0)
                
                print(f"{field_name}: {parsed_value}")
                if raw_value != parsed_value:
                    print(f"   Raw: {raw_value}")
                print(f"   Confidence: {confidence:.2%}")
                print()
        
        # Show meter details if available
        if 'meterDetails' in extracted_data:
            print("⚡ METER DETAILS:")
            print("-" * 20)
            for i, meter in enumerate(extracted_data['meterDetails'], 1):
                print(f"Meter {i}:")
                print(f"  Number: {meter.get('meterNumber', 'N/A')}")
                print(f"  Units: {meter.get('unitsConsumed', 'N/A')}")
                print()
        
        # Show meter readings if available
        if 'meterReadings' in extracted_data:
            print("📊 DETAILED METER READINGS:")
            print("-" * 30)
            for i, reading in enumerate(extracted_data['meterReadings'], 1):
                parsed = reading.get('parsed', {})
                print(f"Reading {i}:")
                if 'meterNumber' in parsed:
                    print(f"  Meter: {parsed['meterNumber'].get('parsed', 'N/A')}")
                if 'unitsConsumed' in parsed:
                    print(f"  Units: {parsed['unitsConsumed'].get('parsed', 'N/A')}")
                if 'currentReading' in parsed:
                    print(f"  Current: {parsed['currentReading'].get('parsed', 'N/A')}")
                if 'previousReading' in parsed:
                    print(f"  Previous: {parsed['previousReading'].get('parsed', 'N/A')}")
                print()
        
        # Show success summary
        extracted_count = len([k for k in field_mapping.keys() if k in extracted_data])
        total_fields = len(field_mapping)
        
        print("📈 EXTRACTION STATISTICS:")
        print("-" * 25)
        print(f"Fields extracted: {extracted_count}/{total_fields}")
        print(f"Success rate: {extracted_count/total_fields:.1%}")
        
        if 'rawText' in extracted_data:
            text_length = len(extracted_data['rawText'])
            print(f"Total text extracted: {text_length:,} characters")
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON file: {json_file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python summary_tool.py <json_file>")
        print("Example: python summary_tool.py enhanced_output.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    summarize_extraction(json_file)

if __name__ == "__main__":
    main()
