# 🔌 Electricity Bill OCR + LLM Data Extractor

A powerful, integrated system that combines **fast OCR text extraction** with **intelligent LLM-based data extraction** to convert electricity bills into structured JSON data.

## 🌟 Features

- **Fast OCR Processing**: Multi-language text extraction using Tesseract
- **Intelligent Data Extraction**: OpenAI-powered structured data extraction
- **Batch Processing**: Process multiple files efficiently
- **Multiple Formats**: Support for PDF, JPG, PNG files
- **Structured Output**: Clean JSON schema with all bill details
- **High Accuracy**: Confidence scoring and validation
- **Error Handling**: Robust error handling and fallbacks

## 🏗️ System Architecture

```
📄 Invoice File → 🔍 OCR (Tesseract) → 📝 Raw Text → 🤖 LLM (OpenAI) → 📊 Structured JSON
```

### Two-Stage Pipeline:
1. **OCR Stage**: Fast, language-agnostic text extraction
2. **LLM Stage**: Intelligent parsing and structured data extraction

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd electricity-ocr-test
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   - **Windows**: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

4. **Set up OpenAI API**
   - Get API key from [OpenAI Platform](https://platform.openai.com/)
   - Set environment variable: `export OPENAI_API_KEY=your_api_key_here`

## 🚀 Usage

### Quick Test (Single File)
```bash
python test_llm_integration.py
```

### Batch Processing (All Files)
```bash
python integrated_extractor.py --api-key YOUR_API_KEY
```

### Environment Variable Setup
```bash
# Set API key as environment variable
export OPENAI_API_KEY=your_api_key_here

# Then run without --api-key parameter
python integrated_extractor.py
```

### Custom Options
```bash
python integrated_extractor.py \
    --api-key YOUR_API_KEY \
    --samples-dir "path/to/your/files" \
    --model "gpt-4"
```

## 📊 Output Formats

### 1. Detailed JSON (`llm_extracted_data_TIMESTAMP.json`)
Complete structured data with metadata:
```json
{
  "extraction_summary": {
    "processed_at": "2025-07-11T18:30:00",
    "total_files": 21,
    "successful_extractions": 20,
    "average_confidence": 0.87
  },
  "extracted_data": [
    {
      "file_info": {
        "file_name": "maharashtra_bill.pdf",
        "confidence_score": 0.92
      },
      "invoice_data": {
        "bill_info": {
          "bill_number": "000002436874795",
          "bill_date": "2024-05-16",
          "due_date": "2024-06-05"
        },
        "customer_info": {
          "customer_name": "ALAKA DILIP JAIN",
          "customer_id": "036012426687"
        },
        "billing_details": {
          "total_amount": 6700.00,
          "units_consumed": 86
        }
      }
    }
  ]
}
```

### 2. Summary CSV (`llm_extraction_summary_TIMESTAMP.csv`)
Quick overview for analysis:
```csv
Sr_No,File_Name,Status,Fields_Extracted,Confidence_Score,Bill_Number,Customer_Name,Total_Amount
1,maharashtra_bill.pdf,success,12,0.92,000002436874795,ALAKA DILIP JAIN,6700.00
```

## 📋 Extracted Data Schema

```json
{
  "bill_info": {
    "bill_number": "string",
    "bill_date": "YYYY-MM-DD", 
    "due_date": "YYYY-MM-DD",
    "billing_period": "string"
  },
  "customer_info": {
    "customer_name": "string",
    "customer_id": "string",
    "address": "string",
    "mobile": "string",
    "email": "string"
  },
  "billing_details": {
    "total_amount": "number",
    "current_reading": "number",
    "previous_reading": "number", 
    "units_consumed": "number",
    "rate_per_unit": "number"
  },
  "utility_info": {
    "company_name": "string",
    "state": "string",
    "service_type": "electricity",
    "meter_number": "string"
  },
  "additional_charges": {
    "fixed_charges": "number",
    "energy_charges": "number",
    "taxes": "number",
    "other_charges": "number"
  },
  "confidence_score": "0.0-1.0",
  "extracted_fields_count": "number"
}
```

## 🔧 Configuration

### Supported File Types
- PDF files (`.pdf`)
- Image files (`.jpg`, `.jpeg`, `.png`)

### Language Support
Automatic support for major Indian languages:
- English, Hindi, Marathi, Kannada
- Bengali, Gujarati, Tamil, Telugu

### OpenAI Models
- `gpt-4o-mini` (default - fast and cost-effective)
- `gpt-4o` (higher accuracy)
- `gpt-4` (most accurate)

## 🎯 Performance

### Benchmarks (21 test files)
- **OCR Processing**: ~3.5 minutes
- **LLM Processing**: ~2-4 minutes (depending on model)
- **Total Pipeline**: ~6-8 minutes
- **Success Rate**: 95%+ 
- **Average Confidence**: 0.85+

### Cost Estimation
Using `gpt-4o-mini`:
- ~$0.02-0.05 per bill
- ~$1-2 per 100 bills

## 📁 Project Structure

```
electricity-ocr-test/
├── ocr_extractor.py           # OCR text extraction
├── llm_extractor.py           # LLM data extraction  
├── integrated_extractor.py    # Main integrated system
├── batch_ocr_results.py       # Simple OCR batch processing
├── test_llm_integration.py    # Test single file
├── requirements.txt           # Dependencies
├── file samples/              # Input files
└── outputs/                   # Generated results
```

## 🚨 Troubleshooting

### Common Issues

1. **"Import openai could not be resolved"**
   ```bash
   pip install openai
   ```

2. **"Tesseract not found"**
   - Install Tesseract and add to PATH
   - Verify: `tesseract --version`

3. **"OpenAI API key not provided"**
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

4. **Low confidence scores**
   - Check image quality
   - Try different OpenAI model
   - Verify OCR text quality

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

- [ ] Support for more utilities (gas, water)
- [ ] Custom field extraction templates
- [ ] Local LLM integration (Ollama)
- [ ] Real-time processing API
- [ ] Web interface
- [ ] Database integration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Open GitHub issue
3. Provide sample files and logs
