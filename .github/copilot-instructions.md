# Electricity Bill OCR + LLM Extractor - AI Agent Instructions

## Architecture Overview

This is a **two-stage pipeline** for extracting structured data from electricity bills:
1. **OCR Stage**: `ocr_extractor.py` - Fast, language-agnostic text extraction using Tesseract
2. **LLM Stage**: `llm_extractor.py` - OpenAI GPT-4o-mini extracts structured JSON from raw text

The system evolved from complex language detection to a simplified, production-ready pipeline optimized for Indian electricity bills.

## Core Components

### Main Pipeline (`integrated_extractor.py`)
- **Entry point**: Batch processes all PDFs in `file samples/` directory
- **Output**: Timestamped JSON files with comprehensive extraction results
- **Usage**: `python integrated_extractor.py` (processes all files automatically)

### OCR Engine (`ocr_extractor.py`) 
- **Method**: `extract_text_from_file(file_path)` for files, `extract_text(image)` for PIL Images
- **Languages**: Comprehensive Indian language support (14 languages: `eng+hin+mar+guj+ben+tam+tel+kan+mal+ori+pan+asm+urd+san`)
- **Preprocessing**: Automatic image enhancement (contrast, sharpness, noise reduction)

### LLM Engine (`llm_extractor.py`)
- **Schema**: Raw/parsed value pairs for all fields (46 total possible fields)
- **Key Method**: `extract_invoice_data(raw_text, filename)` 
- **Output**: Structured JSON with confidence scoring and accuracy assessment

## Data Schema Pattern

All extracted data follows a **raw/parsed dual format**:
```json
{
  "invoiceNumber": {
    "raw": "Bill No: RJVNL/2024/001234",  // Exact OCR text
    "parsed": "RJVNL/2024/001234"          // Cleaned value
  }
}
```

Critical fields include: `invoiceNumber`, `customerInfo` (name, ID, address, mobile), `billingDetails` (totalAmount, dueDate), `meterReadings` array, and date fields with YYYY-MM-DD normalization.

## Environment Setup

### Required Dependencies
- **Tesseract OCR**: Must be installed system-wide with comprehensive Indian language packs (14 languages: `eng`, `hin`, `mar`, `guj`, `ben`, `tam`, `tel`, `kan`, `mal`, `ori`, `pan`, `asm`, `urd`, `san`)
- **Poppler**: For PDF→image conversion
- **Python packages**: `requirements.txt` (pytesseract, pdf2image, Pillow, openai)

### Configuration (`.env`)
```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
SAMPLES_DIR=file samples
```

## Development Workflows

### Testing New Files
1. Place PDF in `file samples/` directory
2. Run `python integrated_extractor.py`
3. Check console output for confidence scores and field counts
4. Review timestamped JSON output file

### Modifying Extraction Schema
- **LLM Schema**: Update `_create_extraction_prompt()` in `llm_extractor.py`
- **Accuracy Assessment**: Modify `assess_extraction_accuracy()` field counting logic
- **Error Handling**: Both extractors use structured error responses matching the schema

### Performance Optimization
- **OCR Speed**: ~3.5 minutes for 21 files (simplified single-pass approach)
- **LLM Accuracy**: 68-92% confidence scores achieved in production
- **Memory**: Images processed in batches, OCR text cached in results

## Project-Specific Conventions

### Error Handling Pattern
All components return structured responses with `success` flags and detailed error messages. Failed extractions still produce valid schema with null values.

### File Naming Convention
Output files use timestamp format: `llm_extracted_data_YYYYMMDD_HHMMSS.json`

### Logging Strategy
All components use Python logging with INFO level. OCR logs character counts, LLM logs field extraction counts.

## Critical Integration Points

### OCR → LLM Handoff
Raw OCR text passes directly to LLM with no preprocessing. The LLM handles text cleaning and normalization internally.

### Batch Processing Flow
1. Scan `file samples/` for all files
2. Process each file through OCR→LLM pipeline  
3. Aggregate results with summary statistics
4. Generate single timestamped JSON output

### Confidence Scoring System
- **Field-level**: Counts extracted vs. total possible fields (46 max)
- **Quality assessment**: Weighted scoring based on critical fields presence
- **Overall confidence**: Average of completion rate and quality score

## Common Debugging Patterns

### OCR Issues
- Check Tesseract installation and language packs
- Verify image quality in console output (character count warnings)
- Use verbose logging to see preprocessing steps

### LLM Extraction Issues  
- Monitor field extraction counts in console output
- Check confidence scores (below 60% indicates poor OCR input)
- Review raw text in output JSON for OCR quality assessment

### Schema Validation
- LLM responses are JSON-parsed with error handling
- Malformed responses trigger structured error responses
- All output maintains consistent schema regardless of success/failure

When working with this codebase, prioritize understanding the dual OCR→LLM pipeline and the raw/parsed data schema. The system is optimized for production batch processing of Indian electricity bills with comprehensive error handling and accuracy assessment.
