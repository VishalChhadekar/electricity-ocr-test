#!/usr/bin/env python3
"""
OCR Text Extractor for Electricity Bills
Supports multiple Indian languages and various file formats (PDF, JPG, PNG)
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional
import logging

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"Error: Required package not installed. {e}")
    print("Please install requirements using: pip install -r requirements.txt")
    sys.exit(1)


class ElectricityBillOCR:
    """OCR tool for extracting text from electricity bills in multiple Indian languages."""
    
    # Supported languages mapping
    SUPPORTED_LANGUAGES = {
        'eng': 'English',
        'hin': 'Hindi', 
        'mar': 'Marathi',
        'kan': 'Kannada'
    }
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
    
    def __init__(self, language: str = 'eng'):
        """
        Initialize the OCR tool.
        
        Args:
            language (str): Language code for OCR (default: 'eng')
        """
        self.language = language
        self.setup_logging()
        self.validate_language()
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_language(self):
        """Validate if the specified language is supported."""
        if self.language not in self.SUPPORTED_LANGUAGES:
            available_langs = ', '.join(self.SUPPORTED_LANGUAGES.keys())
            raise ValueError(
                f"Unsupported language: {self.language}. "
                f"Available languages: {available_langs}"
            )
        
        self.logger.info(f"Using language: {self.SUPPORTED_LANGUAGES[self.language]} ({self.language})")
    
    def validate_file(self, file_path: str) -> Path:
        """
        Validate if the file exists and has a supported extension.
        
        Args:
            file_path (str): Path to the input file
            
        Returns:
            Path: Validated file path
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file extension is not supported
        """
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
        """
        Preprocess image to improve OCR accuracy.
        
        Args:
            image (Image.Image): Input image
            
        Returns:
            Image.Image: Preprocessed image
        """
        self.logger.info("Preprocessing image for better OCR accuracy...")
        
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
        """
        Convert PDF pages to images.
        
        Args:
            pdf_path (Path): Path to PDF file
            
        Returns:
            List[Image.Image]: List of images for each page
        """
        self.logger.info(f"Converting PDF to images: {pdf_path}")
        
        try:
            # Convert PDF to images with high DPI for better OCR
            images = convert_from_path(
                str(pdf_path),
                dpi=300,  # High DPI for better text recognition
                fmt='PNG'
            )
            self.logger.info(f"Successfully converted {len(images)} pages from PDF")
            return images
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF to images: {e}")
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from a single image using Tesseract OCR.
        
        Args:
            image (Image.Image): Input image
            
        Returns:
            str: Extracted text
        """
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config=custom_config
            )
            
            return text.strip()
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}")
    
    def process_file(self, file_path: str) -> str:
        """
        Process a file and extract text using OCR.
        
        Args:
            file_path (str): Path to the input file
            
        Returns:
            str: Extracted text from all pages/images
        """
        path = self.validate_file(file_path)
        self.logger.info(f"Processing file: {path}")
        
        all_text = []
        
        if path.suffix.lower() == '.pdf':
            # Handle PDF files
            images = self.pdf_to_images(path)
            
            for i, image in enumerate(images, 1):
                self.logger.info(f"Processing page {i}/{len(images)}")
                text = self.extract_text_from_image(image)
                if text:
                    all_text.append(f"=== Page {i} ===\n{text}")
        else:
            # Handle image files
            try:
                image = Image.open(path)
                text = self.extract_text_from_image(image)
                if text:
                    all_text.append(text)
            except Exception as e:
                raise RuntimeError(f"Failed to open image file: {e}")
        
        if not all_text:
            self.logger.warning("No text was extracted from the file")
            return ""
        
        final_text = "\n\n".join(all_text)
        self.logger.info(f"Successfully extracted {len(final_text)} characters of text")
        
        return final_text


def main():
    """Main function to handle command line arguments and run OCR."""
    parser = argparse.ArgumentParser(
        description="OCR Text Extractor for Electricity Bills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar
  python ocr_extractor.py --file image.jpg --lang eng
  python ocr_extractor.py --file bill.png --lang hin
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        required=True,
        help='Path to the input file (PDF, JPG, JPEG, PNG)'
    )
    
    parser.add_argument(
        '--lang', '-l',
        default='eng',
        choices=['eng', 'hin', 'mar', 'kan'],
        help='Language code for OCR (default: eng)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path to save extracted text (optional)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize OCR tool
        ocr_tool = ElectricityBillOCR(language=args.lang)
        
        # Process the file
        extracted_text = ocr_tool.process_file(args.file)
        
        # Output results
        if extracted_text:
            print("\n" + "="*60)
            print("EXTRACTED TEXT:")
            print("="*60)
            print(extracted_text)
            print("="*60)
            
            # Save to output file if specified
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(extracted_text, encoding='utf-8')
                print(f"\nText saved to: {output_path}")
        else:
            print("No text could be extracted from the file.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
