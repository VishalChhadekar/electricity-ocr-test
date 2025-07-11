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
        
        # Use a comprehensive language set for Indian electricity bills
        # This covers most common languages in a single pass
        comprehensive_langs = 'eng+hin+mar+kan+ben+guj+tam+tel'
        
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
            
            # Poor results - try targeted approach
            else:
                self.logger.info("Poor comprehensive results, trying targeted detection...")
                
                # Try most common language combinations for Indian documents
                fallback_combinations = [
                    ('eng', 'English-only'),
                    ('hin+eng', 'Hindi+English'),
                    ('mar+eng', 'Marathi+English'),
                    ('kan+eng', 'Kannada+English')
                ]
                
                best_result = text
                best_confidence = confidence
                best_lang = 'multi(comprehensive)'
                
                for lang_combo, description in fallback_combinations:
                    try:
                        fallback_text = pytesseract.image_to_string(
                            processed_image,
                            lang=lang_combo,
                            config=r'--oem 3 --psm 6'
                        )
                        fallback_confidence = self.calculate_text_confidence(fallback_text)
                        
                        if fallback_confidence > best_confidence:
                            best_result = fallback_text
                            best_confidence = fallback_confidence
                            best_lang = lang_combo.replace('+', '_')
                            self.logger.info(f"Better result from {description}: conf={fallback_confidence:.2f}")
                            
                    except Exception as e:
                        self.logger.warning(f"Fallback {description} failed: {e}")
                
                return best_result.strip(), best_lang
                
        except Exception as e:
            self.logger.warning(f"Comprehensive detection failed: {e}")
            
            # Ultimate fallback to English
            try:
                self.logger.info("Using English fallback...")
                text = pytesseract.image_to_string(
                    processed_image,
                    lang='eng',
                    config=r'--oem 3 --psm 6'
                )
                return text.strip(), 'eng'
            except Exception as e2:
                self.logger.error(f"All detection methods failed: {e2}")
                return "", 'eng'
    
    def calculate_script_match_bonus(self, text: str, language: str) -> float:
        """Calculate bonus score based on how well the text matches the expected script for the language."""
        if not text or not text.strip():
            return 0.0
        
        # Count characters in different scripts
        script_counts = {
            'latin': 0,
            'devanagari': 0,
            'kannada': 0,
            'tamil': 0,
            'telugu': 0,
            'gujarati': 0,
            'bengali': 0,
            'arabic': 0
        }
        
        total_alpha = 0
        for char in text:
            if char.isalpha():
                total_alpha += 1
                code_point = ord(char)
                
                if code_point < 256:
                    script_counts['latin'] += 1
                elif 0x0900 <= code_point <= 0x097F:
                    script_counts['devanagari'] += 1
                elif 0x0C80 <= code_point <= 0x0CFF:
                    script_counts['kannada'] += 1
                elif 0x0B80 <= code_point <= 0x0BFF:
                    script_counts['tamil'] += 1
                elif 0x0C00 <= code_point <= 0x0C7F:
                    script_counts['telugu'] += 1
                elif 0x0A80 <= code_point <= 0x0AFF:
                    script_counts['gujarati'] += 1
                elif 0x0980 <= code_point <= 0x09FF:
                    script_counts['bengali'] += 1
                elif 0x0600 <= code_point <= 0x06FF:
                    script_counts['arabic'] += 1
        
        if total_alpha == 0:
            return 0.0
        
        # Calculate script ratios
        script_ratios = {k: v / total_alpha for k, v in script_counts.items()}
        
        # Expected script for each language
        language_script_map = {
            'eng': 'latin',
            'hin': 'devanagari',
            'mar': 'devanagari',
            'nep': 'devanagari',
            'san': 'devanagari',
            'kan': 'kannada',
            'tam': 'tamil',
            'tel': 'telugu',
            'guj': 'gujarati',
            'ben': 'bengali',
            'urd': 'arabic',
            'ara': 'arabic'
        }
        
        expected_script = language_script_map.get(language, 'latin')
        script_match_ratio = script_ratios.get(expected_script, 0.0)
        
        # Bonus calculation
        if script_match_ratio > 0.5:
            return 0.3  # Strong match
        elif script_match_ratio > 0.2:
            return 0.15  # Moderate match
        elif script_match_ratio > 0.05:
            return 0.05  # Weak match
        else:
            return 0.0  # No match
    
    def calculate_text_confidence(self, text: str) -> float:
        """Calculate a confidence score for extracted text quality."""
        if not text or not text.strip():
            return 0.0
        
        text = text.strip()
        char_count = len(text)
        
        if char_count == 0:
            return 0.0
        
        # Basic metrics
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.1
        
        # Character type analysis
        alpha_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        space_count = sum(1 for c in text if c.isspace())
        punct_count = sum(1 for c in text if c in '.,;:!?()-')
        
        # Ratios
        alpha_ratio = alpha_count / char_count
        digit_ratio = digit_count / char_count
        space_ratio = space_count / char_count
        
        # Scoring factors
        
        # 1. Text length score (longer text usually better)
        length_score = min(char_count / 500, 1.0)  # Normalize to 500 chars
        
        # 2. Word structure score
        avg_word_length = char_count / word_count if word_count > 0 else 0
        if 2 <= avg_word_length <= 10:  # Reasonable word lengths
            word_structure_score = 0.8
        elif 1 <= avg_word_length <= 15:
            word_structure_score = 0.6
        else:
            word_structure_score = 0.3
        
        # 3. Character composition score
        if alpha_ratio >= 0.4:  # Good amount of alphabetic content
            char_composition_score = min(alpha_ratio, 0.8)
        elif digit_ratio >= 0.3:  # Numeric content (bills have lots of numbers)
            char_composition_score = 0.7
        else:
            char_composition_score = 0.3
        
        # 4. Readability score (penalize too many special characters)
        special_char_ratio = 1 - (alpha_ratio + digit_ratio + space_ratio)
        if special_char_ratio > 0.3:
            readability_score = 0.5  # Too many special characters
        else:
            readability_score = 0.9
        
        # 5. Word count bonus
        if word_count >= 10:
            word_count_score = 0.9
        elif word_count >= 5:
            word_count_score = 0.7
        else:
            word_count_score = 0.5
        
        # Combine scores with weights
        confidence = (
            length_score * 0.25 +
            word_structure_score * 0.2 +
            char_composition_score * 0.25 +
            readability_score * 0.15 +
            word_count_score * 0.15
        )
        
        # Bonus for common patterns in electricity bills
        text_lower = text.lower()
        bill_keywords = ['bill', 'amount', 'date', 'total', 'payment', 'charge', 'electricity', 'meter', 'reading', 'rs', '₹']
        keyword_bonus = sum(0.05 for keyword in bill_keywords if keyword in text_lower)
        confidence += min(keyword_bonus, 0.2)  # Max 0.2 bonus
        
        return min(confidence, 1.0)
    
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
    
    def extract_text_from_image(self, image: Image.Image, page_num: int = 1) -> tuple:
        """Extract text from a single image using Tesseract with language detection."""
        try:
            self.logger.info(f"Processing page {page_num}")
            
            # Extract text with automatic language detection
            text, detected_lang = self.extract_text_with_language_detection(image, page_num)
            
            # Store detected language for reporting
            if detected_lang not in self.detected_languages:
                self.detected_languages.append(detected_lang)
            
            return text, detected_lang
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}")
    
    def extract_text_from_file(self, file_path: str) -> dict:
        """Extract text from file (PDF or image) with language detection results."""
        path = self.validate_file(file_path)
        self.logger.info(f"Processing file: {path}")
        
        all_text = []
        detected_languages = []
        
        if path.suffix.lower() == '.pdf':
            images = self.pdf_to_images(path)
        else:
            images = [Image.open(path)]
        
        # Process each page/image
        for i, image in enumerate(images, 1):
            text, detected_lang = self.extract_text_from_image(image, i)
            
            if text:
                if len(images) > 1:
                    all_text.append(f"=== Page {i} ===\n{text}")
                else:
                    all_text.append(text)
                
                detected_languages.append(detected_lang)
        
        combined_text = "\n\n".join(all_text)
        self.logger.info(f"Successfully extracted {len(combined_text)} characters of text")
        
        # Determine most common detected language
        if detected_languages:
            most_common_lang = max(set(detected_languages), key=detected_languages.count)
        else:
            most_common_lang = self.language if self.language != 'auto' else 'eng'
        
        return {
            'text': combined_text,
            'detected_language': most_common_lang,
            'all_detected_languages': list(set(detected_languages)),
            'page_languages': detected_languages
        }
    
    def create_json_output(self, extraction_result: dict, file_path: str) -> dict:
        """Create JSON output with raw OCR text and language detection results."""
        path = Path(file_path)
        
        raw_text = extraction_result['text']
        detected_lang = extraction_result['detected_language']
        all_detected = extraction_result['all_detected_languages']
        
        # Get language name
        if detected_lang.startswith('multi('):
            if 'comprehensive' in detected_lang:
                lang_name = 'Multiple Languages (Comprehensive Auto-Detection)'
            elif 'indian' in detected_lang:
                lang_name = 'Multiple Indian Languages'
            else:
                lang_name = f'Multiple Languages: {detected_lang}'
        elif '_' in detected_lang:
            # Handle combined languages like 'hin_eng'
            langs = detected_lang.split('_')
            lang_names = [self.SUPPORTED_LANGUAGES.get(lang, lang) for lang in langs]
            lang_name = ' + '.join(lang_names)
        else:
            lang_name = self.SUPPORTED_LANGUAGES.get(detected_lang, f"Unknown ({detected_lang})")
        
        output = {
            "data": {
                "rawText": raw_text,
                "textLength": len(raw_text),
                "extractedAt": datetime.now().isoformat(),
                "detectedLanguage": detected_lang,
                "detectedLanguageName": lang_name,
                "allDetectedLanguages": all_detected,
                "pageLanguages": extraction_result['page_languages'],
                "inputLanguageMode": self.language,
                "autoDetectionEnabled": self.enable_auto_detection,
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
        """Process file and return OCR results in JSON format with automatic language detection."""
        try:
            # Extract text with language detection
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
                    "detectedLanguage": "unknown",
                    "detectedLanguageName": "Unknown",
                    "allDetectedLanguages": [],
                    "pageLanguages": [],
                    "inputLanguageMode": self.language,
                    "autoDetectionEnabled": self.enable_auto_detection,
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
        description="OCR Text Extractor for Electricity Bills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ocr_extractor.py --file "bill.pdf"                    # Auto-detect language
  python ocr_extractor.py --file "bill.pdf" --lang auto        # Explicit auto-detection
  python ocr_extractor.py --file "bill.pdf" --lang hin         # Force Hindi
  python ocr_extractor.py --file image.jpg --output result.json --pretty
  python ocr_extractor.py --file "multiple_pages.pdf" --text-only
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        required=True,
        help='Path to the input file (PDF, JPG, JPEG, PNG)'
    )
    
    parser.add_argument(
        '--lang', '-l',
        default='auto',
        help='Language code for OCR (default: auto). Use "auto" for automatic detection, or specify language codes like eng, hin, mar, kan, etc.'
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
        ocr_tool = OCRExtractor(language=args.lang)
        
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
                print(f"Detected language: {extraction_result['detected_language']}", file=sys.stderr)
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
                "detectedLanguage": "unknown",
                "detectedLanguageName": "Unknown",
                "allDetectedLanguages": [],
                "pageLanguages": [],
                "inputLanguageMode": args.lang if hasattr(args, 'lang') else 'auto',
                "autoDetectionEnabled": True,
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
