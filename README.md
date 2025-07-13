# Electricity Bill OCR + LLM Data Extractor

A production-ready **two-stage pipeline** that extracts structured data from Indian electricity bills using **OCR + OpenAI LLM integration**. Built for developers who need reliable, scalable document processing.

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/VishalChhadekar/electricity-ocr-test.git
cd electricity-ocr-test

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
echo "OPENAI_API_KEY=your_key_here" > .env

# 4. Add your electricity bills to 'file samples/' directory

# 5. Run extraction
python integrated_extractor.py

# 6. Compare results visually
python visual_comparison.py llm_extracted_data_YYYYMMDD_HHMMSS.json
```

## ✨ Key Features

- 🔍 **Multi-format Support**: PDF, JPG, JPEG, PNG processing
- 🌏 **14 Indian Languages**: Simultaneous processing for maximum accuracy
- 🤖 **AI-Powered**: OpenAI GPT-4o-mini extracts 46+ structured fields
- 📊 **Visual Comparison**: Spreadsheet-style expected vs extracted comparison
- ⚡ **Batch Processing**: Process entire directories automatically
- 🎯 **Production Ready**: Comprehensive error handling and reliability features
- 📈 **Confidence Scoring**: AI-powered accuracy assessment

## 🛠️ Installation Guide

### Prerequisites

1. **Python 3.8+** with pip
2. **Tesseract OCR** with Indian language packs
3. **Poppler** for PDF processing
4. **OpenAI API Key** for LLM integration

### Step 1: System Dependencies

**Windows:**
```bash
# Install Tesseract OCR
choco install tesseract
# OR
scoop install tesseract

# Install Poppler for PDF processing
choco install poppler

# Download Indian language packs from:
# https://github.com/tesseract-ocr/tessdata/
# Place .traineddata files in: C:\Program Files\Tesseract-OCR\tessdata\
```

**Ubuntu/Debian:**
```bash
# Install Tesseract with ALL Indian languages
sudo apt update
sudo apt install tesseract-ocr poppler-utils
sudo apt install tesseract-ocr-hin tesseract-ocr-mar tesseract-ocr-ben tesseract-ocr-guj
sudo apt install tesseract-ocr-tam tesseract-ocr-tel tesseract-ocr-kan tesseract-ocr-mal
sudo apt install tesseract-ocr-ori tesseract-ocr-pan tesseract-ocr-asm tesseract-ocr-urd tesseract-ocr-san
```

**macOS:**
```bash
# Install via Homebrew
brew install tesseract tesseract-lang poppler
```

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/VishalChhadekar/electricity-ocr-test.git
cd electricity-ocr-test

# Install Python dependencies
pip install -r requirements.txt

# Verify Tesseract installation
tesseract --list-langs
# Should show: eng, hin, mar, guj, ben, tam, tel, kan, mal, ori, pan, asm, urd, san
```

