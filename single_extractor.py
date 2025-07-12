#!/usr/bin/env python3
"""
Single File OCR + LLM Invoice Data Extractor
Tests a single electricity bill file using OCR + OpenAI LLM
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_extractor import OCRExtractor
from llm_extractor import LLMInvoiceExtractor


class SingleFileExtractor:
    """Single file OCR + LLM invoice data extractor."""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        """Initialize the single file extractor."""
        self.ocr_extractor = OCRExtractor()
        self.llm_extractor = LLMInvoiceExtractor(api_key=openai_api_key, model=model)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from a single invoice file using OCR + LLM.
        
        Args:
            file_path: Path to the invoice file
            
        Returns:
            Dictionary containing extraction results
        """
        try:
            file_name = os.path.basename(file_path)
            
            print(f"🔍 Processing file: {file_name}")
            print("=" * 60)
            
            self.logger.info(f"Starting extraction for: {file_name}")
            
            # Step 1: OCR Text Extraction
            print("📄 Step 1: Extracting text using OCR...")
            self.logger.info("Step 1: Extracting raw text using OCR...")
            
            ocr_result = self.ocr_extractor.extract_text(file_path)
            
            if not ocr_result['success']:
                error_msg = f"OCR extraction failed: {ocr_result.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'file_name': file_name
                }
            
            raw_text = ocr_result['text']
            text_length = len(raw_text)
            
            print(f"   ✓ Extracted {text_length} characters")
            self.logger.info(f"OCR extracted {text_length} characters")
            
            if text_length < 50:
                warning_msg = f"Warning: Very short text extracted ({text_length} chars). File might be poor quality."
                print(f"   ⚠️  {warning_msg}")
                self.logger.warning(warning_msg)
            
            # Step 2: LLM Data Extraction
            print("🤖 Step 2: Extracting structured data using LLM...")
            self.logger.info("Step 2: Extracting structured data using LLM...")
            
            llm_result = self.llm_extractor.extract_invoice_data(
                raw_text=raw_text,
                filename=file_name
            )
            
            if not llm_result['success']:
                error_msg = f"LLM extraction failed: {llm_result.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'file_name': file_name,
                    'ocr_text': raw_text
                }
            
            # Extract key information for display
            extracted_data = llm_result['extracted_data']
            confidence = llm_result['confidence']
            fields_extracted = llm_result['fields_extracted']
            
            # Display results
            print(f"   ✓ Confidence: {confidence:.1%}")
            print(f"   ✓ Fields extracted: {fields_extracted}")
            
            # Show key extracted fields
            data = extracted_data.get('data', {})
            
            # Invoice/Bill Number
            invoice_num = data.get('invoiceNumber', {}).get('parsed')
            if invoice_num:
                print(f"   📄 Invoice Number: {invoice_num}")
            
            # Customer Name
            customer_name = data.get('customerInfo', {}).get('name', {}).get('parsed')
            if customer_name:
                print(f"   👤 Customer: {customer_name}")
            
            # Bill Amount
            bill_amount = data.get('billingDetails', {}).get('totalAmount', {}).get('parsed')
            if bill_amount:
                print(f"   💰 Amount: ₹{bill_amount}")
            
            # Units Consumed
            meter_readings = data.get('meterReadings', [])
            if meter_readings and len(meter_readings) > 0:
                units = meter_readings[0].get('unitsConsumed')
                if units:
                    print(f"   ⚡ Units: {units}")
            
            # Reading Dates
            prev_date = data.get('previousReadingDate', {}).get('parsed')
            curr_date = data.get('presentReadingDate', {}).get('parsed')
            if prev_date or curr_date:
                print(f"   📅 Reading: {prev_date or 'N/A'} → {curr_date or 'N/A'}")
            
            self.logger.info(f"Successfully extracted {fields_extracted} fields")
            
            # Prepare result
            result = {
                'success': True,
                'file_info': {
                    'file_name': file_name,
                    'file_path': file_path,
                    'processing_status': 'success',
                    'fields_extracted': fields_extracted,
                    'confidence_score': confidence,
                    'processed_at': datetime.now().isoformat()
                },
                'invoice_data': extracted_data,
                'ocr_metadata': {
                    'raw_text': raw_text,
                    'text_length': text_length,
                    'ocr_engine': 'tesseract'
                }
            }
            
            print("✅ Extraction completed successfully!")
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error during extraction: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'file_name': os.path.basename(file_path) if file_path else 'unknown'
            }


def save_single_result(result: Dict[str, Any], output_file: Optional[str] = None) -> str:
    """
    Save single file extraction result to JSON.
    
    Args:
        result: Extraction result dictionary
        output_file: Optional custom output filename
        
    Returns:
        Path to saved file
    """
    try:
        if output_file:
            filename = output_file
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = result.get('file_info', {}).get('file_name', 'unknown')
            safe_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"single_extraction_{safe_name}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Result saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Failed to save result: {e}")
        return ""


def main():
    """Main function for single file extraction."""
    parser = argparse.ArgumentParser(
        description="Single File OCR + LLM Invoice Data Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python single_extractor.py "file samples/Bihar.pdf"
  python single_extractor.py "file samples/Maharastra.pdf" --output my_result.json
  python single_extractor.py "file samples/Karnataka-Bescom.pdf" --api-key your_key_here
        """
    )
    
    parser.add_argument("file_path", help="Path to the invoice file to process")
    parser.add_argument("--api-key", help="OpenAI API key (overrides .env file)")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use")
    parser.add_argument("--output", help="Output JSON filename (optional)")
    parser.add_argument("--no-save", action="store_true", help="Don't save result to file")
    
    args = parser.parse_args()
    
    # Validate file path
    if not os.path.exists(args.file_path):
        print(f"❌ Error: File not found: {args.file_path}")
        sys.exit(1)
    
    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OpenAI API key not found. Set OPENAI_API_KEY in .env file or use --api-key")
        sys.exit(1)
    
    # Initialize extractor
    print("🚀 Starting Single File OCR + LLM Extraction")
    print("=" * 60)
    
    extractor = SingleFileExtractor(
        openai_api_key=api_key,
        model=args.model
    )
    
    # Extract data
    result = extractor.extract_single_file(args.file_path)
    
    # Display result summary
    print("\n" + "=" * 60)
    if result['success']:
        confidence = result.get('file_info', {}).get('confidence_score', 0)
        fields = result.get('file_info', {}).get('fields_extracted', 0)
        print(f"✅ SUCCESS: {confidence:.1%} confidence, {fields} fields extracted")
        
        # Save result if requested
        if not args.no_save:
            save_single_result(result, args.output)
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
