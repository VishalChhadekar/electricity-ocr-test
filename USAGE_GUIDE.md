# OCR Usage Guide

This guide shows how to use both the basic OCR extractor and the structured JSON OCR extractor for electricity bills.

## 🛠️ Available Tools

### 1. Basic OCR Extractor (`ocr_extractor.py`)
Extracts plain text from electricity bills with basic output formatting.

### 2. Structured JSON OCR Extractor (`structured_ocr_extractor.py`)
Extracts text and provides structured JSON output with field detection, confidence scores, and metadata - compatible with professional document processing systems.

## 📋 Basic Usage Examples

### Basic Text Extraction
```bash
# Extract text from Marathi PDF
python ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar

# Extract text from English image
python ocr_extractor.py --file electricity_bill.jpg --lang eng

# Save output to file
python ocr_extractor.py --file bill.pdf --lang hin --output extracted_text.txt
```

### Structured JSON Extraction
```bash
# Extract structured data with pretty JSON
python structured_ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar --pretty

# Save structured data to JSON file
python structured_ocr_extractor.py --file bill.pdf --lang eng --output result.json --pretty

# Compact JSON output
python structured_ocr_extractor.py --file bill.jpg --lang hin
```

## 🎯 Extracted Fields (Structured OCR)

The structured OCR extractor automatically detects and extracts:

### Core Bill Information
- **Customer Number** (`customerNumber`) - ग्राहक क्रमांक
- **Bill Number** (`billNumber`) - देयक संख्या
- **Meter Number** (`meterNumber`) - मीटर संख्या
- **Bill Date** (`billDate`) - देयक दिनांक
- **Due Date** (`dueDate`) - देय दिनांक
- **Total Amount** (`totalAmount`) - कुल रक्कम

### Meter Reading Information
- **Current Reading** (`currentReading`) - वर्तमान रीडिंग
- **Previous Reading** (`previousReading`) - मागील रीडिंग
- **Units Consumed** (`unitsConsumed`) - युनिट वापर
- **Meter Readings Array** (`meterReadings`) - Complex meter data with nested fields

### Additional Data
- **Raw Text** (`rawText`) - Complete extracted text from all pages
- **Metadata** - Document processing information, page details, confidence scores

## 📊 JSON Output Structure

```json
{
  "data": {
    "customerNumber": {
      "id": 203576112,
      "rectangle": { "x0": 100.0, "y0": 100.0, "x1": 200.0, "y1": 120.0, "pageIndex": 0 },
      "raw": "036012426687",
      "parsed": "036012426687",
      "confidence": 0.85,
      "contentType": "text"
    },
    "dueDate": {
      "id": 2182008558,
      "raw": "14-06-2024",
      "parsed": "2024-06-14",
      "confidence": 0.85,
      "contentType": "date"
    },
    "rawText": "=== Page 1 ===\n[Full OCR text...]"
  },
  "meta": {
    "identifier": "BEEBEDJI",
    "fileName": "Maharastra.pdf",
    "language": "mar",
    "pages": [...]
  },
  "error": { "errorCode": null, "errorDetail": null }
}
```

## 🌐 Supported Languages

| Code | Language | Script |
|------|----------|--------|
| `eng` | English | Latin |
| `hin` | Hindi | Devanagari |
| `mar` | Marathi | Devanagari |
| `kan` | Kannada | Kannada |

## 📁 Supported File Formats

- **PDF** (`.pdf`) - Multi-page support
- **JPEG** (`.jpg`, `.jpeg`) 
- **PNG** (`.png`)

## ⚙️ Command Line Options

### Basic OCR Extractor
```bash
python ocr_extractor.py [options]

Options:
  --file, -f     Input file path (required)
  --lang, -l     Language code [eng|hin|mar|kan] (default: eng)
  --output, -o   Output text file (optional)
  --verbose, -v  Enable verbose logging
```

### Structured OCR Extractor
```bash
python structured_ocr_extractor.py [options]

Options:
  --file, -f     Input file path (required)
  --lang, -l     Language code [eng|hin|mar|kan] (default: eng)
  --output, -o   Output JSON file (optional)
  --pretty, -p   Pretty print JSON output
  --verbose, -v  Enable verbose logging
```

## 🔍 Processing Examples

### Example 1: Maharashtra Bill Processing
```bash
# Basic text extraction
python ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar --output maharashtra_text.txt

# Structured JSON extraction
python structured_ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar --output maharashtra_data.json --pretty
```

### Example 2: Hindi Bill Processing
```bash
# Extract and display structured data
python structured_ocr_extractor.py --file hindi_bill.pdf --lang hin --pretty

# Save to specific output file
python structured_ocr_extractor.py --file hindi_bill.pdf --lang hin --output hindi_bill_data.json
```

### Example 3: English Bill Processing
```bash
# Quick extraction with verbose logging
python structured_ocr_extractor.py --file english_bill.jpg --lang eng --verbose --pretty
```

## 🎨 Integration Examples

### Python Integration
```python
import json
import subprocess

# Run structured OCR extraction
result = subprocess.run([
    'python', 'structured_ocr_extractor.py', 
    '--file', 'bill.pdf', 
    '--lang', 'mar', 
    '--output', 'result.json'
], capture_output=True, text=True)

# Load extracted data
with open('result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Access extracted fields
customer_number = data['data'].get('customerNumber', {}).get('parsed')
due_date = data['data'].get('dueDate', {}).get('parsed')
total_amount = data['data'].get('totalAmount', {}).get('parsed')

print(f"Customer: {customer_number}")
print(f"Due Date: {due_date}")
print(f"Amount: {total_amount}")
```

### JavaScript/Node.js Integration
```javascript
const { exec } = require('child_process');
const fs = require('fs');

// Run OCR extraction
exec('python structured_ocr_extractor.py --file bill.pdf --lang mar --output result.json', 
     (error, stdout, stderr) => {
    if (error) {
        console.error('OCR Error:', error);
        return;
    }
    
    // Read extracted data
    const data = JSON.parse(fs.readFileSync('result.json', 'utf8'));
    
    console.log('Extracted Fields:');
    console.log('Customer Number:', data.data.customerNumber?.parsed);
    console.log('Due Date:', data.data.dueDate?.parsed);
    console.log('Amount:', data.data.totalAmount?.parsed);
});
```

## 🛠️ Troubleshooting

### Common Issues

1. **Language pack not found**
   ```bash
   # Run installation test
   python test_installation.py
   ```

2. **PDF processing fails**
   - Ensure Poppler is installed: `scoop install poppler`
   - Check PDF is not password protected

3. **Low accuracy results**
   - Try different language codes
   - Ensure image quality is good (300+ DPI)
   - Check if bill is rotated or skewed

### Validation Commands
```bash
# Test all dependencies
python test_installation.py

# Test with sample file
python structured_ocr_extractor.py --file "file samples/Maharastra.pdf" --lang mar --verbose
```

## 📈 Performance Tips

1. **Image Quality**: Use high-resolution scans (300+ DPI)
2. **Language Selection**: Choose the correct language for best accuracy
3. **File Format**: PDF files generally provide better results than images
4. **Preprocessing**: The tool automatically enhances images for better OCR accuracy

## 🔒 Data Privacy

- All processing is done locally on your machine
- No data is sent to external services
- Output files are saved locally as specified

## 📞 Support

For technical issues or questions:
1. Check the installation guide: `README.md`
2. Run the test script: `python test_installation.py`
3. Review error messages in verbose mode: `--verbose`
