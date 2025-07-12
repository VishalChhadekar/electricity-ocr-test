# Electricity Bill OCR + LLM Data Extractor

An intelligent two-stage pipeline that extracts structured data from electricity bills using OCR + OpenAI LLM integration.

## Features

- 🔍 **Multi-format Support**: Processes PDF, JPG, JPEG, and PNG files
- 🌏 **Language-Agnostic**: Automatic multi-language detection and processing
- 🤖 **AI-Powered Extraction**: OpenAI LLM extracts structured JSON from raw OCR text
- 📄 **PDF Processing**: Automatically converts PDF pages to images for OCR
- 🖼️ **Smart Preprocessing**: Enhances image quality for better text recognition
- 🎯 **Batch Processing**: Process entire directories of electricity bills automatically
- 📊 **Confidence Scoring**: AI-powered accuracy assessment with detailed metrics
- � **Structured Output**: Comprehensive JSON schema with raw/parsed value pairs

## Supported Languages

The system automatically detects and processes multiple Indian languages simultaneously for comprehensive electricity bill coverage:

| Language | Code | Script | Priority | Status |
|----------|------|--------|----------|--------|
| English  | `eng` | Latin | ⭐ Must-have | ✅ Installed |
| Hindi    | `hin` | Devanagari | ⭐ Must-have | ✅ Installed |
| Marathi  | `mar` | Devanagari | ⭐ Must-have | ✅ Installed |
| Gujarati | `guj` | Gujarati | ⭐ Must-have | ✅ Installed |
| Bengali  | `ben` | Bengali | ⭐ Must-have | ✅ Installed |
| Tamil    | `tam` | Tamil | ⭐ Must-have | ✅ Installed |
| Telugu   | `tel` | Telugu | ⭐ Must-have | ✅ Installed |
| Kannada  | `kan` | Kannada | ⭐ Must-have | ✅ Installed |
| Malayalam| `mal` | Malayalam | 🔥 Important | ✅ Installed |
| Odia     | `ori` | Odia | 🔥 Important | ✅ Installed |
| Punjabi  | `pan` | Gurmukhi | 🔥 Important | ✅ Installed |
| Assamese | `asm` | Assamese | 🔥 Important | ✅ Installed |
| Urdu     | `urd` | Arabic | 🔥 Important | ✅ Installed |
| Sanskrit | `san` | Devanagari | 📚 Optional | ✅ Installed |
| Konkani  | `kok` | Devanagari | 📚 Rare | ❌ Not available |

**Total: 14 languages** - Comprehensive coverage for Indian electricity utilities!

**Note**: The system processes all available languages in a single pass for maximum accuracy. No language selection needed - it's fully automatic!

## Prerequisites

### System Requirements

1. **Tesseract OCR**: Required for text extraction from images:

   **Windows:**
   ```bash
   # Install Tesseract with comprehensive language support
   choco install tesseract
   # OR for more language options
   scoop install tesseract
   
   # For additional Indian languages, download language packs from:
   # https://github.com/tesseract-ocr/tessdata/
   # Place .traineddata files in: C:\Program Files\Tesseract-OCR\tessdata\
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install tesseract-ocr
   # Install ALL Indian language packs for complete coverage
   sudo apt install tesseract-ocr-hin tesseract-ocr-mar tesseract-ocr-kan tesseract-ocr-ben
   sudo apt install tesseract-ocr-guj tesseract-ocr-tam tesseract-ocr-tel tesseract-ocr-mal
   sudo apt install tesseract-ocr-ori tesseract-ocr-pan tesseract-ocr-asm tesseract-ocr-urd
   sudo apt install tesseract-ocr-san tesseract-ocr-kok
   ```

   **macOS:**
   ```bash
   # Install Tesseract with comprehensive language support
   brew install tesseract tesseract-lang
   # This should include most Indian languages automatically
   ```

2. **Poppler**: Required for PDF processing:

   **Windows:**
   ```bash
   # Usually included with Tesseract installation
   choco install poppler
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt install poppler-utils
   ```

   **macOS:**
   ```bash
   brew install poppler
   ```

