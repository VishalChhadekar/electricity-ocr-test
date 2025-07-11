#!/usr/bin/env python3
"""
LLM Invoice Data Extractor
Uses OpenAI to extract structured data from electricity bill OCR text
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import openai
except ImportError:
    print("Error: OpenAI package not installed. Please run: pip install openai")
    exit(1)


class LLMInvoiceExtractor:
    """Extracts structured data from electricity bills using OpenAI."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize the LLM extractor with OpenAI API key."""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        self.logger = logging.getLogger(__name__)
        
    def assess_extraction_accuracy(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the accuracy and completeness of extracted data."""
        
        data = extracted_data.get("data", {})
        
        # Count non-null extracted fields
        extracted_count = 0
        total_fields = 0
        
        # Simple fields (invoiceNumber, dates)
        simple_fields = ["invoiceNumber", "previousReadingDate", "presentReadingDate", 
                        "billingDate", "nextReadingDate"]
        
        for field in simple_fields:
            total_fields += 2  # raw and parsed
            if data.get(field, {}).get("raw"):
                extracted_count += 1
            if data.get(field, {}).get("parsed"):
                extracted_count += 1
        
        # Customer info fields
        customer_info = data.get("customerInfo", {})
        customer_fields = ["name", "customerId", "address", "mobile"]
        
        for field in customer_fields:
            total_fields += 2  # raw and parsed
            if customer_info.get(field, {}).get("raw"):
                extracted_count += 1
            if customer_info.get(field, {}).get("parsed"):
                extracted_count += 1
        
        # Billing details
        billing_details = data.get("billingDetails", {})
        billing_fields = ["totalAmount", "dueDate", "billingPeriod"]
        
        for field in billing_fields:
            total_fields += 2  # raw and parsed
            if billing_details.get(field, {}).get("raw"):
                extracted_count += 1
            if billing_details.get(field, {}).get("parsed"):
                extracted_count += 1
        
        # Utility info
        utility_info = data.get("utilityInfo", {})
        utility_fields = ["companyName", "state"]
        
        for field in utility_fields:
            total_fields += 2  # raw and parsed
            if utility_info.get(field, {}).get("raw"):
                extracted_count += 1
            if utility_info.get(field, {}).get("parsed"):
                extracted_count += 1
        
        # Meter readings (count any meter reading as additional extracted data)
        meter_readings = data.get("meterReadings", [])
        meter_fields_per_reading = 5  # meterNumber, previousReading, presentReading, multiplyingFactor, unitsConsumed, maxDemand
        
        for reading in meter_readings:
            for field in ["meterNumber", "previousReading", "presentReading", "multiplyingFactor", "unitsConsumed", "maxDemand"]:
                if reading.get(field):
                    extracted_count += 1
        
        # Add meter reading slots to total (assume max 3 meters per bill)
        total_fields += 6 * 3  # 6 fields per meter, max 3 meters
        
        # Calculate accuracy metrics
        completion_rate = extracted_count / total_fields if total_fields > 0 else 0
        
        # Quality assessment based on field extraction patterns
        quality_score = 0.0
        
        # Basic info extracted
        if data.get("invoiceNumber", {}).get("parsed"):
            quality_score += 0.2
        
        # Date consistency
        date_fields = ["previousReadingDate", "presentReadingDate", "billingDate"]
        valid_dates = sum(1 for field in date_fields if data.get(field, {}).get("parsed"))
        quality_score += (valid_dates / len(date_fields)) * 0.3
        
        # Customer info completeness
        customer_completeness = sum(1 for field in customer_fields if customer_info.get(field, {}).get("parsed"))
        quality_score += (customer_completeness / len(customer_fields)) * 0.2
        
        # Billing amount extracted
        if billing_details.get("totalAmount", {}).get("parsed"):
            quality_score += 0.15
        
        # Meter readings extracted
        if meter_readings:
            quality_score += 0.15
        
        # Overall confidence (average of completion and quality)
        overall_confidence = (completion_rate + quality_score) / 2
        
        return {
            "extracted_fields_count": extracted_count,
            "total_possible_fields": total_fields,
            "completion_rate": round(completion_rate, 3),
            "quality_score": round(quality_score, 3),
            "overall_confidence": round(overall_confidence, 3),
            "meter_readings_count": len(meter_readings),
            "has_critical_fields": bool(
                data.get("invoiceNumber", {}).get("parsed") and
                billing_details.get("totalAmount", {}).get("parsed")
            )
        }
    
    def extract_invoice_data(self, raw_text: str, file_name: str) -> Dict[str, Any]:
        """Extract structured data from raw OCR text using OpenAI."""
        
        prompt = self._create_extraction_prompt(raw_text, file_name)
        
        try:
            self.logger.info(f"Sending OCR text to OpenAI for data extraction...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured data from electricity bills. Always return valid JSON with the exact schema requested."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=3000  # Increased for more complex output
            )
            
            # Extract the JSON response
            content = response.choices[0].message.content.strip()
            
            # Remove any markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            # Parse the JSON
            extracted_data = json.loads(content.strip())
            
            # Assess accuracy and update metadata
            accuracy_assessment = self.assess_extraction_accuracy(extracted_data)
            
            # Update extraction metadata with accuracy assessment
            if "extractionMetadata" not in extracted_data:
                extracted_data["extractionMetadata"] = {}
            
            extracted_data["extractionMetadata"].update({
                "extracted_at": datetime.now().isoformat(),
                "model_used": self.model,
                "file_name": file_name,
                "raw_text_length": len(raw_text),
                "extraction_method": "openai_llm",
                **accuracy_assessment
            })
            
            self.logger.info(f"Successfully extracted structured data using {self.model}")
            self.logger.info(f"Accuracy: {accuracy_assessment['overall_confidence']:.2f}, Fields: {accuracy_assessment['extracted_fields_count']}/{accuracy_assessment['total_possible_fields']}")
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from OpenAI: {e}")
            return self._create_error_response(f"Invalid JSON response: {str(e)}", file_name, raw_text)
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            return self._create_error_response(str(e), file_name, raw_text)
    
    def _create_extraction_prompt(self, raw_text: str, file_name: str) -> str:
        """Create a detailed prompt for data extraction."""
        
        return f"""
Extract structured data from this electricity bill OCR text. Return ONLY a valid JSON object with the following exact schema:

{{
  "data": {{
    "invoiceNumber": {{
      "raw": "exact text from OCR or null",
      "parsed": "cleaned/formatted value or null"
    }},
    "previousReadingDate": {{
      "raw": "exact date text from OCR or null",
      "parsed": "YYYY-MM-DD format or null"
    }},
    "presentReadingDate": {{
      "raw": "exact date text from OCR or null", 
      "parsed": "YYYY-MM-DD format or null"
    }},
    "billingDate": {{
      "raw": "exact date text from OCR or null",
      "parsed": "YYYY-MM-DD format or null"
    }},
    "nextReadingDate": {{
      "raw": "exact date text from OCR or null",
      "parsed": "YYYY-MM-DD format or null"
    }},
    "customerInfo": {{
      "name": {{
        "raw": "exact name from OCR or null",
        "parsed": "cleaned name or null"
      }},
      "customerId": {{
        "raw": "exact ID from OCR or null",
        "parsed": "cleaned ID or null"
      }},
      "address": {{
        "raw": "exact address from OCR or null",
        "parsed": "cleaned address or null"
      }},
      "mobile": {{
        "raw": "exact mobile from OCR or null",
        "parsed": "cleaned mobile or null"
      }}
    }},
    "billingDetails": {{
      "totalAmount": {{
        "raw": "exact amount text from OCR or null",
        "parsed": "numeric value or null"
      }},
      "dueDate": {{
        "raw": "exact due date from OCR or null",
        "parsed": "YYYY-MM-DD format or null"
      }},
      "billingPeriod": {{
        "raw": "exact period text from OCR or null",
        "parsed": "cleaned period or null"
      }}
    }},
    "utilityInfo": {{
      "companyName": {{
        "raw": "exact company name from OCR or null",
        "parsed": "cleaned company name or null"
      }},
      "state": {{
        "raw": "exact state from OCR or null",
        "parsed": "cleaned state name or null"
      }}
    }},
    "meterReadings": [
      {{
        "meterNumber": "meter number or null",
        "previousReading": "numeric value as string or null",
        "presentReading": "numeric value as string or null", 
        "multiplyingFactor": "numeric value as string or null",
        "unitsConsumed": "numeric value as string or null",
        "maxDemand": "numeric value as string or null"
      }}
    ]
  }},
  "extractionMetadata": {{
    "confidence_score": "number between 0-1",
    "extracted_fields_count": "number of non-null fields extracted",
    "total_possible_fields": "total number of extractable fields"
  }}
}}

Rules:
1. For "raw" values: Extract EXACTLY as it appears in the OCR text
2. For "parsed" values: Clean, format, and standardize the data
3. Convert dates to YYYY-MM-DD format in parsed values
4. Extract numeric values as strings in meter readings
5. If multiple meters exist, include all in the meterReadings array
6. Use null for missing/unclear information
7. Provide confidence score based on overall extraction quality
8. Count extracted fields accurately
9. Return ONLY valid JSON, no explanations

File name: {file_name}

OCR Text:
{raw_text}
"""

    def _create_error_response(self, error_message: str, file_name: str, raw_text: str) -> Dict[str, Any]:
        """Create an error response with the expected schema."""
        return {
            "data": {
                "invoiceNumber": {
                    "raw": None,
                    "parsed": None
                },
                "previousReadingDate": {
                    "raw": None,
                    "parsed": None
                },
                "presentReadingDate": {
                    "raw": None,
                    "parsed": None
                },
                "billingDate": {
                    "raw": None,
                    "parsed": None
                },
                "nextReadingDate": {
                    "raw": None,
                    "parsed": None
                },
                "customerInfo": {
                    "name": {
                        "raw": None,
                        "parsed": None
                    },
                    "customerId": {
                        "raw": None,
                        "parsed": None
                    },
                    "address": {
                        "raw": None,
                        "parsed": None
                    },
                    "mobile": {
                        "raw": None,
                        "parsed": None
                    }
                },
                "billingDetails": {
                    "totalAmount": {
                        "raw": None,
                        "parsed": None
                    },
                    "dueDate": {
                        "raw": None,
                        "parsed": None
                    },
                    "billingPeriod": {
                        "raw": None,
                        "parsed": None
                    }
                },
                "utilityInfo": {
                    "companyName": {
                        "raw": None,
                        "parsed": None
                    },
                    "state": {
                        "raw": None,
                        "parsed": None
                    }
                },
                "meterReadings": []
            },
            "extractionMetadata": {
                "confidence_score": 0.0,
                "extracted_fields_count": 0,
                "total_possible_fields": 20,
                "extracted_at": datetime.now().isoformat(),
                "model_used": self.model,
                "file_name": file_name,
                "raw_text_length": len(raw_text),
                "extraction_method": "openai_llm",
                "error": error_message
            }
        }

    def validate_extraction(self, extracted_data: Dict[str, Any]) -> bool:
        """Validate the extracted data structure."""
        required_sections = ["bill_info", "customer_info", "billing_details", "utility_info", "additional_charges"]
        
        try:
            for section in required_sections:
                if section not in extracted_data:
                    return False
            
            # Check if we have some meaningful data
            non_null_count = 0
            for section in required_sections:
                for key, value in extracted_data[section].items():
                    if value is not None:
                        non_null_count += 1
            
            return non_null_count > 0
            
        except Exception:
            return False
