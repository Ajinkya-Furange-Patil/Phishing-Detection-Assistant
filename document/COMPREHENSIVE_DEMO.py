"""
Comprehensive Phishing Analysis Demo
Demonstrates all features of the advanced analyzer
"""

import requests
import json
from datetime import datetime

API_URL = 'http://localhost:5000'

def print_header(text):
    print("\n" + "=" * 100)
    print(f"  {text}")
    print("=" * 100)

def print_section(text):
    print(f"\n{'─' * 100}")
    print(f"  {text}")
    print(f"{'─' * 100}")

def analyze_email(description, email_content, subject, sender):
    """Perform comprehensive analysis on an email."""
    
    print_header(f"TEST CASE: {description}")
    
    print(f"\n📧 EMAIL DETAILS:")
    print(f"   Subject: {subject}")
    print(f"   Sender: {sender}")
    print(f"   Content Preview: {email_content[:150]}...")
    
    try:
        response = requests.post(
            f'{API_URL}/analyze',
            json={
                'email_content': email_content,
                'subject': subject,
                'sender': sender,
                'model': 'random_forest'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result['success']:
                analysis = result['analysis']
                
                # Display results
                print_section("📊 RISK ASSESSMENT")
                print(f"   Phishing Probability: {analysis['phishing_probability']*100:.2f}%")
                print(f"   Risk Level: {analysis['risk_level']}")
                print(f"   Threat Score: {analysis['threat_indicators']['score']}/{analysis['threat_indicators']['max_score']}")
                
                # Red Flags
                if analysis['red_flags']:
                    print_section(f"🚩 RED FLAGS DETECTED ({len(analysis['red_flags'])})")
                    for i, flag in enumerate(analysis['red_flags'], 1):
                        print(f"\n   {i}. [{flag['severity']}] {flag['type']}")
                        print(f"      • {flag['description']}")
                        print(f"      • Indicator: {flag['indicator']}")
                
                # Social Engineering
                if analysis['social_engineering']['details']:
                    print_section(f"🎭 SOCIAL ENGINEERING TECHNIQUES ({analysis['social_engineering']['techniques_detected']})")
                    for tech in analysis['social_engineering']['details']:
                        print(f"\n   • {tech['technique']} [{tech['severity']}]")
                        print(f"     Description: {tech['description']}")
                        print(f"     Why it works: {tech['explanation']}")
                        if tech['keywords_found']:
                            print(f"     Keywords found: {', '.join(tech['keywords_found'])}")
                
                # Sender Analysis
                print_section("✉️ SENDER ANALYSIS")
                sender_info = analysis['sender_analysis']
                print(f"   Email: {sender_info.get('email', 'N/A')}")
                print(f"   Domain: {sender_info.get('domain', 'N/A')}")
                print(f"   Risk Level: {sender_info['risk']}")
                print(f"   Issues:")
                for issue in sender_info['issues']:
                    print(f"      • {issue}")
                
                # URL Analysis
                if analysis['url_analysis']['total_urls'] > 0:
                    print_section("🔗 URL ANALYSIS")
                    print(f"   Total URLs: {analysis['url_analysis']['total_urls']}")
                    print(f"   Risk Level: {analysis['url_analysis']['risk']}")
                    if analysis['url_analysis']['urls_found']:
                        print(f"   URLs Found:")
                        for url in analysis['url_analysis']['urls_found']:
                            print(f"      • {url}")
                    print(f"   Issues:")
                    for issue in analysis['url_analysis']['issues']:
                        print(f"      • {issue}")
                
                # Recommended Actions
                print_section("📋 RECOMMENDED ACTIONS")
                for rec in analysis['recommended_actions']:
                    print(f"\n   [{rec['priority']}] {rec['action']}")
                    print(f"   Reason: {rec['reason']}")
                    print(f"   Steps to take:")
                    for step in rec['steps']:
                        print(f"      ✓ {step}")
                
                # Employee Awareness
                print_section("🎓 EMPLOYEE AWARENESS ADVICE")
                awareness = analysis['employee_awareness']
                
                if awareness['learning_points']:
                    print("\n   Key Learning Points:")
                    for point in awareness['learning_points']:
                        print(f"\n   📌 {point['topic']}")
                        print(f"      • Lesson: {point['lesson']}")
                        print(f"      • Tip: {point['tip']}")
                        print(f"      • Example: {point['example']}")
                
                print("\n   General Security Advice:")
                for advice in awareness['general_advice']:
                    print(f"      {advice}")
                
                print(f"\n   Training Recommendation:")
                print(f"      {awareness['training_recommendation']}")
                
                # Quiz Questions
                if awareness['quiz_questions']:
                    print("\n   Security Awareness Quiz:")
                    for i, q in enumerate(awareness['quiz_questions'], 1):
                        print(f"\n      Q{i}: {q['question']}")
                        print(f"      ✓ Correct: {q['correct_answer']}")
                        print(f"      Explanation: {q['explanation']}")
                
                # Threat Indicators
                print_section("⚠️ THREAT INDICATORS")
                threat = analysis['threat_indicators']
                print(f"   Threat Level: {threat['threat_level']}")
                print(f"   Score: {threat['score']}/{threat['max_score']} ({threat['percentage']:.1f}%)")
                if threat['indicators']:
                    print(f"   Detected Indicators:")
                    for indicator in threat['indicators']:
                        print(f"      • {indicator}")
                
                print("\n" + "=" * 100)
                
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API. Is the server running?")
        print("   Start it with: python backend/app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    print_header("🛡️ COMPREHENSIVE PHISHING ANALYSIS SYSTEM - DEMO")
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
            print("⚠️  API may not be ready")
    except:
        print("❌ API is not responding!")
        print("\n⚠️  Please start the backend server first:")
        print("   cd backend")
        print("   python app.py")
        return
    
    # Test cases with comprehensive details
    test_cases = [
        {
            "description": "High-Risk Phishing - Account Suspension Threat",
            "subject": "URGENT: Your Account Will Be Suspended",
            "sender": "security-alert@gmail.com",
            "content": """
URGENT ACTION REQUIRED!

Your account has been flagged for suspicious activity. If you do not verify your 
identity within 24 hours, your account will be permanently suspended and all data deleted.

Click here immediately to verify: http://secure-verify-account.tk/login

Failure to act will result in:
- Immediate account termination
- Loss of all data
- Legal action may be taken

This is your final warning. Act now!

Security Team
            """
        },
        {
            "description": "Prize Scam - Lottery Winner",
            "subject": "Congratulations! You've Won $1,000,000",
            "sender": "lottery-winner@yahoo.com",
            "content": """
CONGRATULATIONS!!!

You have been selected as the lucky winner of our international lottery!

Prize Amount: $1,000,000 USD

To claim your prize:
1. Click here: http://claim-prize.xyz/winner
2. Provide your bank account details
3. Pay a small processing fee of $500
4. Receive your winnings within 48 hours!

This is a limited time offer. Claim now before it expires!

Don't miss this once-in-a-lifetime opportunity!
            """
        },
        {
            "description": "Legitimate - Team Meeting Invitation",
            "subject": "Weekly Team Meeting - Thursday 3pm",
            "sender": "sarah.johnson@company.com",
            "content": """
Hi Team,

This is a reminder about our weekly team meeting scheduled for Thursday at 3pm 
in Conference Room B.

Agenda:
- Q4 project status updates
- Budget review for next quarter
- New team member introduction
- Questions and discussion

Please review the quarterly report I sent yesterday before the meeting.

Looking forward to seeing everyone there!

Best regards,
Sarah Johnson
Project Manager
Company Inc.
            """
        },
        {
            "description": "Medium Risk - Password Reset Request",
            "subject": "Password Reset Required",
            "sender": "no-reply@service-alerts.com",
            "content": """
Hello,

We detected unusual login activity on your account from an unrecognized device.

For your security, please reset your password immediately by clicking the link below:

Reset Password: http://reset-password.suspicious-domain.com

If you don't reset within 12 hours, your account may be locked.

If you didn't request this, please contact support.

Thank you,
Security Team
            """
        },
        {
            "description": "Legitimate - Invoice Notification",
            "subject": "Invoice #INV-2024-12345",
            "sender": "billing@trustedcompany.com",
            "content": """
Dear Valued Customer,

Thank you for your recent purchase. Please find your invoice details below:

Invoice Number: INV-2024-12345
Date: January 15, 2024
Amount: $149.99
Payment Due: February 15, 2024

You can view your invoice by logging into your account at www.trustedcompany.com

If you have any questions, please contact our support team at 1-800-123-4567 
or email support@trustedcompany.com

We appreciate your business!

Best regards,
Billing Department
Trusted Company Inc.
            """
        }
    ]
    
    # Run all test cases
    for i, test_case in enumerate(test_cases, 1):
        analyze_email(
            f"{i}/{len(test_cases)} - {test_case['description']}",
            test_case['content'],
            test_case['subject'],
            test_case['sender']
        )
        
        if i < len(test_cases):
            input("\n\n⏸️  Press Enter to continue to next test case...")
    
    # Final summary
    print_header("✨ DEMONSTRATION COMPLETE")
    print("\n📊 Analysis Features Demonstrated:")
    print("   ✅ ML-based phishing probability")
    print("   ✅ Red flag detection")
    print("   ✅ Social engineering technique identification")
    print("   ✅ Sender risk assessment")
    print("   ✅ URL analysis")
    print("   ✅ Actionable recommendations")
    print("   ✅ Employee awareness training")
    print("   ✅ Security quiz generation")
    print("   ✅ Threat scoring")
    
    print("\n🎯 System Capabilities:")
    print("   • Analyzes email content, subject, and sender")
    print("   • Detects 10+ types of red flags")
    print("   • Identifies 6 social engineering techniques")
    print("   • Provides priority-based action items")
    print("   • Generates customized security training")
    print("   • Creates awareness quiz questions")
    print("   • Calculates comprehensive threat scores")
    
    print("\n🚀 Next Steps:")
    print("   1. Use the web interface at: backend/test_interface.html")
    print("   2. Install browser extension for real-time protection")
    print("   3. Test with your own email samples")
    print("   4. Share with security team for evaluation")
    print("   5. Deploy to production for organization-wide use")
    
    print("\n" + "=" * 100 + "\n")

if __name__ == "__main__":
    main()
