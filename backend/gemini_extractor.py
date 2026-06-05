"""
Gemini API Integration for Email Content Extraction
Uses Google's Gemini AI to extract structured email data from raw HTML
"""

import os
import google.generativeai as genai
from typing import Dict, Any
import json
import re

class GeminiEmailExtractor:
    """Extract email components using Gemini AI."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini extractor.
        
        Args:
            api_key: Google Gemini API key. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_email_components(self, page_html: str) -> Dict[str, Any]:
        """
        Extract email components from raw HTML using Gemini.
        
        Args:
            page_html: Raw HTML content from email page
            
        Returns:
            Dictionary with extracted email components:
            {
                'subject': str,
                'sender': str,
                'sender_name': str,
                'body': str,
                'to': str,
                'cc': str,
                'date': str,
                'urls': list,
                'attachments': list,
                'extraction_success': bool,
                'extraction_confidence': float
            }
        """
        
        prompt = self._create_extraction_prompt(page_html)
        
        try:
            response = self.model.generate_content(prompt)
            extracted_data = self._parse_gemini_response(response.text)
            extracted_data['extraction_success'] = True
            return extracted_data
            
        except Exception as e:
            print(f"Gemini extraction error: {e}")
            return self._fallback_extraction(page_html)
    
    def _create_extraction_prompt(self, html: str) -> str:
        """Create prompt for Gemini to extract email data."""
        
        # Limit HTML size to avoid token limits (keep first 50000 chars)
        html_snippet = html[:50000] if len(html) > 50000 else html
        
        prompt = f"""
You are an expert email parser. Extract the following information from this email HTML content.

IMPORTANT: Return ONLY a valid JSON object with these exact fields. No additional text.

Required fields:
- subject: The email subject line (string)
- sender: The sender's email address (string, format: email@domain.com)
- sender_name: The sender's display name (string)
- body: The main email body text (string, plain text only, no HTML tags)
- to: Recipient email address (string)
- cc: CC recipients if any (string, comma-separated)
- date: Email date/time (string)
- urls: List of URLs found in email (array of strings)
- attachments: List of attachment names (array of strings)
- extraction_confidence: Your confidence in extraction accuracy (float 0-1)

Rules:
1. Extract plain text only for body - remove all HTML tags
2. If a field is not found, use empty string "" or empty array []
3. For body, preserve paragraph structure but remove HTML
4. Extract ALL URLs including hidden ones in href attributes
5. Return ONLY the JSON object, nothing else

HTML Content:
{html_snippet}

JSON Response:
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response."""
        
        try:
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Validate required fields
            required_fields = ['subject', 'sender', 'body']
            for field in required_fields:
                if field not in data:
                    data[field] = ''
            
            # Ensure optional fields exist
            optional_fields = {
                'sender_name': '',
                'to': '',
                'cc': '',
                'date': '',
                'urls': [],
                'attachments': [],
                'extraction_confidence': 0.8
            }
            
            for field, default in optional_fields.items():
                if field not in data:
                    data[field] = default
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response was: {response_text[:500]}")
            return self._fallback_extraction_from_text(response_text)
    
    def _fallback_extraction_from_text(self, text: str) -> Dict[str, Any]:
        """Fallback: Try to extract from non-JSON response."""
        
        data = {
            'subject': '',
            'sender': '',
            'sender_name': '',
            'body': text,  # Use full response as body
            'to': '',
            'cc': '',
            'date': '',
            'urls': re.findall(r'https?://[^\s<>"]+', text),
            'attachments': [],
            'extraction_confidence': 0.3,
            'extraction_success': False
        }
        
        # Try to find email patterns
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if emails:
            data['sender'] = emails[0]
        
        return data
    
    def _fallback_extraction(self, html: str) -> Dict[str, Any]:
        """Fallback extraction using regex when Gemini fails."""
        
        print("Using fallback extraction (regex-based)")
        
        data = {
            'subject': '',
            'sender': '',
            'sender_name': '',
            'body': '',
            'to': '',
            'cc': '',
            'date': '',
            'urls': [],
            'attachments': [],
            'extraction_confidence': 0.5,
            'extraction_success': False
        }
        
        # Remove HTML tags for body
        body = re.sub(r'<[^>]+>', ' ', html)
        body = re.sub(r'\s+', ' ', body).strip()
        data['body'] = body[:5000]  # Limit length
        
        # Extract URLs
        data['urls'] = re.findall(r'https?://[^\s<>"]+', html)
        
        # Extract email addresses
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html)
        if emails:
            data['sender'] = emails[0]
            if len(emails) > 1:
                data['to'] = emails[1]
        
        # Try to find subject in common patterns
        subject_patterns = [
            r'<title>([^<]+)</title>',
            r'subject["\s:]+([^"<\n]+)',
            r'<h1[^>]*>([^<]+)</h1>',
        ]
        for pattern in subject_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                data['subject'] = match.group(1).strip()
                break
        
        return data


def test_extractor():
    """Test the Gemini extractor with sample HTML."""
    
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Account Verification Required</title></head>
    <body>
        <div class="email">
            <div class="header">
                <span class="from">security@company.com</span>
                <span class="to">user@example.com</span>
                <span class="date">2024-01-15 10:30 AM</span>
            </div>
            <h1 class="subject">URGENT: Account Verification Required</h1>
            <div class="body">
                <p>Dear User,</p>
                <p>Your account has been flagged for suspicious activity.</p>
                <p>Please verify your identity by clicking here: 
                <a href="http://suspicious-link.com">Verify Now</a></p>
                <p>If you don't verify within 24 hours, your account will be suspended.</p>
                <p>Security Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        extractor = GeminiEmailExtractor()
        result = extractor.extract_email_components(sample_html)
        
        print("Extraction Result:")
        print(json.dumps(result, indent=2))
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo use Gemini API:")
        print("1. Get API key from: https://makersuite.google.com/app/apikey")
        print("2. Set environment variable: GEMINI_API_KEY=your-key-here")


if __name__ == "__main__":
    test_extractor()
