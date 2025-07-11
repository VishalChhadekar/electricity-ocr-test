# Electricity Bill OCR Text Extractor

A Python-based OCR tool that extracts text from electricity bills in various formats and multiple Indian languages using Tesseract.

## Features

- 🔍 **Multi-format Support**: Processes PDF, JPG, JPEG, and PNG files
- 🌏 **Multi-language Support**: English, Hindi, Marathi, and Kannada
- 📄 **PDF Processing**: Automatically converts PDF pages to images for OCR
- 🖼️ **Image Preprocessing**: Enhances image quality for better text recognition
- 💻 **CLI Interface**: Easy-to-use command-line interface
- 📝 **Text Output**: Displays extracted text and optionally saves to file

## Supported Languages

| Language | Code | Script |
|----------|------|--------|
| English  | `eng` | Latin |
| Hindi    | `hin` | Devanagari |
| Marathi  | `mar` | Devanagari |
| Kannada  | `kan` | Kannada |

## Prerequisites

### System Requirements

1. **Tesseract OCR**: You need to install Tesseract OCR on your system:

   **Windows:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH
   - Download language packs for Indian languages

   **macOS:**
   ```bash
   brew install tesseract
   brew install tesseract-lang  # For additional languages
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install tesseract-ocr
   sudo apt install tesseract-ocr-hin tesseract-ocr-mar tesseract-ocr-kan
   ```

2. **Poppler** (for PDF processing):

   **Windows:**
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract and add to PATH

   **macOS:**
   ```bash
   brew install poppler
   ```

   **Linux:**
   ```bash
   sudo apt install poppler-utils
   ```

## Installation

1. **Clone or download this project**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python ocr_extractor.py --file "path/to/your/file" --lang <language_code>
```

### Examples

1. **Extract text from a Marathi PDF:**
   ```bash
   python ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar
   ```

2. **Extract text from an English image:**
   ```bash
   python ocr_extractor.py --file "bill.jpg" --lang eng
   ```

3. **Extract text from Hindi PDF and save to file:**
   ```bash
   python ocr_extractor.py --file "hindi_bill.pdf" --lang hin --output extracted_text.txt
   ```

4. **Extract with verbose logging:**
   ```bash
   python ocr_extractor.py --file "bill.png" --lang kan --verbose
   ```

### Batch Processing

For processing multiple files at once, use the batch processor:

```bash
python batch_ocr.py --input "bills_folder/" --output "extracted_texts/" --lang mar
```

This will process all supported files in the input directory and save extracted text files in the output directory.

### Command Line Options

- `--file, -f`: Path to input file (required)
- `--lang, -l`: Language code (default: `eng`)
- `--output, -o`: Output file path to save extracted text (optional)
- `--verbose, -v`: Enable verbose logging
- `--help, -h`: Show help message

## File Structure

```
electricity-ocr-test/
├── ocr_extractor.py       # Main OCR script
├── batch_ocr.py          # Batch processing script
├── test_installation.py  # Installation test script
├── examples.py           # Usage examples
├── setup.bat            # Windows setup script
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── file samples/         # Sample files
    └── Maharastra.pdf    # Sample Marathi electricity bill
```

## How It Works

1. **File Validation**: Checks if the input file exists and has a supported extension
2. **PDF Conversion**: Converts PDF pages to high-resolution images (300 DPI)
3. **Image Preprocessing**: 
   - Converts to grayscale
   - Enhances contrast and sharpness
   - Applies gaussian blur to reduce noise
4. **OCR Processing**: Uses Tesseract with language-specific models
5. **Text Extraction**: Extracts and formats text from all pages/images
6. **Output**: Displays text on console and optionally saves to file

## Troubleshooting

### Common Issues

1. **"Tesseract not found"**:
   - Ensure Tesseract is installed and added to your system PATH
   - On Windows, you might need to set the tesseract path manually

2. **"Language not supported"**:
   - Install the required Tesseract language packs
   - Verify language codes are correct (`eng`, `hin`, `mar`, `kan`)

3. **Poor OCR quality**:
   - Ensure input images are high quality and well-lit
   - Try different preprocessing options
   - Check if the language setting matches the document

4. **PDF conversion fails**:
   - Install Poppler utilities
   - Ensure PDF is not password-protected or corrupted

### Tips for Better Results

- Use high-resolution images (300 DPI or higher)
- Ensure good contrast between text and background
- Avoid skewed or rotated documents
- Use the correct language setting for your document
- For multi-language documents, you can try combining language codes (e.g., `eng+hin`)

## Dependencies

- `pytesseract`: Python wrapper for Tesseract OCR
- `pdf2image`: Convert PDF pages to images
- `Pillow`: Image processing library
- `argparse`: Command-line argument parsing (built-in)

## Contributing

Feel free to contribute by:
- Adding support for more Indian languages
- Improving image preprocessing algorithms
- Adding more output formats
- Enhancing error handling

## License

This project is open source and available under the MIT License.