3. **OpenAI API Key**: Required for intelligent data extraction
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a `.env` file in the project root with your key

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure OpenAI API:**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   SAMPLES_DIR=file samples
   ```

### Expanding Language Support

To install additional Indian language packs on your current system:

**Windows (Manual Installation):**
1. Download `.traineddata` files from [Tesseract Language Data](https://github.com/tesseract-ocr/tessdata/)
2. Copy files to: `C:\Program Files\Tesseract-OCR\tessdata\` or your Tesseract installation directory
3. Required files for complete Indian coverage:
   ```
   ben.traineddata  (Bengali)
   guj.traineddata  (Gujarati) 
   tam.traineddata  (Tamil)
   tel.traineddata  (Telugu)
   mal.traineddata  (Malayalam)
   ori.traineddata  (Odia)
   pan.traineddata  (Punjabi)
   asm.traineddata  (Assamese)
   urd.traineddata  (Urdu)
   san.traineddata  (Sanskrit)
   kok.traineddata  (Konkani)
   ```

**Linux (Package Manager):**
```bash
# Install remaining language packs
sudo apt install tesseract-ocr-ben tesseract-ocr-guj tesseract-ocr-tam tesseract-ocr-tel
sudo apt install tesseract-ocr-mal tesseract-ocr-ori tesseract-ocr-pan tesseract-ocr-asm
sudo apt install tesseract-ocr-urd tesseract-ocr-san
# Note: tesseract-ocr-kok may not be available in all repositories
```

**Verify Installation:**
```bash
tesseract --list-langs
```

## Usage

### Batch Processing (Recommended)

Process all electricity bills in the samples directory:

```bash
python integrated_extractor.py
```

This will:
- Automatically process all files in `file samples/` directory
- Extract text using OCR from each document
- Use OpenAI to extract structured data with 46+ fields
- Generate timestamped JSON output with detailed results
- Show confidence scores and field extraction counts

### Output Structure

The system generates comprehensive JSON output with:

```json
{
  "extraction_summary": {
    "total_files": 5,
    "successful_extractions": 4,
    "average_confidence": 0.82
  },
  "extracted_data": [
    {
      "file_info": {
        "file_name": "electricity_bill.pdf",
        "confidence_score": 0.85,
        "fields_extracted": 38
      },
      "invoice_data": {
        "data": {
          "invoiceNumber": {
            "raw": "Bill No: 123456789",
            "parsed": "123456789"
          },
          "customerInfo": {
            "name": {
              "raw": "RAJESH KUMAR",
              "parsed": "Rajesh Kumar"
            }
          },
          "billingDetails": {
            "totalAmount": {
              "raw": "₹1,234.56",
              "parsed": "1234.56"
            }
          }
        }
      }
    }
  ]
}
```

## System Architecture

This is a **two-stage intelligent pipeline**:

1. **OCR Stage** (`ocr_extractor.py`): 
   - Fast, language-agnostic text extraction using Tesseract
   - Comprehensive multi-language processing (14 Indian languages simultaneously)
   - Smart image preprocessing for optimal text recognition

2. **LLM Stage** (`llm_extractor.py`):
   - OpenAI GPT-4o-mini extracts structured data from raw text
   - 46+ field extraction with raw/parsed value pairs
   - Confidence scoring and accuracy assessment

3. **Integration** (`integrated_extractor.py`):
   - Batch processing of entire directories
   - Comprehensive error handling and fallback strategies
   - Detailed reporting with extraction statistics

## File Structure

```
electricity-ocr-test/
├── integrated_extractor.py    # Main batch processor (OCR + LLM)
├── ocr_extractor.py           # OCR text extraction engine
├── llm_extractor.py           # OpenAI LLM data extraction
├── requirements.txt           # Python dependencies
├── .env                       # API keys and configuration
├── README.md                  # This file
└── file samples/              # Input directory for electricity bills
    └── *.pdf                  # Place your PDF files here
```

## How It Works

### OCR Stage:
1. **File Validation**: Checks supported formats (PDF, JPG, JPEG, PNG)
2. **PDF Conversion**: Converts PDF pages to high-resolution images (300 DPI)
3. **Image Preprocessing**: Enhances contrast, sharpness, and reduces noise
4. **Multi-language OCR**: Processes with **14 Indian languages** simultaneously (`eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san`)
5. **Fallback Strategy**: Falls back to English-only if multi-language fails

### LLM Stage:
1. **Text Analysis**: OpenAI analyzes raw OCR text
2. **Structured Extraction**: Extracts 46+ fields including:
   - Invoice numbers and dates
   - Customer information (name, ID, address, mobile)
   - Billing details (amount, due date, period)
   - Meter readings (multiple meters supported)
   - Utility company information
3. **Data Validation**: Raw/parsed value pairs with confidence scoring
4. **Quality Assessment**: Accuracy metrics and completion rates

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**:
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - Check API key has sufficient credits

2. **"Tesseract not found"**:
   - Ensure Tesseract is installed and added to system PATH
   - Install additional language packs for better accuracy

3. **Poor extraction accuracy (low confidence scores)**:
   - Check image quality - ensure high resolution and good contrast
   - Verify text is clearly readable in the original document
   - Low confidence (<60%) often indicates poor OCR input quality

4. **"Language pack missing" warnings**:
   - Install additional Tesseract language packs for better accuracy
   - System will continue with available languages but may miss text

5. **PDF processing issues**:
   - Ensure Poppler is properly installed
   - Check that PDF files are not password-protected or corrupted

## Dependencies

- **Core OCR**: `pytesseract`, `pdf2image`, `Pillow`
- **LLM Integration**: `openai` (GPT-4o-mini)
- **Configuration**: `python-dotenv`
- **System Requirements**: Tesseract OCR, Poppler utilities

## Performance Metrics

- **Processing Speed**: ~3.5 minutes for 21 files
- **Accuracy Range**: 68-92% confidence scores in production
- **Language Support**: 14 Indian languages simultaneous processing
- **Field Extraction**: 46+ structured fields per document
- **Geographic Coverage**: Complete support for all Indian state electricity boards

## Contributing

Contributions welcome! Areas for improvement:
- **Language Expansion**: Adding more Indian languages
- **OCR Accuracy**: Enhanced preprocessing algorithms  
- **Schema Extension**: Additional electricity bill field types
- **Performance**: Optimization for large batch processing
- **Error Handling**: Enhanced validation and recovery strategies

## License

This project is open source and available under the MIT License.
