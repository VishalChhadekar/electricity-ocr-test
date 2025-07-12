#!/usr/bin/env python3
"""
Simple OCR Text Extractor for Electricity Bills
Extracts raw text from PDF and image files using Tesseract OCR
Simplified version without language detection - for use with LLM/NLP processing
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List
import logging
import uuid

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"Error: Required package not installed. {e}")
    print("Please install requirements using: pip install -r requirements.txt")
    sys.exit(1)


class OCRExtractor:
    """Simple OCR extractor that focuses only on text extraction without language detection."""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}

    def __init__(self):
        """Initialize the simple OCR extractor."""
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, image: Image.Image) -> str:
        """Extract text using a simple, fast OCR approach."""
        processed_image = self.preprocess_image(image)
        
        # Comprehensive Indian language set for complete electricity bill coverage
        # All major Indian languages used in electricity bills across states (14 languages)
        comprehensive_langs = 'eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san'
        
        try:
            text = pytesseract.image_to_string(
                processed_image,
                lang=comprehensive_langs,
                config=r'--oem 3 --psm 6'
            )
            return text.strip()
        except Exception as e:
            self.logger.warning(f"Comprehensive OCR failed: {e}. Trying English only.")
            # Fallback to English only if comprehensive fails
            try:
                text = pytesseract.image_to_string(
                    processed_image,
                    lang='eng',
                    config=r'--oem 3 --psm 6'
                )
                return text.strip()
            except Exception as e:
                self.logger.error(f"OCR extraction failed: {e}")
                return ""
    
    def validate_file(self, file_path: str) -> Path:
        """Validate if the file exists and has a supported extension."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            supported_exts = ', '.join(self.SUPPORTED_EXTENSIONS)
            raise ValueError(
                f"Unsupported file extension: {path.suffix}. "
                f"Supported extensions: {supported_exts}"
            )
        
        return path
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy."""
        self.logger.debug("Preprocessing image for better OCR accuracy...")
        
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight gaussian blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def pdf_to_images(self, pdf_path: Path) -> List[Image.Image]:
        """Convert PDF pages to images."""
        self.logger.info(f"Converting PDF to images: {pdf_path}")
        
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=300,
                fmt='PNG'
            )
            self.logger.info(f"Successfully converted {len(images)} pages from PDF")
            return images
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF to images: {e}")
    
    def extract_text_from_image(self, image: Image.Image, page_num: int = 1) -> str:
        """Extract text from a single image using simple OCR."""
        try:
            self.logger.info(f"Processing page {page_num}")
            text = self.extract_text(image)
            return text
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}")
    
    def extract_text_from_file(self, file_path: str) -> dict:
        """Extract text from file (PDF or image)."""
        path = self.validate_file(file_path)
        self.logger.info(f"Processing file: {path}")
        
        all_text = []
        
        if path.suffix.lower() == '.pdf':
            images = self.pdf_to_images(path)
        else:
            images = [Image.open(path)]
        
        # Process each page/image
        for i, image in enumerate(images, 1):
            text = self.extract_text_from_image(image, i)
            
            if text:
                if len(images) > 1:
                    all_text.append(f"=== Page {i} ===\n{text}")
                else:
                    all_text.append(text)
        
        combined_text = "\n\n".join(all_text)
        self.logger.info(f"Successfully extracted {len(combined_text)} characters of text")
        
        return {
            'text': combined_text,
            'text_length': len(combined_text)
        }
    
    def create_json_output(self, extraction_result: dict, file_path: str) -> dict:
        """Create JSON output with raw OCR text."""
        path = Path(file_path)
        
        raw_text = extraction_result['text']
        
        output = {
            "data": {
                "rawText": raw_text,
                "textLength": len(raw_text),
                "extractedAt": datetime.now().isoformat(),
                "fileName": path.name,
                "fileExtension": path.suffix.lower(),
                "ocrEngine": "tesseract",
                "extractionId": str(uuid.uuid4())
            },
            "error": {
                "errorCode": None,
                "errorDetail": None
            },
            "status": "success"
        }
        
        return output
    
    def process_file(self, file_path: str) -> dict:
        """Process file and return OCR results in JSON format."""
        try:
            # Extract text
            extraction_result = self.extract_text_from_file(file_path)
            
            # Create JSON output
            result = self.create_json_output(extraction_result, file_path)
            
            return result
            
        except Exception as e:
            # Return error in JSON format
            return {
                "data": {
                    "rawText": "",
                    "textLength": 0,
                    "extractedAt": datetime.now().isoformat(),
                    "fileName": Path(file_path).name if file_path else "unknown",
                    "fileExtension": "",
                    "ocrEngine": "tesseract",
                    "extractionId": str(uuid.uuid4())
                },
                "error": {
                    "errorCode": "EXTRACTION_FAILED",
                    "errorDetail": str(e)
                },
                "status": "failed"
            }


def main():
    """Main function to handle command line arguments and run OCR."""
    parser = argparse.ArgumentParser(
        description="Simple OCR Text Extractor for Electricity Bills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ocr_extractor_simple.py --file "bill.pdf"
  python ocr_extractor_simple.py --file "bill.pdf" --output result.json --pretty
  python ocr_extractor_simple.py --file image.jpg --text-only
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        required=True,
        help='Path to the input file (PDF, JPG, JPEG, PNG)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file path to save results (optional)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        help='Pretty print JSON output'
    )
    
    parser.add_argument(
        '--text-only',
        action='store_true',
        help='Output only the raw text without JSON formatting'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize OCR tool
        ocr_tool = OCRExtractor()
        
        # Process the file
        if args.text_only:
            # Extract and output only raw text
            extraction_result = ocr_tool.extract_text_from_file(args.file)
            raw_text = extraction_result['text']
            print(raw_text)
            
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(raw_text, encoding='utf-8')
                print(f"\nRaw text saved to: {output_path}", file=sys.stderr)
        else:
            # Extract and output JSON
            result = ocr_tool.process_file(args.file)
            
            # Format JSON output
            if args.pretty:
                json_output = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                json_output = json.dumps(result, ensure_ascii=False)
            
            # Output results
            print(json_output)
            
            # Save to output file if specified
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(json_output, encoding='utf-8')
                print(f"\nResults saved to: {output_path}", file=sys.stderr)
            
    except Exception as e:
        error_response = {
            "data": {
                "rawText": "",
                "textLength": 0,
                "extractedAt": datetime.now().isoformat(),
                "fileName": Path(args.file).name if hasattr(args, 'file') and args.file else "unknown",
                "fileExtension": "",
                "ocrEngine": "tesseract",
                "extractionId": str(uuid.uuid4())
            },
            "error": {
                "errorCode": "SYSTEM_ERROR",
                "errorDetail": str(e)
            },
            "status": "failed"
        }
        print(json.dumps(error_response, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
