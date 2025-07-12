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
    
    def _post_process_multilingual_text(self, raw_text: str) -> str:
        """
        Post-process OCR text to handle multi-language issues and improve accuracy
        """
        import re
        
        self.logger.debug("Starting post-processing of multilingual OCR text...")
        processed_text = raw_text
        
        # 1. Clean up excessive whitespace but preserve structure
        processed_text = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_text)
        processed_text = re.sub(r'[ \t]+', ' ', processed_text)  # Multiple spaces to single space
        
        # 2. Fix common Hindi-English boundary issues
        processed_text = re.sub(r'([a-zA-Z])\s*([ऀ-ॿ])', r'\1 \2', processed_text)
        processed_text = re.sub(r'([ऀ-ॿ])\s*([a-zA-Z])', r'\1 \2', processed_text)
        
        # 3. Clean up currency symbols and numbers
        processed_text = re.sub(r'Rs\.\s*(\d+)', r'Rs. \1', processed_text)
        processed_text = re.sub(r'रु\s*(\d+)', r'रु. \1', processed_text)
        processed_text = re.sub(r'₹\s*(\d+)', r'₹ \1', processed_text)
        
        # 4. Fix common date format issues
        processed_text = re.sub(r'(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})', r'\1-\2-\3', processed_text)
        
        # 5. Remove excessive special characters but preserve important ones
        processed_text = re.sub(r'[‏‎۱۲۳۰-۹]+', '', processed_text)  # Remove Arabic-Indic digits artifacts
        processed_text = re.sub(r'[੧੦ਕਿਗ]+', '', processed_text)  # Remove Gurmukhi artifacts
        processed_text = re.sub(r'[০-৯৪৬৮ৰ]+', '', processed_text)  # Remove Bengali digit artifacts
        
        # 6. Fix common meter reading table issues
        processed_text = re.sub(r'मीटर\s*संख्या', 'मीटर संख्या', processed_text)
        processed_text = re.sub(r'Meter\s*No', 'Meter No', processed_text)
        processed_text = re.sub(r'बिल\s*संख्या', 'बिल संख्या', processed_text)
        processed_text = re.sub(r'Bill\s*No', 'Bill No', processed_text)
        
        # 7. Clean up GST-related text (common issue in bills)
        processed_text = re.sub(r'एसजीएसटी\s*(?:ए|८|9)', 'एसजीएसटी 9%', processed_text)
        processed_text = re.sub(r'सीजीएसटी\s*(?:९|9)', 'सीजीएसटी 9%', processed_text)
        
        # 8. Fix phone number formatting
        processed_text = re.sub(r'(\d{3})XXXX(\d{3})', r'\1XXXXX\2', processed_text)
        processed_text = re.sub(r'(\d{10})', r'\1', processed_text)  # Keep 10-digit numbers intact
        
        # 9. Remove standalone single characters that are OCR artifacts
        processed_text = re.sub(r'\n[^\w\s]\n', '\n', processed_text)
        
        self.logger.debug(f"Post-processing completed: {len(processed_text)} characters")
        return processed_text.strip()
    
    def _extract_with_multiple_strategies(self, image, strategies=['standard', 'enhanced', 'table_focused']):
        """
        Try multiple OCR strategies and combine results intelligently
        """
        results = {}
        comprehensive_langs = 'eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san'
        
        for strategy in strategies:
            try:
                if strategy == 'standard':
                    # Standard OCR with balanced preprocessing
                    processed_image = self.preprocess_image(image, 'standard')
                    text = pytesseract.image_to_string(
                        processed_image,
                        lang=comprehensive_langs,
                        config='--psm 6 --oem 3'
                    )
                elif strategy == 'enhanced':
                    # OCR with different PSM for mixed content
                    processed_image = self.preprocess_image(image, 'line_by_line')
                    text = pytesseract.image_to_string(
                        processed_image,
                        lang=comprehensive_langs,
                        config='--psm 3 --oem 3'  # Fully automatic page segmentation
                    )
                elif strategy == 'table_focused':
                    # OCR optimized for tabular data
                    processed_image = self.preprocess_image(image, 'table_aware')
                    text = pytesseract.image_to_string(
                        processed_image,
                        lang=comprehensive_langs,
                        config='--psm 6 --oem 3 -c preserve_interword_spaces=1'
                    )
                
                # Post-process each result
                text = self._post_process_multilingual_text(text)
                results[strategy] = text
                self.logger.debug(f"Strategy '{strategy}': {len(text)} characters extracted")
                
            except Exception as e:
                self.logger.warning(f"Strategy {strategy} failed: {e}")
                results[strategy] = ""
        
        # Combine results intelligently
        return self._combine_ocr_results(results)
    
    def _combine_ocr_results(self, results):
        """
        Intelligently combine multiple OCR results to get the best text
        """
        if not results:
            return ""
        
        # Filter out empty results
        valid_results = {k: v for k, v in results.items() if v.strip()}
        
        if not valid_results:
            return ""
        
        # Use the longest result as base (usually captures more content)
        best_strategy = max(valid_results.keys(), key=lambda k: len(valid_results[k]))
        best_result = valid_results[best_strategy]
        
        # Log comparison for debugging
        for strategy, text in valid_results.items():
            self.logger.info(f"Strategy '{strategy}': {len(text)} characters")
        
        self.logger.info(f"Selected best result from '{best_strategy}' strategy")
        return best_result

    def extract_text(self, image: Image.Image) -> str:
        """Extract text using enhanced multi-strategy OCR with comprehensive post-processing."""
        self.logger.info("Starting enhanced multi-strategy OCR extraction...")
        
        # Use multi-strategy approach with intelligent combination
        best_text = self._extract_with_multiple_strategies(image)
        
        # Fallback to English if all comprehensive attempts fail
        if not best_text or len(best_text) < 50:
            try:
                self.logger.warning("Multi-language extraction insufficient, trying English fallback...")
                processed_image = self.preprocess_image(image, 'standard')
                text = pytesseract.image_to_string(
                    processed_image,
                    lang='eng',
                    config='--psm 6 --oem 3 -c preserve_interword_spaces=1'
                )
                best_text = self._post_process_multilingual_text(text)
                self.logger.info(f"English fallback result: {len(best_text)} characters")
            except Exception as e:
                self.logger.error(f"English fallback failed: {e}")
                return ""
        
        self.logger.info(f"Final OCR result: {len(best_text)} characters extracted")
        return best_text
    
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
    
    def preprocess_image(self, image: Image.Image, strategy: str = 'standard') -> Image.Image:
        """Preprocess image to improve OCR accuracy with strategy-specific optimizations."""
        self.logger.debug(f"Preprocessing image for {strategy} OCR strategy...")
        
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')
        
        # Strategy-specific preprocessing
        if strategy == 'table_aware':
            # Stronger contrast enhancement for table borders
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Moderate sharpness to preserve table structure
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            # Minimal blur to preserve table lines
            image = image.filter(ImageFilter.GaussianBlur(radius=0.3))
            
        elif strategy == 'line_by_line':
            # High contrast for individual line processing
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.2)
            
            # High sharpness for character clarity
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.5)
            
            # Very light blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.2))
            
        else:  # standard strategy
            # Balanced enhancement for general text
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhanced sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Light gaussian blur to reduce noise
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