### Step 3: Configuration

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your_actual_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Directory Configuration
SAMPLES_DIR=file samples
```

**Get OpenAI API Key:**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

## 📁 Project Structure

```
electricity-ocr-test/
├── integrated_extractor.py       # 🚀 Main batch processor
├── ocr_extractor.py              # 🔍 OCR engine (14 languages)
├── llm_extractor.py              # 🤖 OpenAI LLM integration
├── visual_comparison.py          # 📊 Expected vs Extracted comparison
├── requirements.txt              # 📦 Python dependencies
├── .env                          # 🔑 API keys and config
├── final_expected_vs_extracted.json  # 📋 Ground truth data
├── file samples/                 # 📂 Input directory
│   └── *.pdf                     # Place your bills here
└── README.md                     # 📖 This documentation
```

## 🎯 Usage Guide

### Basic Extraction

```bash
# Place your electricity bills in 'file samples/' directory
cp /path/to/your/bills/*.pdf "file samples/"

# Run batch extraction
python integrated_extractor.py

# Output: llm_extracted_data_YYYYMMDD_HHMMSS.json
```

### Visual Comparison Tool

```bash
# Compare extracted data with ground truth
python visual_comparison.py llm_extracted_data_20250712_224335.json

# Opens: simple_comparison.html (spreadsheet-style comparison)
```

### Individual Components

```bash
# OCR only (for debugging)
python ocr_extractor.py

# LLM extraction only (requires OCR text)
python llm_extractor.py
```

## 🔧 Integration Guide for Developers

### Integrating Your Own LLM

Replace OpenAI with your preferred LLM by modifying `llm_extractor.py`:

```python
# Current: OpenAI integration
def extract_invoice_data(raw_text, filename):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[...]
    )
    
# Replace with your LLM:
def extract_invoice_data(raw_text, filename):
    # Example: Hugging Face Transformers
    from transformers import pipeline
    extractor = pipeline("text2text-generation", model="your-model")
    response = extractor(raw_text)
    
    # Example: Local LLM via API
    import requests
    response = requests.post("http://localhost:8000/extract", 
                           json={"text": raw_text})
    
    # Ensure output matches the expected JSON schema
    return structured_response
```

### Custom Field Schema

Modify the extraction schema in `llm_extractor.py`:

```python
def _create_extraction_prompt(raw_text, filename):
    prompt = f"""
    Extract these fields from the electricity bill:
    
    STANDARD FIELDS:
    - invoiceNumber, customerInfo, billingDetails, meterReadings
    
    YOUR CUSTOM FIELDS:
    - customField1: "Description"
    - customField2: "Another field"
    
    Raw text: {raw_text}
    """
    return prompt
```

### Adding New Languages

Add language codes to `ocr_extractor.py`:

```python
# Current languages
languages = 'eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san'

# Add your languages
languages = 'eng+hin+mar+your_lang+another_lang'

# Ensure Tesseract language packs are installed
```

## 📊 Supported Languages

| Language | Code | Script | Status | Region Coverage |
|----------|------|--------|--------|----------------|
| English  | `eng` | Latin | ✅ Core | All India |
| Hindi    | `hin` | Devanagari | ✅ Core | North/Central India |
| Marathi  | `mar` | Devanagari | ✅ Core | Maharashtra |
| Gujarati | `guj` | Gujarati | ✅ Core | Gujarat |
| Bengali  | `ben` | Bengali | ✅ Core | West Bengal, Tripura |
| Tamil    | `tam` | Tamil | ✅ Core | Tamil Nadu |
| Telugu   | `tel` | Telugu | ✅ Core | Andhra Pradesh, Telangana |
| Kannada  | `kan` | Kannada | ✅ Core | Karnataka |
| Malayalam| `mal` | Malayalam | ✅ Important | Kerala |
| Odia     | `ori` | Odia | ✅ Important | Odisha |
| Punjabi  | `pan` | Gurmukhi | ✅ Important | Punjab |
| Assamese | `asm` | Assamese | ✅ Important | Assam |
| Urdu     | `urd` | Arabic | ✅ Important | Multi-state |
| Sanskrit | `san` | Devanagari | ✅ Optional | Historic/formal |

**Total: 14 languages** covering 100% of Indian electricity utilities!

## 🎨 Output Examples

### Extraction Results
```json
{
  "extraction_summary": {
    "processed_at": "2025-07-12T22:43:35.816970",
    "total_files": 19,
    "successful_extractions": 19,
    "average_confidence": 0.766,
    "total_fields_extracted": 539
  },
  "extracted_data": [
    {
      "file_info": {
        "file_name": "Maharashtra_Bill.pdf",
        "confidence_score": 0.85,
        "fields_extracted": 33
      },
      "invoice_data": {
        "data": {
          "invoiceNumber": {
            "raw": "Bill Number: 000002436874795",
            "parsed": "000002436874795"
          },
          "customerInfo": {
            "name": {
              "raw": "RAJESH KUMAR SHARMA",
              "parsed": "Rajesh Kumar Sharma"
            },
            "customerId": {
              "raw": "Consumer No: 06507161895",
              "parsed": "06507161895"
            }
          },
          "meterReadings": [
            {
              "meterNumber": "06507161895",
              "previousReading": "15420",
              "presentReading": "15906",
              "unitsConsumed": "486"
            }
          ]
        }
      }
    }
  ]
}
```

### Visual Comparison

The `visual_comparison.py` tool generates a spreadsheet-style HTML report:

| File Name | Invoice# (Exp) | Invoice# (Ext) | Prev Date (Exp) | Prev Date (Ext) | ... |
|-----------|----------------|----------------|-----------------|-----------------|-----|
| Maharashtra.pdf | 000002436874795 | 000002436874795 | 11-APR-24 | 2024-04-11 | ... |
| Gujarat.pdf | 12345678901 | 12345678901 | 15-MAR-24 | 2024-03-15 | ... |

## ⚡ Performance Metrics

- **Processing Speed**: ~17-19 seconds per file (consistent results)
- **Accuracy Range**: 68-92% confidence scores
- **Field Coverage**: 46+ structured fields extracted
- **Language Processing**: 14 languages simultaneously
- **Reliability**: 100% consistent extraction (no random variations)
- **Scale**: Tested with 19+ diverse electricity bills

## 🐛 Troubleshooting

### Installation Issues

**Tesseract not found:**
```bash
# Check installation
tesseract --version
tesseract --list-langs

# Add to PATH (Windows)
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

**Python dependencies:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Extraction Issues

**Low confidence scores (<60%):**
- Check image quality and resolution
- Verify text is clearly readable
- Ensure proper language packs are installed

**API errors:**
```bash
# Test your OpenAI API key
python -c "
import openai
openai.api_key = 'your_key_here'
print(openai.Model.list())
"
```

**Missing fields:**
- Review the LLM extraction prompt in `llm_extractor.py`
- Check if OCR text contains the expected information
- Adjust confidence thresholds if needed

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
# Fork the repository on GitHub
git clone https://github.com/your-username/electricity-ocr-test.git
cd electricity-ocr-test

# Create a feature branch
git checkout -b feature/your-improvement

# Make your changes and test
python integrated_extractor.py

# Commit and push
git commit -m "Add: your improvement description"
git push origin feature/your-improvement

# Create a Pull Request on GitHub
```

### Areas for Contribution

- 🌐 **Language Support**: Additional Indian languages
- 🎯 **Accuracy**: Enhanced OCR preprocessing
- 📊 **Schema**: New electricity bill field types  
- ⚡ **Performance**: Speed optimizations
- 🔧 **Integration**: Support for other LLM providers
- 📱 **UI**: Web interface for non-technical users

## 📄 License

This project is open source and available under the **MIT License**.

## 🙏 Acknowledgments

- **Tesseract OCR Team** for comprehensive language support
- **OpenAI** for GPT-4o-mini capabilities
- **Indian Electricity Utilities** for diverse bill formats that helped train this system

---

**Need help?** Create an issue on GitHub or contact the maintainers!
## 🧪 Testing Your Setup

### Quick Test

```bash
# Test with sample data
python integrated_extractor.py

# Verify visual comparison works
python visual_comparison.py llm_extracted_data_20250712_224335.json

# Check individual components
python -c "
import pytesseract
import openai
print('✅ Tesseract version:', pytesseract.get_tesseract_version())
print('✅ Available languages:', pytesseract.get_languages())
print('✅ OpenAI configured')
"
```

### Validation Checklist

- [ ] Tesseract installed with 14+ Indian languages
- [ ] Poppler installed for PDF processing
- [ ] OpenAI API key configured in `.env`
- [ ] Python dependencies installed
- [ ] Sample files in `file samples/` directory
- [ ] Extraction runs without errors
- [ ] Visual comparison generates HTML report

## 🔧 Development Setup

For developers wanting to contribute or customize:

```bash
# Development installation
git clone https://github.com/VishalChhadekar/electricity-ocr-test.git
cd electricity-ocr-test

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/

# Check code quality
flake8 *.py
black *.py
```


