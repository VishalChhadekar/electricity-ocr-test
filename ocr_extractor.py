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
    """Optimized OCR extractor with smart caching and performance improvements."""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}

    def __init__(self):
        """Initialize the reliable OCR extractor."""
        self.setup_logging()
        
        # Remove aggressive caching that can cause inconsistency
        self._preprocessed_cache = {}  # Keep minimal cache
        self._last_image_hash = None
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_image_hash(self, image):
        """Quick hash of image for caching"""
        import hashlib
        return hashlib.md5(image.tobytes()).hexdigest()[:16]
    
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
        Ultra-optimized multi-strategy OCR with aggressive early exit and language optimization
        """
        
        # Strategy definitions with optimized language sets
        strategies = [
            {
                'name': 'comprehensive_primary',
                'config': '--psm 6 --oem 3',
                'preprocessing': 'standard',
                'languages': 'eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san',
                'min_chars': 150,
                'priority': 1
            },
            {
                'name': 'table_focused', 
                'config': '--psm 6 --oem 3 -c preserve_interword_spaces=1',
                'preprocessing': 'table_aware',
                'languages': 'eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san',
                'min_chars': 100,
                'priority': 2
            },
            {
                'name': 'fallback_psm4',
                'config': '--psm 4 --oem 3',
                'preprocessing': 'line_by_line',
                'languages': 'eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san',
                'min_chars': 50,
                'priority': 3
            }
        ]
        
        best_result = ""
        best_score = 0
        
        for strategy in strategies:
            try:
                start_time = self._get_time()
                
                # Get preprocessed image (cached)
                processed_image = self.preprocess_image(image, strategy['preprocessing'])
                
                # Run OCR with full language set
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=strategy['languages'],
                    config=strategy['config']
                )
                
                # Quality check
                text_length = len(text.strip())
                if text_length < strategy['min_chars']:
                    self.logger.debug(f"Strategy '{strategy['name']}': insufficient content ({text_length} chars)")
                    continue
                
                # Full quality assessment for reliability
                processed_text = self._post_process_multilingual_text(text)
                score = self._calculate_text_quality_score(processed_text)
                
                processing_time = self._get_time() - start_time
                self.logger.debug(f"Strategy '{strategy['name']}': {len(processed_text)} chars, score: {score}, time: {processing_time:.2f}s")
                
                # Update best result if this is better
                if score > best_score:
                    best_score = score
                    best_result = processed_text
                    self.logger.info(f"New best result from '{strategy['name']}' with score: {score}")
                
                # Only exit early if we have a very high-quality result
                if score > 500 and strategy['priority'] == 1:
                    self.logger.info(f"High-quality result achieved with primary strategy (score: {score})")
                    break
                    
            except Exception as e:
                self.logger.warning(f"Strategy '{strategy['name']}' failed: {e}")
                continue
        
        if not best_result:
            self.logger.warning("All strategies failed, trying minimal English fallback...")
            return self._minimal_english_fallback(image)
        
        self.logger.info(f"Final best result selected with score: {best_score}")
        return best_result
    
    def _ultra_fast_quality_score(self, text: str) -> int:
        """
        Ultra-fast quality scoring for immediate early exit decisions
        """
        if not text or len(text.strip()) < 20:
            return 0
        
        score = len(text.strip()) // 2  # Base score (faster than full length)
        
        # Ultra-fast indicators (single character checks)
        if '₹' in text or 'र' in text:  # Currency or Hindi
            score += 30
        if any(char.isdigit() for char in text[:100]):  # Numbers in first 100 chars
            score += 40
        if 'Bill' in text[:50] or 'बिल' in text[:50]:  # Bill indicators early
            score += 50
        
        return score
    
    def _minimal_english_fallback(self, image):
        """
        Minimal English-only fallback for absolute worst-case scenarios
        """
        try:
            # Use cached standard preprocessing
            processed_image = self.preprocess_image(image, 'standard')
            text = pytesseract.image_to_string(
                processed_image,
                lang='eng',  # English only
                config='--psm 6 --oem 3'  # Simplest, fastest config
            )
            return text.strip()  # Skip post-processing for speed
        except Exception as e:
            self.logger.error(f"Minimal English fallback failed: {e}")
            return ""
    
    def _calculate_text_quality_score(self, text: str) -> int:
        """
        Fast quality scoring for OCR results to enable early exit
        """
        import re
        
        if not text or len(text.strip()) < 50:
            return 0
        
        score = len(text.strip())  # Base score on length
        
        # Quick bonuses for key indicators (no expensive regex)
        if 'Bill' in text or 'बिल' in text:
            score += 50
        if 'Meter' in text or 'मीटर' in text:
            score += 50  
        if 'Customer' in text or 'ग्राहक' in text:
            score += 30
        if '₹' in text or 'Rs' in text or 'रु' in text:
            score += 40
        
        # Bonus for numbers (indicates structured data)
        digit_count = sum(1 for c in text if c.isdigit())
        score += min(digit_count * 2, 100)  # Cap bonus at 100
        
        # Bonus for hyphens (meter numbers, account numbers)
        hyphen_count = text.count('-')
        score += min(hyphen_count * 20, 60)  # Cap bonus at 60
        
        # Penalty for too many special characters (OCR noise)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and c not in ' \n\t\r.,()-:') / max(len(text), 1)
        if special_char_ratio > 0.1:
            score -= int(special_char_ratio * 100)
        
        return max(score, 0)
    
    def _fallback_english_extraction(self, image):
        """
        Fast English-only fallback when all other strategies fail
        """
        try:
            processed_image = self.preprocess_image(image, 'standard')
            text = pytesseract.image_to_string(
                processed_image,
                lang='eng',  # English only for speed
                config='--psm 6 --oem 3'
            )
            return self._post_process_multilingual_text(text)
        except Exception as e:
            self.logger.error(f"English fallback failed: {e}")
            return ""
    
    def _get_time(self):
        """Get current time for performance measurement"""
        import time
        return time.time()
    
    def extract_text(self, image: Image.Image) -> str:
        """Optimized text extraction with smart cascading strategies and early exit."""
        self.logger.info("Starting optimized multi-strategy OCR extraction...")
        
        # Clear cache if we're processing a new image
        current_hash = self._get_image_hash(image)
        if self._last_image_hash != current_hash:
            self._preprocessed_cache.clear()
            self._last_image_hash = current_hash
        
        start_time = self._get_time()
        
        # Use optimized table-aware strategy approach
        best_text = self._extract_with_table_aware_strategies(image)
        
        # Fast English fallback only if comprehensive extraction failed
        if not best_text or len(best_text) < 50:
            self.logger.warning("Multi-language extraction insufficient, trying fast English fallback...")
            best_text = self._fallback_english_extraction(image)
        
        total_time = self._get_time() - start_time
        self.logger.info(f"OCR completed in {total_time:.2f}s: {len(best_text)} characters extracted")
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
        """
        Reliable preprocessing with minimal caching to ensure consistency
        """
        # Clear cache periodically to prevent stale results
        if len(self._preprocessed_cache) > 5:
            self._preprocessed_cache.clear()
            self.logger.debug("Cleared preprocessing cache for reliability")
        
        # Create cache key
        image_hash = self._get_image_hash(image)
        cache_key = f"{image_hash}_{strategy}"
        
        # Check cache but limit its use
        if cache_key in self._preprocessed_cache:
            self.logger.debug(f"Using cached preprocessing for {strategy}")
            return self._preprocessed_cache[cache_key]
        
        self.logger.debug(f"Preprocessing image for {strategy} OCR strategy...")
        
        # Convert to grayscale if not already
        if image.mode != 'L':
            processed_image = image.convert('L')
        else:
            processed_image = image.copy()
        
        # Strategy-specific preprocessing (optimized)
        if strategy == 'table_aware':
            # Stronger contrast for table borders
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(2.0)
            
            # Moderate sharpness 
            enhancer = ImageEnhance.Sharpness(processed_image)
            processed_image = enhancer.enhance(1.5)
            
            # Minimal blur
            processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius=0.3))
            
        elif strategy == 'line_by_line':
            # High contrast and sharpness for individual lines
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(2.2)
            
            enhancer = ImageEnhance.Sharpness(processed_image)
            processed_image = enhancer.enhance(2.5)
            
            processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius=0.2))
            
        else:  # standard strategy (fastest, most common)
            # Balanced enhancement
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(1.5)
            
            enhancer = ImageEnhance.Sharpness(processed_image)
            processed_image = enhancer.enhance(2.0)
            
            processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Cache the result (limit cache size to prevent memory issues)
        if len(self._preprocessed_cache) > 10:  # Limit cache size
            # Remove oldest entry
            oldest_key = next(iter(self._preprocessed_cache))
            del self._preprocessed_cache[oldest_key]
        
        self._preprocessed_cache[cache_key] = processed_image
        return processed_image
    
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
