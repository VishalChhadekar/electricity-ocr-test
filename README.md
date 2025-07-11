# Electricity Bill OCR Text Extractor

A simple Python-based OCR tool that extracts raw text from electricity bills using Tesseract OCR.

## Features

- 🔍 **Multi-format Support**: Processes PDF, JPG, JPEG, and PNG files
- 🌏 **Multi-language Support**: English, Hindi, Marathi, and Kannada  
- 📄 **PDF Processing**: Automatically converts PDF pages to images for OCR
- 🖼️ **Image Preprocessing**: Enhances image quality for better text recognition
- 💻 **CLI Interface**: Easy-to-use command-line interface
- � **JSON Output**: Structured JSON output with metadata
- 📝 **Text Output**: Raw text extraction option

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

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-mar tesseract-ocr-kan
   ```

   **Linux (CentOS/RHEL):**
   ```bash
   sudo yum install tesseract tesseract-langpack-hin tesseract-langpack-mar tesseract-langpack-kan
   ```

   **macOS:**
   ```bash
   brew install tesseract tesseract-lang
   ```

2. **Poppler**: For PDF processing:

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt install poppler-utils
   ```

   **Linux (CentOS/RHEL):**
   ```bash
   sudo yum install poppler-utils
   ```

   **macOS:**
   ```bash
   brew install poppler
   ```
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

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Arguments

```bash
python ocr_extractor.py --file <path> [options]
```

**Required Arguments:**
- `--file`, `-f`: Path to the input file (PDF, JPG, JPEG, PNG)

**Optional Arguments:**
- `--lang`, `-l`: Language code for OCR (default: eng)
  - Choices: `eng`, `hin`, `mar`, `kan`
- `--output`, `-o`: Output file path to save results
- `--verbose`, `-v`: Enable verbose logging
- `--pretty`, `-p`: Pretty print JSON output  
- `--text-only`: Output only raw text without JSON formatting

### Examples

1. **Extract text from a Marathi PDF (JSON output):**
   ```bash
   python ocr_extractor.py --file "bill.pdf" --lang mar --pretty
   ```

2. **Extract raw text only from an English image:**
   ```bash
   python ocr_extractor.py --file "bill.jpg" --lang eng --text-only
   ```

3. **Save results to file:**
   ```bash
   python ocr_extractor.py --file "bill.pdf" --lang mar --output results.json --pretty
   ```

4. **Verbose processing with English:**
   ```bash
   python ocr_extractor.py --file "bill.pdf" --lang eng --verbose --pretty
   ```

### Output Formats

**JSON Output (default):**
```json
{
  "data": {
    "rawText": "Extracted text content here...",
    "textLength": 1234,
    "extractedAt": "2025-07-11T15:30:00.000000",
    "language": "eng",
    "languageName": "English",
    "fileName": "bill.pdf",
    "fileExtension": ".pdf",
    "ocrEngine": "tesseract",
    "extractionId": "unique-uuid-here"
  },
  "error": {
    "errorCode": null,
    "errorDetail": null
  },
  "status": "success"
}
```

**Text-only Output:**
```
Raw extracted text from the document...
```

## Testing Installation

Test your installation:

```bash
python test_installation.py
```

This will verify that all dependencies are correctly installed and working.

## File Structure

```
electricity-ocr-test/
├── ocr_extractor.py        # Main OCR script
├── test_installation.py   # Installation test script
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── file samples/           # Sample files
    ├── Maharastra.pdf      # Sample Marathi electricity bill
    └── Multiple-Meters.pdf # Sample English electricity bill
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
6. **Output**: Returns structured JSON or raw text

## Troubleshooting

### Common Issues

1. **"Tesseract not found"**:
   - Ensure Tesseract is installed and added to your system PATH
   - Install language-specific packs as needed

2. **"Language not supported"**:
   - Install the required Tesseract language packs
   - Verify language codes are correct (`eng`, `hin`, `mar`, `kan`)

3. **Poor OCR quality**:
   - Ensure input images are high quality and well-lit
   - Try different preprocessing settings for specific document types

4. **PDF processing issues**:
   - Ensure Poppler is properly installed
   - Check that PDF files are not password-protected or corrupted

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
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
