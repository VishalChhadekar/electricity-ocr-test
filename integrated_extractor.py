#!/usr/bin/env python3
"""
Integrated OCR + LLM Invoice Data Extractor
Combines fast OCR text extraction with OpenAI intelligent data extraction
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import csv
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_extractor import OCRExtractor
from llm_extractor import LLMInvoiceExtractor


class IntegratedInvoiceExtractor:
    """Combines OCR and LLM for complete invoice data extraction."""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        """Initialize the integrated extractor."""
        self.ocr_extractor = OCRExtractor()
        self.llm_extractor = LLMInvoiceExtractor(openai_api_key, model)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_invoice_data(self, file_path: str) -> Dict[str, Any]:
        """Complete invoice data extraction pipeline: OCR -> LLM."""
        
        file_name = Path(file_path).name
        self.logger.info(f"Starting integrated extraction for: {file_name}")
        
        try:
            # Step 1: OCR Text Extraction
            self.logger.info("Step 1: Extracting raw text using OCR...")
            ocr_result = self.ocr_extractor.extract_text_from_file(file_path)
            raw_text = ocr_result['text']
            
            if not raw_text or len(raw_text.strip()) < 50:
                raise ValueError("OCR extracted insufficient text content")
            
            self.logger.info(f"OCR extracted {len(raw_text)} characters")
            
            # Step 2: LLM Data Extraction
            self.logger.info("Step 2: Extracting structured data using LLM...")
            structured_data = self.llm_extractor.extract_invoice_data(raw_text, file_name)
            
            # Add OCR metadata
            structured_data["ocr_metadata"] = {
                "raw_text": raw_text,
                "text_length": len(raw_text),
                "ocr_engine": "tesseract"
            }
            
            # Add processing status
            structured_data["processing_status"] = {
                "status": "success",
                "pipeline_steps": ["ocr_extraction", "llm_extraction"],
                "processed_at": datetime.now().isoformat()
            }
            
            # Get fields count from extraction metadata
            fields_count = structured_data.get("extractionMetadata", {}).get("extracted_fields_count", 0)
            self.logger.info(f"Successfully extracted {fields_count} fields")
            return structured_data
            
        except Exception as e:
            self.logger.error(f"Extraction failed for {file_name}: {str(e)}")
            return self._create_error_response(str(e), file_name)
    
    def _create_error_response(self, error_message: str, file_name: str) -> Dict[str, Any]:
        """Create an error response with the expected schema."""
        return {
            "data": {
                "invoiceNumber": {"raw": None, "parsed": None},
                "previousReadingDate": {"raw": None, "parsed": None},
                "presentReadingDate": {"raw": None, "parsed": None},
                "billingDate": {"raw": None, "parsed": None},
                "nextReadingDate": {"raw": None, "parsed": None},
                "customerInfo": {
                    "name": {"raw": None, "parsed": None},
                    "customerId": {"raw": None, "parsed": None},
                    "address": {"raw": None, "parsed": None},
                    "mobile": {"raw": None, "parsed": None}
                },
                "billingDetails": {
                    "totalAmount": {"raw": None, "parsed": None},
                    "dueDate": {"raw": None, "parsed": None},
                    "billingPeriod": {"raw": None, "parsed": None}
                },
                "utilityInfo": {
                    "companyName": {"raw": None, "parsed": None},
                    "state": {"raw": None, "parsed": None}
                },
                "meterReadings": []
            },
            "extractionMetadata": {
                "confidence_score": 0.0,
                "extracted_fields_count": 0,
                "total_possible_fields": 46,
                "completion_rate": 0.0,
                "quality_score": 0.0,
                "overall_confidence": 0.0,
                "meter_readings_count": 0,
                "has_critical_fields": False,
                "extracted_at": datetime.now().isoformat(),
                "model_used": "gpt-4o-mini",
                "file_name": file_name,
                "raw_text_length": 0,
                "extraction_method": "integrated_ocr_llm",
                "error": error_message
            },
            "ocr_metadata": {
                "raw_text": "",
                "text_length": 0,
                "ocr_engine": "tesseract"
            },
            "processing_status": {
                "status": "failed",
                "pipeline_steps": ["ocr_extraction", "llm_extraction"],
                "processed_at": datetime.now().isoformat(),
                "error": error_message
            }
        }


def batch_extract_with_llm(samples_dir: str = None, openai_api_key: str = None, model: str = None):
    """Batch process all files with integrated OCR + LLM extraction."""
    
    # Load configuration from .env file if not provided
    if not openai_api_key:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("Error: OpenAI API key not found!")
            print("Please set OPENAI_API_KEY in your .env file")
            return
    
    if not model:
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    if not samples_dir:
        samples_dir = os.getenv('SAMPLES_DIR', 'samples')
    
    # Initialize integrated extractor
    extractor = IntegratedInvoiceExtractor(openai_api_key, model)
    
    # Define paths
    samples_path = Path(samples_dir)
    
    # Results storage
    results = []
    
    print("Starting Integrated OCR + LLM Invoice Data Extraction...")
    print("=" * 80)
    
    # Get all files in samples directory
    if not samples_path.exists():
        print(f"Error: Directory '{samples_path}' not found!")
        return
    
    files = [f for f in samples_path.iterdir() if f.is_file()]
    
    if not files:
        print(f"No files found in '{samples_path}' directory!")
        return
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        print(f"\nProcessing {i}/{len(files)}: {file_path.name}")
        print("-" * 60)
        
        try:
            # Extract structured data
            structured_data = extractor.extract_invoice_data(str(file_path))
            
            # Summary for console output
            status = structured_data["processing_status"]["status"]
            extraction_metadata = structured_data.get("extractionMetadata", {})
            fields_extracted = extraction_metadata.get("extracted_fields_count", 0)
            confidence = extraction_metadata.get("overall_confidence", 0.0)
            
            if status == "success":
                print(f"✅ Success: Extracted {fields_extracted} fields (confidence: {confidence:.2f})")
                
                # Show key extracted data from new schema
                data = structured_data.get("data", {})
                
                # Invoice number
                invoice_num = data.get("invoiceNumber", {}).get("parsed")
                if invoice_num:
                    print(f"   📄 Bill Number: {invoice_num}")
                
                # Customer name
                customer_name = data.get("customerInfo", {}).get("name", {}).get("parsed")
                if customer_name:
                    print(f"   👤 Customer: {customer_name}")
                
                # Total amount
                total_amount = data.get("billingDetails", {}).get("totalAmount", {}).get("parsed")
                if total_amount:
                    print(f"   💰 Amount: ₹{total_amount}")
                
                # Meter readings for units consumed
                meter_readings = data.get("meterReadings", [])
                if meter_readings and meter_readings[0].get("unitsConsumed"):
                    units = meter_readings[0]["unitsConsumed"]
                    print(f"   ⚡ Units: {units}")
                    
            else:
                error_msg = structured_data["processing_status"].get("error", "Unknown error")
                print(f"❌ Failed: {error_msg}")
            
            # Store result
            results.append({
                'sr_no': i,
                'file_name': file_path.name,
                'status': status,
                'extracted_fields': fields_extracted,
                'confidence_score': confidence,
                'structured_data': structured_data
            })
            
        except Exception as e:
            print(f"❌ Critical error processing {file_path.name}: {str(e)}")
            results.append({
                'sr_no': i,
                'file_name': file_path.name,
                'status': 'error',
                'extracted_fields': 0,
                'confidence_score': 0.0,
                'structured_data': extractor._create_error_response(str(e), file_path.name)
            })
    
    # Generate output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate detailed JSON with all structured data
    json_filename = f"llm_extracted_data_{timestamp}.json"
    generate_detailed_json(results, json_filename)
    
    # Generate summary CSV
    csv_filename = f"llm_extraction_summary_{timestamp}.csv"
    generate_summary_csv(results, csv_filename)
    
    # Print final summary
    print("\n" + "=" * 80)
    print("INTEGRATED EXTRACTION COMPLETE")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    avg_confidence = sum(r['confidence_score'] for r in results if r['status'] == 'success') / max(successful, 1)
    total_fields = sum(r['extracted_fields'] for r in results)
    
    print(f"Total files processed: {len(results)}")
    print(f"Successful extractions: {successful}")
    print(f"Failed extractions: {failed}")
    print(f"Average confidence: {avg_confidence:.2f}")
    print(f"Total fields extracted: {total_fields}")
    print(f"\nOutput files generated:")
    print(f"  📊 Detailed JSON: {json_filename}")
    print(f"  📋 Summary CSV: {csv_filename}")


def generate_detailed_json(results, filename):
    """Generate detailed JSON with all structured data."""
    try:
        output_data = {
            "extraction_summary": {
                "processed_at": datetime.now().isoformat(),
                "total_files": len(results),
                "successful_extractions": sum(1 for r in results if r['status'] == 'success'),
                "failed_extractions": sum(1 for r in results if r['status'] != 'success'),
                "total_fields_extracted": sum(r['extracted_fields'] for r in results),
                "average_confidence": sum(r['confidence_score'] for r in results if r['status'] == 'success') / max(sum(1 for r in results if r['status'] == 'success'), 1),
                "extraction_method": "integrated_ocr_llm"
            },
            "extracted_data": [
                {
                    "file_info": {
                        "sr_no": result['sr_no'],
                        "file_name": result['file_name'],
                        "processing_status": result['status'],
                        "fields_extracted": result['extracted_fields'],
                        "confidence_score": result['confidence_score']
                    },
                    "invoice_data": result['structured_data']
                }
                for result in results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Detailed JSON saved: {filename}")
        
    except Exception as e:
        print(f"✗ Failed to generate detailed JSON: {e}")


def generate_summary_csv(results, filename):
    """Generate enhanced summary CSV for the new schema."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Sr_No', 'File_Name', 'Status', 'Fields_Extracted', 'Confidence_Score',
                'Bill_Number_Raw', 'Bill_Number_Parsed', 'Customer_Name_Raw', 'Customer_Name_Parsed',
                'Total_Amount_Raw', 'Total_Amount_Parsed', 'Units_Consumed', 'Company_Name_Raw', 
                'Company_Name_Parsed', 'Bill_Date_Raw', 'Bill_Date_Parsed', 'Due_Date_Raw', 'Due_Date_Parsed',
                'LLM_Extracted_Output', 'LLM_Accuracy'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                structured_data = result['structured_data']
                data = structured_data.get('data', {})
                metadata = structured_data.get('extractionMetadata', {})
                
                # Get first meter reading for units consumed
                meter_readings = data.get('meterReadings', [])
                units_consumed = meter_readings[0].get('unitsConsumed', '') if meter_readings else ''
                
                # Create a summary of extracted output
                llm_output_summary = f"Fields: {metadata.get('extracted_fields_count', 0)}/{metadata.get('total_possible_fields', 0)}, " + \
                                   f"Confidence: {metadata.get('overall_confidence', 0):.2f}, " + \
                                   f"Quality: {metadata.get('quality_score', 0):.2f}"
                
                writer.writerow({
                    'Sr_No': result['sr_no'],
                    'File_Name': result['file_name'],
                    'Status': result['status'],
                    'Fields_Extracted': result['extracted_fields'],
                    'Confidence_Score': f"{result['confidence_score']:.2f}",
                    'Bill_Number_Raw': data.get('invoiceNumber', {}).get('raw', ''),
                    'Bill_Number_Parsed': data.get('invoiceNumber', {}).get('parsed', ''),
                    'Customer_Name_Raw': data.get('customerInfo', {}).get('name', {}).get('raw', ''),
                    'Customer_Name_Parsed': data.get('customerInfo', {}).get('name', {}).get('parsed', ''),
                    'Total_Amount_Raw': data.get('billingDetails', {}).get('totalAmount', {}).get('raw', ''),
                    'Total_Amount_Parsed': data.get('billingDetails', {}).get('totalAmount', {}).get('parsed', ''),
                    'Units_Consumed': units_consumed,
                    'Company_Name_Raw': data.get('utilityInfo', {}).get('companyName', {}).get('raw', ''),
                    'Company_Name_Parsed': data.get('utilityInfo', {}).get('companyName', {}).get('parsed', ''),
                    'Bill_Date_Raw': data.get('billingDate', {}).get('raw', ''),
                    'Bill_Date_Parsed': data.get('billingDate', {}).get('parsed', ''),
                    'Due_Date_Raw': data.get('billingDetails', {}).get('dueDate', {}).get('raw', ''),
                    'Due_Date_Parsed': data.get('billingDetails', {}).get('dueDate', {}).get('parsed', ''),
                    'LLM_Extracted_Output': llm_output_summary,
                    'LLM_Accuracy': f"{metadata.get('overall_confidence', 0):.2f}"
                })
        
        print(f"✓ Enhanced Summary CSV saved: {filename}")
        
    except Exception as e:
        print(f"✗ Failed to generate summary CSV: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrated OCR + LLM Invoice Data Extraction")
    parser.add_argument("--api-key", help="OpenAI API key (overrides .env file)")
    parser.add_argument("--samples-dir", help="Directory containing invoice files (overrides .env file)")
    parser.add_argument("--model", help="OpenAI model to use (overrides .env file)")
    
    args = parser.parse_args()
    
    batch_extract_with_llm(args.samples_dir, args.api_key, args.model)
