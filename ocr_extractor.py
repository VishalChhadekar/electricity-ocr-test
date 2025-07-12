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
        Advanced post-processing to handle multi-language issues and improve accuracy
        Addresses specific issues: hyphenated numbers, terminology variations, abbreviated terms
        """
        import re
        
        self.logger.debug("Starting advanced post-processing of multilingual OCR text...")
        processed_text = raw_text
        
        # 1. Fix hyphenated meter numbers and similar patterns
        # Common patterns: 123456-789, ABC123-DEF456, etc.
        processed_text = re.sub(r'(\d+)\s*[-–—]\s*(\d+)', r'\1-\2', processed_text)
        processed_text = re.sub(r'([A-Z]+\d+)\s*[-–—]\s*(\d+)', r'\1-\2', processed_text)
        processed_text = re.sub(r'(\d+)\s*[-–—]\s*([A-Z]+\d+)', r'\1-\2', processed_text)
        
        # 2. Fix common OCR spacing issues that break hyphenated numbers
        processed_text = re.sub(r'(\d+)\s+[-–—]\s+(\d+)', r'\1-\2', processed_text)
        processed_text = re.sub(r'(\d+)[-–—]\s+(\d+)', r'\1-\2', processed_text)
        processed_text = re.sub(r'(\d+)\s+[-–—](\d+)', r'\1-\2', processed_text)
        
        # 3. Standardize terminology variations for better LLM recognition
        terminology_fixes = {
            # Consumption variations
            r'Net\s+Consumption': 'Total Unit Consumption',
            r'Net\s+Units': 'Total Unit Consumption', 
            r'Consumption\s+Units': 'Total Unit Consumption',
            r'Units\s+Consumed': 'Total Unit Consumption',
            
            # Meter number variations
            r'RRNO\.?': 'Meter Number',
            r'RR\s+No\.?': 'Meter Number',
            r'RR\.Number': 'Meter Number',
            r'Meter\s+Code': 'Meter Number',
            r'MRCode': 'Meter Number',
            r'MR\s+Code': 'Meter Number',
            
            # Hindi/Marathi abbreviations
            r'एकण\s*युनिट': 'एकण युनिट',
            r'एकण(?!\s*युनिट)': 'एकण युनिट',  # Add युनिट if missing
            r'यूनिट्स': 'युनिट',
            r'कंझम्पशन': 'खपत',
            
            # Bill number variations
            r'Bill\s+No\.?': 'Bill Number',
            r'बिल\s+क्र\.?': 'बिल संख्या',
            r'Invoice\s+No\.?': 'Invoice Number',
        }
        
        for pattern, replacement in terminology_fixes.items():
            processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE)
        
        # 4. Clean up excessive whitespace but preserve table structure
        processed_text = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_text)
        processed_text = re.sub(r'[ \t]+', ' ', processed_text)
        
        # 5. Fix common Hindi-English boundary issues
        processed_text = re.sub(r'([a-zA-Z])\s*([ऀ-ॿ])', r'\1 \2', processed_text)
        processed_text = re.sub(r'([ऀ-ॿ])\s*([a-zA-Z])', r'\1 \2', processed_text)
        
        # 6. Preserve table formatting - fix common table separators
        processed_text = re.sub(r'\|\s*\|', '|', processed_text)  # Fix double pipes
        processed_text = re.sub(r'\s*\|\s*', ' | ', processed_text)  # Standardize pipe spacing
        
        # 7. Fix currency and number formatting
        processed_text = re.sub(r'Rs\.?\s*(\d+)', r'Rs. \1', processed_text)
        processed_text = re.sub(r'रु\.?\s*(\d+)', r'रु. \1', processed_text)
        processed_text = re.sub(r'₹\s*(\d+)', r'₹ \1', processed_text)
        
        # 8. Fix date formatting
        processed_text = re.sub(r'(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})', r'\1-\2-\3', processed_text)
        
        # 9. Remove OCR artifacts while preserving important characters
        processed_text = re.sub(r'[‏‎۱۲۳۰-۹]+', '', processed_text)  # Arabic-Indic digits
        processed_text = re.sub(r'[੧੦ਕਿਗ]+', '', processed_text)  # Gurmukhi artifacts
        processed_text = re.sub(r'[০-৯৪৬৮ৰ]+', '', processed_text)  # Bengali artifacts
        
        # 10. Fix GST-related text
        processed_text = re.sub(r'एसजीएसटी\s*(?:ए|८|9)', 'एसजीएसटी 9%', processed_text)
        processed_text = re.sub(r'सीजीएसटी\s*(?:९|9)', 'सीजीएसटी 9%', processed_text)
        
        # 11. Clean up phone numbers
        processed_text = re.sub(r'(\d{3})XXXX(\d{3})', r'\1XXXXX\2', processed_text)
        
        # 12. Remove standalone artifacts
        processed_text = re.sub(r'\n[^\w\s]\n', '\n', processed_text)
        
        self.logger.debug(f"Advanced post-processing completed: {len(processed_text)} characters")
        return processed_text.strip()
    
    def _extract_with_table_aware_strategies(self, image):
        """
        Enhanced multi-strategy OCR specifically designed for table recognition
        """
        results = {}
        comprehensive_langs = 'eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san'
        
        # Strategy 1: Standard OCR
        try:
            processed_image = self.preprocess_image(image, 'standard')
            text = pytesseract.image_to_string(
                processed_image,
                lang=comprehensive_langs,
                config='--psm 6 --oem 3'
            )
            results['standard'] = self._post_process_multilingual_text(text)
            self.logger.debug(f"Standard strategy: {len(results['standard'])} characters")
        except Exception as e:
            self.logger.warning(f"Standard strategy failed: {e}")
            results['standard'] = ""
        
        # Strategy 2: Table-focused OCR with preserved spacing
        try:
            processed_image = self.preprocess_image(image, 'table_aware')
            text = pytesseract.image_to_string(
                processed_image,
                lang=comprehensive_langs,
                config='--psm 6 --oem 3 -c preserve_interword_spaces=1 -c page_separator=""'
            )
            results['table_focused'] = self._post_process_multilingual_text(text)
            self.logger.debug(f"Table-focused strategy: {len(results['table_focused'])} characters")
        except Exception as e:
            self.logger.warning(f"Table-focused strategy failed: {e}")
            results['table_focused'] = ""
        
        # Strategy 3: Line-by-line for complex layouts
        try:
            processed_image = self.preprocess_image(image, 'line_by_line')
            text = pytesseract.image_to_string(
                processed_image,
                lang=comprehensive_langs,
                config='--psm 4 --oem 3 -c preserve_interword_spaces=1'
            )
            results['line_by_line'] = self._post_process_multilingual_text(text)
            self.logger.debug(f"Line-by-line strategy: {len(results['line_by_line'])} characters")
        except Exception as e:
            self.logger.warning(f"Line-by-line strategy failed: {e}")
            results['line_by_line'] = ""
        
        # Strategy 4: Sparse text mode for difficult cases
        try:
            processed_image = self.preprocess_image(image, 'standard')
            text = pytesseract.image_to_string(
                processed_image,
                lang=comprehensive_langs,
                config='--psm 8 --oem 3'  # Treat image as single word
            )
            results['sparse_text'] = self._post_process_multilingual_text(text)
            self.logger.debug(f"Sparse text strategy: {len(results['sparse_text'])} characters")
        except Exception as e:
            self.logger.warning(f"Sparse text strategy failed: {e}")
            results['sparse_text'] = ""
        
        return self._intelligently_combine_results(results)
    
    def _intelligently_combine_results(self, results):
        """
        Intelligently combine multiple OCR results focusing on table preservation and completeness
        """
        import re
        
        if not results:
            return ""
        
        # Filter out empty results
        valid_results = {k: v for k, v in results.items() if v.strip()}
        
        if not valid_results:
            return ""
        
        # Scoring system for result quality
        scored_results = []
        for strategy, text in valid_results.items():
            score = len(text)  # Base score on length
            
            # Bonus for table indicators
            if '|' in text or 'Meter Number' in text or 'मीटर संख्या' in text:
                score += 200
            
            # Bonus for hyphenated numbers (likely meter numbers)
            hyphen_count = len(re.findall(r'\d+-\d+', text))
            score += hyphen_count * 100
            
            # Bonus for key terminology
            key_terms = ['Total Unit Consumption', 'Net Consumption', 'RRNO', 'एकण युनिट']
            for term in key_terms:
                if term in text:
                    score += 50
            
            scored_results.append((strategy, text, score))
        
        # Select best result based on score
        best_strategy, best_text, best_score = max(scored_results, key=lambda x: x[2])
        
        # Log results for debugging
        for strategy, text, score in scored_results:
            self.logger.info(f"Strategy '{strategy}': {len(text)} chars, score: {score}")
        
        self.logger.info(f"Selected best result from '{best_strategy}' strategy (score: {best_score})")
        return best_text

    def extract_text(self, image: Image.Image) -> str:
        """Extract text using enhanced table-aware multi-strategy OCR with comprehensive post-processing."""
        self.logger.info("Starting enhanced table-aware multi-strategy OCR extraction...")
        
        # Use enhanced table-aware strategy approach
        best_text = self._extract_with_table_aware_strategies(image)
        
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
