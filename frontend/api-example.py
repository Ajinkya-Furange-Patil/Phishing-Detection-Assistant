"""
Example Flask API for Phishing Detection Assistant
This is a simple backend that the extension can connect to
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension

@app.route('/api/scan', methods=['POST'])
def scan_email():
    """
    Scan an email for phishing indicators
    
    Expected input:
    {
        "subject": "Email subject",
        "sender": "sender@example.com",
        "body": "Email body text",
        "links": ["http://example.com"],
        "headers": {...},
        "attachments": [...],
        "platform": "gmail"
    }
    
    Returns:
    {
        "isPhishing": false,
        "confidence": 0.85,
        "modules": {
            "content": 0.12,
            "url": 0.08,
            "header": 0.05,
            "attachment": 0.01,
            "behavioral": 0.10
        },
        "threats": []
    }
    """
    try:
        email_data = request.get_json()
        
        # Extract email components
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', '')
        body = email_data.get('body', '')
        links = email_data.get('links', [])
        attachments = email_data.get('attachments', [])
        
        # ============================================
        # TODO: Replace with actual ML model inference
        # ============================================
        # This is a placeholder - implement your 5-module detection here
        
        # Module 1: Content Analysis (BERT)
        content_score = analyze_content(subject, body)
        
        # Module 2: URL Analysis
        url_score = analyze_urls(links)
        
        # Module 3: Header Analysis
        header_score = analyze_headers(sender)
        
        # Module 4: Attachment Analysis
        attachment_score = analyze_attachments(attachments)
        
        # Module 5: Behavioral Analysis
        behavioral_score = analyze_behavior(subject, body)
        
        # Meta-Learner: Combine all module scores
        # TODO: Replace with trained XGBoost meta-learner
        combined_score = (content_score + url_score + header_score + 
                         attachment_score + behavioral_score) / 5
        
        # Determine if phishing
        is_phishing = combined_score > 0.5
        
        # Identify specific threats
        threats = []
        if url_score > 0.7:
            threats.append("Suspicious URLs detected")
        if header_score > 0.7:
            threats.append("Email authentication failed")
        if behavioral_score > 0.7:
            threats.append("Manipulative language detected")
        if attachment_score > 0.7:
            threats.append("Risky attachments found")
        
        # Return results
        response = {
            "isPhishing": is_phishing,
            "confidence": float(combined_score),
            "modules": {
                "content": float(content_score),
                "url": float(url_score),
                "header": float(header_score),
                "attachment": float(attachment_score),
                "behavioral": float(behavioral_score)
            },
            "threats": threats
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# Placeholder analysis functions
# TODO: Replace these with actual ML models
# ============================================

def analyze_content(subject, body):
    """Module 1: BERT content analysis"""
    # Placeholder - implement BERT model inference
    phishing_keywords = ['urgent', 'verify', 'suspended', 'account', 'click', 'password']
    text = (subject + ' ' + body).lower()
    score = sum(1 for keyword in phishing_keywords if keyword in text) / len(phishing_keywords)
    return min(score, 1.0)

def analyze_urls(links):
    """Module 2: URL feature extraction"""
    # Placeholder - implement URL feature analysis
    if not links:
        return 0.0
    
    suspicious_count = 0
    for url in links:
        if any(indicator in url.lower() for indicator in ['.tk', '.ml', 'bit.ly', 'tinyurl']):
            suspicious_count += 1
        if 'http://' in url:  # No HTTPS
            suspicious_count += 0.5
    
    return min(suspicious_count / len(links), 1.0)

def analyze_headers(sender):
    """Module 3: Email header verification"""
    # Placeholder - implement SPF/DKIM/DMARC checking
    # In production, parse actual email headers
    suspicious_domains = ['@temp-mail.com', '@guerrillamail.com']
    score = 0.8 if any(domain in sender.lower() for domain in suspicious_domains) else 0.1
    return score

def analyze_attachments(attachments):
    """Module 4: Attachment analysis"""
    # Placeholder - implement attachment entropy/macro detection
    if not attachments:
        return 0.0
    
    risky_extensions = ['.exe', '.docm', '.xlsm', '.js', '.vbs', '.bat']
    risky_count = sum(1 for att in attachments 
                     if any(att.get('name', '').lower().endswith(ext) 
                     for ext in risky_extensions))
    
    return min(risky_count / len(attachments), 1.0)

def analyze_behavior(subject, body):
    """Module 5: Behavioral/psychological analysis"""
    # Placeholder - implement psychological trigger detection
    urgency_words = ['urgent', 'immediate', 'act now', 'expires', 'limited time']
    threat_words = ['suspend', 'close', 'terminate', 'block', 'restricted']
    
    text = (subject + ' ' + body).lower()
    urgency_count = sum(1 for word in urgency_words if word in text)
    threat_count = sum(1 for word in threat_words if word in text)
    
    return min((urgency_count + threat_count) / 10, 1.0)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Phishing Detection API is running"}), 200


if __name__ == '__main__':
    print("Starting Phishing Detection API...")
    print("Backend running on http://localhost:5000")
    print("Extension should connect to: http://localhost:5000/api/scan")
    app.run(debug=True, host='0.0.0.0', port=5000)
