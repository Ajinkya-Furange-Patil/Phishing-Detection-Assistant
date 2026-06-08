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
            print("[WARN] Gemini API key not found. Gemini extraction will be unavailable, falling back to regex.")
            self.model = None
            return
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
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
        if not self.model:
            return self._fallback_extraction(page_html)
        
        prompt = self._create_extraction_prompt(page_html)
        
        try:
            # Use standard API call with timeout options to prevent ThreadPoolExecutor deadlocks in Flask reloader
            response = self.model.generate_content(
                prompt,
                request_options={"timeout": 30.0}
            )
            
            extracted_data = self._parse_gemini_response(response.text)
            extracted_data['extraction_success'] = True
            return extracted_data
            
        except Exception as e:
            print(f"Gemini extraction error: {e}")
            return self._fallback_extraction(page_html)
    
    def _create_extraction_prompt(self, html: str) -> str:
        """Create prompt for Gemini to extract email data."""
        
        # Limit HTML size to avoid token limits (keep first 40000 chars)
        html_snippet = html[:40000] if len(html) > 40000 else html
        
        prompt = f"""
You are a precise email parser. Your task is to extract exactly three fields from the email HTML below into a strict JSON format.

Required Fields:
- "sender": The sender's email address and/or display name (e.g., "John Doe <john@domain.com>"). Parse this directly from From/Sender information in the HTML.
- "subject": The exact subject line of the email.
- "body": The main readable plain-text email message body. Do NOT include HTML tags, CSS styles, JavaScript code, navigation menus, header lists, or sidebar noise. ONLY extract text that is part of the actual message body content. Do NOT add or invent any text that is not explicitly present.

Rules:
1. Extract ONLY these 3 fields. Do not add any other keys.
2. If a field is not found, use an empty string "".
3. Return ONLY a valid raw JSON object. Do not include markdown code block syntax (like ```json). No intro, no explanation.

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
            
            # If urls are not extracted, parse them from body text
            if not data['urls']:
                import re
                data['urls'] = re.findall(r'https?://[^\s<>"]+', data.get('body', ''))
                
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

    def analyze_email(self, email_content: str, subject: str = '', sender: str = '') -> Dict[str, Any]:
        """
        Analyze email content for phishing using Gemini API.
        """
        if not self.model:
            raise ValueError("Gemini model is not initialized. Please verify your GEMINI_API_KEY environment variable.")
            
        prompt = f"""
You are an advanced cybersecurity AI specialized in phishing detection and email security auditing.
Analyze the following email for phishing indicators, threat levels, and social engineering techniques.

Email Details:
- Sender: {sender}
- Subject: {subject}
- Content: {email_content}

Your task is to output a detailed phishing analysis strictly adhering to the JSON structure specified below. Do not add markdown code block markers (like ```json). No preamble, no explanation, just raw JSON.

Required JSON Structure:
{{
  "phishing_probability": float (from 0.0 to 1.0 representing the confidence/probability that this email is phishing),
  "risk_level": "HIGH" | "MEDIUM" | "LOW",
  "red_flags": [
    {{
      "type": "Urgency" | "Suspicious Request" | "Prize Scam" | "Financial Request" | "Threatening Language" | "Domain Mismatch" | "Poor Formatting" | "Other",
      "severity": "HIGH" | "MEDIUM" | "LOW",
      "description": "Short explanation of this specific flag",
      "indicator": "The behavior/indicator that tipped off this flag"
    }}
  ],
  "social_engineering": {{
    "techniques_detected": int,
    "details": [
      {{
        "technique": "Urgency" | "Fear" | "Greed" | "Authority" | "Trust" | "Curiosity" | "Impersonation",
        "description": "How this technique is defined generally",
        "keywords_found": [string],
        "severity": "HIGH" | "MEDIUM",
        "explanation": "Specific explanation of how this technique is used in this email"
      }}
    ],
    "overall_risk": "HIGH" | "MEDIUM" | "LOW"
  }},
  "sender_analysis": {{
    "email": "{sender}",
    "domain": "Extracted domain name of sender",
    "valid": true | false,
    "risk": "HIGH" | "MEDIUM" | "LOW",
    "issues": [string]
  }},
  "url_analysis": {{
    "total_urls": int,
    "risk": "HIGH" | "MEDIUM" | "LOW",
    "issues": [string]
  }},
  "content_analysis": {{
    "subject": "{subject}",
    "body_length": int,
    "risk": "HIGH" | "MEDIUM" | "LOW",
    "issues": [string]
  }},
  "recommended_actions": [
    {{
      "priority": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      "action": "What the user should do",
      "reason": "Why this action is critical",
      "steps": [string]
    }}
  ],
  "employee_awareness": {{
    "learning_points": [
      {{
        "topic": "Educational concept topic",
        "lesson": "The core takeaway from this email pattern",
        "tip": "Actionable daily habit tip to avoid this threat"
      }}
    ],
    "general_advice": [string]
  }},
  "threat_indicators": {{
    "score": int (0-100 overall threat score),
    "max_score": 100,
    "percentage": float (0.0 to 100.0),
    "threat_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
    "indicators": [string]
  }}
}}
"""
        try:
            # Use standard API call with timeout options to prevent ThreadPoolExecutor deadlocks in Flask reloader
            response = self.model.generate_content(
                prompt,
                request_options={"timeout": 30.0}
            )
            
            cleaned = response.text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON to ensure correctness
            analysis_data = json.loads(cleaned)
            return analysis_data
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            err_str = str(e)
            if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
                raise ValueError("Google Gemini API key is invalid. Please verify the GEMINI_API_KEY environment variable on your server.")
            raise e


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
