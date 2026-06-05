"""
Quick Demo Script - Phishing Detection API
Run this to see the system in action!
"""

import requests
import json
from datetime import datetime

API_URL = 'http://localhost:5000'

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_result(result):
    pred = result['prediction']
    
    # Determine color/emoji based on result
    if pred['is_phishing']:
        emoji = "🚨"
        status = "PHISHING DETECTED"
    else:
        emoji = "✅"
        status = "SAFE"
    
    print(f"\n{emoji} {status} {emoji}")
    print(f"\nConfidence: {pred['confidence']*100:.1f}%")
    print(f"Risk Level: {pred['risk_level']}")
    print(f"Phishing Probability: {pred['phishing_probability']*100:.1f}%")
    print(f"Legitimate Probability: {pred['legitimate_probability']*100:.1f}%")
    print(f"Model Used: {pred['model_used'].replace('_', ' ').title()}")
    
    print("\nFeatures Detected:")
    for key, value in pred['features'].items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")

def test_email(description, text):
    print_header(f"Test: {description}")
    print(f"\nEmail Text:\n{text[:150]}...")
    
    try:
        response = requests.post(
            f'{API_URL}/predict',
            json={'text': text, 'model': 'random_forest'},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print_result(result)
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Start it with: python backend/app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print_header("🛡️ PHISHING DETECTION SYSTEM - LIVE DEMO")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Endpoint: {API_URL}")
    
    # Check API health
    try:
        response = requests.get(f'{API_URL}/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status'].upper()}")
            print(f"✅ Models Loaded: {data['models_loaded']}")
        else:
            print("⚠️ API may not be ready")
    except:
        print("❌ API is not responding!")
        print("\n⚠️ Please start the backend server first:")
        print("   cd backend")
        print("   python app.py")
        return
    
    # Test cases
    test_cases = [
        {
            "description": "Phishing - Urgent Account Suspension",
            "text": "URGENT! Your account has been suspended due to suspicious activity. Click here immediately to restore access or all your data will be permanently deleted: http://suspicious-bank.com/restore-account"
        },
        {
            "description": "Phishing - Lottery Scam",
            "text": "Congratulations! You have won $1,000,000 in our international lottery! To claim your prize, please provide your bank account details and pay a small processing fee of $500. Click here: http://fake-lottery.com/claim"
        },
        {
            "description": "Phishing - Password Reset Scam",
            "text": "Your password has expired. You must reset it immediately to continue accessing your account. Click the link below to verify your identity: http://phishing-site.com/verify?user=victim"
        },
        {
            "description": "Legitimate - Team Meeting",
            "text": "Hi team, please review the quarterly report I sent yesterday. Let's discuss the key findings in tomorrow's meeting at 3pm in Conference Room B. Looking forward to your feedback. Thanks, Sarah"
        },
        {
            "description": "Legitimate - Invoice Email",
            "text": "Dear valued customer, thank you for your recent purchase. Your invoice #INV-12345 is attached to this email. The payment is due within 30 days. If you have any questions, please contact our support team at support@company.com"
        },
        {
            "description": "Legitimate - Project Update",
            "text": "Project status update: The development phase is on track and 75% complete. We're scheduled to begin testing next week. All team members should update their tasks in the project tracker by Friday. Let me know if you need any assistance."
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        test_email(f"{i}/{len(test_cases)} - {test_case['description']}", test_case['text'])
        
        # Pause between tests for readability
        if i < len(test_cases):
            input("\nPress Enter to continue to next test...")
    
    # Summary
    print_header("✨ DEMO COMPLETE")
    print("\nWhat you can do next:")
    print("  1. Open test_interface.html in your browser for interactive testing")
    print("  2. Load the browser extension (frontend folder) in Chrome/Edge")
    print("  3. Test with your own email samples")
    print("  4. Check the API documentation in backend/README.md")
    print("  5. Review model performance in models/results/")
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
