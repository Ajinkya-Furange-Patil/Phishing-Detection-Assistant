from flask import Flask, request, jsonify, send_from_directory, send_file, redirect
from flask_cors import CORS
import pickle
import os
import sys
import io
import re
import random
from datetime import datetime
from advanced_analyzer import PhishingAnalyzer

# Set stdout/stderr to UTF-8 to prevent console encoding crashes on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension

# Initialize advanced analyzer
advanced_analyzer = PhishingAnalyzer()

# Initialize Gemini extractor (optional - only if API key is set)
try:
    gemini_extractor = GeminiEmailExtractor()
    GEMINI_AVAILABLE = True
    print("✓ Gemini API initialized")
except Exception as e:
    gemini_extractor = None
    GEMINI_AVAILABLE = False
    print(f"⚠ Gemini API not available: {e}")
    print("  Extension will use fallback extraction")

# Paths to models
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models', 'saved_models')
# Note: On Windows, paths are case-insensitive, but we will look up the model path.
# Since list_dir showed MODELS in uppercase, we check if MODELS exists to build the proper absolute path.
if not os.path.exists(MODEL_DIR):
    MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'MODELS', 'saved_models')

VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
LOGISTIC_MODEL_PATH = os.path.join(MODEL_DIR, 'logistic_regression_model.pkl')
RANDOM_FOREST_PATH = os.path.join(MODEL_DIR, 'random_forest_model.pkl')

# Frontend paths
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

# Load models at startup
print("=" * 80)
print("PHISHGUARD API - Starting Up")
print("=" * 80)

try:
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    print("[OK] TF-IDF Vectorizer loaded")
    
    with open(LOGISTIC_MODEL_PATH, 'rb') as f:
        logistic_model = pickle.load(f)
    print("[OK] Logistic Regression model loaded")
    
    with open(RANDOM_FOREST_PATH, 'rb') as f:
        random_forest_model = pickle.load(f)
    print("[OK] Random Forest model loaded")
    
    print("\nAll models loaded successfully!")
    print("=" * 80)
    
except Exception as e:
    print(f"[ERROR] Error loading models: {e}")
    print("Please run train_models.py first to train and save models.")
    exit(1)

# Default model to use
DEFAULT_MODEL = 'random_forest'  # Options: 'logistic' or 'random_forest'


def extract_urls(text):
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s<>"]*'
    urls = re.findall(url_pattern, text)
    return urls


def extract_features(text):
    """Extract additional features from email text."""
    features = {
        'num_urls': len(extract_urls(text)),
        'num_exclamation': text.count('!'),
        'num_question': text.count('?'),
        'has_urgent': any(word in text.lower() for word in ['urgent', 'immediate', 'act now', 'limited time']),
        'has_suspicious_words': any(word in text.lower() for word in ['click here', 'verify', 'suspend', 'confirm', 'account', 'winner', 'prize', 'claim']),
        'text_length': len(text),
        'has_money_symbols': '$' in text or '€' in text or '£' in text,
    }
    return features


def compute_module_scores(text, features, phishing_prob):
    """
    Compute per-module risk scores for the multi-modular diagnostics panel.
    Returns scores between 0 and 1 for each module.
    """
    text_lower = text.lower()

    # Module 1: Content Analysis — keyword-based heuristics
    urgent_count = sum(1 for w in ['urgent', 'immediate', 'act now', 'limited time', 'expires', 'hurry', 'final notice', 'last chance'] if w in text_lower)
    suspicious_count = sum(1 for w in ['verify', 'confirm', 'suspended', 'locked', 'click here', 'click below', 'update your', 'security alert', 'reset password'] if w in text_lower)
    prize_count = sum(1 for w in ['winner', 'won', 'prize', 'congratulations', 'claim', 'reward', 'free', 'gift', 'lottery'] if w in text_lower)
    content_score = min(1.0, (urgent_count * 0.15 + suspicious_count * 0.12 + prize_count * 0.1))
    content_score = max(content_score, phishing_prob * 0.6)

    # Module 2: URL Reputation
    urls = extract_urls(text)
    url_risk = 0
    for url in urls:
        if any(s in url for s in ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']):
            url_risk += 0.3
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            url_risk += 0.4
        if any(s in url for s in ['-login', 'secure-', 'verify-', 'account-', 'update-', 'confirm-']):
            url_risk += 0.25
        if len(url) > 80:
            url_risk += 0.15
    url_score = min(1.0, url_risk + (0.1 if len(urls) > 3 else 0))
    url_score = max(url_score, phishing_prob * 0.4)

    # Module 3: Header Security (heuristic from content since we don't have real headers)
    header_risk = 0
    if 'noreply' in text_lower or 'no-reply' in text_lower:
        header_risk += 0.1
    if re.search(r'from:.*\b(gmail|yahoo|hotmail)\b.*\b(bank|paypal|apple|microsoft)\b', text_lower):
        header_risk += 0.4
    if 'x-mailer' in text_lower:
        header_risk += 0.05
    header_score = min(1.0, header_risk)
    header_score = max(header_score, phishing_prob * 0.3)

    # Module 4: Attachment Telemetry
    attach_risk = 0
    if any(ext in text_lower for ext in ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.msi']):
        attach_risk += 0.6
    if any(ext in text_lower for ext in ['.zip', '.rar', '.7z']):
        attach_risk += 0.2
    if 'attachment' in text_lower or 'attached' in text_lower:
        attach_risk += 0.05
    attachment_score = min(1.0, attach_risk)
    attachment_score = max(attachment_score, phishing_prob * 0.15)

    # Module 5: Behavioral Profiling
    behavioral_risk = 0
    if features.get('has_urgent'):
        behavioral_risk += 0.25
    if features.get('num_exclamation', 0) > 3:
        behavioral_risk += 0.15
    if features.get('has_money_symbols'):
        behavioral_risk += 0.1
    financial_words = sum(1 for w in ['bank', 'payment', 'credit card', 'paypal', 'wire transfer', 'refund', 'invoice'] if w in text_lower)
    behavioral_risk += financial_words * 0.1
    behavioral_score = min(1.0, behavioral_risk)
    behavioral_score = max(behavioral_score, phishing_prob * 0.5)

    return {
        'content': round(content_score, 4),
        'url': round(url_score, 4),
        'header': round(header_score, 4),
        'attachment': round(attachment_score, 4),
        'behavioral': round(behavioral_score, 4)
    }


def predict_phishing(text, model_type='random_forest'):
    """Predict if text is phishing using specified model."""
    # Transform text using vectorizer
    text_vector = vectorizer.transform([text])
    
    # Select model
    model = random_forest_model if model_type == 'random_forest' else logistic_model
    
    # Make prediction
    prediction = model.predict(text_vector)[0]
    probabilities = model.predict_proba(text_vector)[0]
    
    # Extract features
    features = extract_features(text)
    
    # Phishing probability
    phishing_prob = float(probabilities[1])
    
    # Compute multi-module scores
    modules = compute_module_scores(text, features, phishing_prob)
    
    result = {
        'is_phishing': bool(prediction == 1),
        'confidence': float(probabilities[prediction]),
        'phishing_probability': phishing_prob,
        'legitimate_probability': float(probabilities[0]),
        'risk_level': 'High' if phishing_prob > 0.7 else 'Medium' if phishing_prob > 0.3 else 'Low',
        'model_used': model_type,
        'features': features,
        'modules': modules,
        'timestamp': datetime.now().isoformat()
    }
    
    return result


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/')
def home():
    """Serve the test interface."""
    return send_file(os.path.join(os.path.dirname(__file__), 'test_interface.html'))


@app.route('/popup')
def popup():
    """Serve the popup (extension) interface for testing."""
    return redirect('/frontend/popup.html')


@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve frontend static files (CSS, JS, etc.)."""
    return send_from_directory(FRONTEND_DIR, filename)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'models_loaded': True,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/info', methods=['GET'])
def api_info():
    """API info endpoint."""
    return jsonify({
        'status': 'running',
        'service': 'PhishGuard Detection API',
        'version': '2.1',
        'models_available': ['logistic', 'random_forest'],
        'default_model': DEFAULT_MODEL,
        'endpoints': {
            'POST /predict': 'Analyze email text for phishing',
            'POST /api/scan': 'Analyze email (extension-compatible)',
            'POST /predict/batch': 'Analyze multiple emails',
            'GET /health': 'Check API health',
            'GET /stats': 'Get API statistics',
            'GET /popup': 'Extension popup test page'
        }
    })


@app.route('/api/scan', methods=['POST'])
def api_scan():
    """
    Extension-compatible scan endpoint.
    Accepts email data from the Chrome extension frontend and returns
    results in the format the popup diagnostics panel expects.
    
    Request body:
    {
        "subject": "Email subject",
        "body": "Email body text",
        "sender": "sender@example.com",
        "text": "Full email text (alternative)"
    }
    
    Response:
    {
        "isPhishing": true/false,
        "confidence": 0.0 - 1.0,
        "subject": "...",
        "modules": { "content": ..., "url": ..., ... },
        "risk_level": "High/Medium/Low",
        ...
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Build text from available fields
        text = data.get('text', '')
        if not text:
            subject = data.get('subject', '')
            body = data.get('body', '')
            sender = data.get('sender', '')
            text = f"{subject} {body} {sender}".strip()
        
        if not text:
            return jsonify({'error': 'No text provided for analysis'}), 400
        
        model_type = data.get('model', DEFAULT_MODEL)
        if model_type not in ['logistic', 'random_forest']:
            model_type = DEFAULT_MODEL
        
        # Run prediction
        result = predict_phishing(text, model_type)
        
        # Return in the format the frontend popup.js expects
        return jsonify({
            'isPhishing': result['is_phishing'],
            'confidence': result['phishing_probability'],
            'subject': data.get('subject', 'Unknown'),
            'risk_level': result['risk_level'],
            'model_used': result['model_used'],
            'modules': result['modules'],
            'features': result['features'],
            'phishing_probability': result['phishing_probability'],
            'legitimate_probability': result['legitimate_probability'],
            'timestamp': result['timestamp']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'isPhishing': False,
            'confidence': 0,
            'modules': {'content': 0, 'url': 0, 'header': 0, 'attachment': 0, 'behavioral': 0}
        }), 500


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict if email is phishing.
    
    Request body:
    {
        "text": "Email subject and body text",
        "subject": "Optional: email subject only",
        "body": "Optional: email body only",
        "model": "Optional: 'logistic' or 'random_forest' (default)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract text
        text = data.get('text', '')
        if not text:
            subject = data.get('subject', '')
            body = data.get('body', '')
            text = f"{subject} {body}".strip()
        
        if not text:
            return jsonify({'error': 'No text provided for analysis'}), 400
        
        # Get model preference
        model_type = data.get('model', DEFAULT_MODEL)
        if model_type not in ['logistic', 'random_forest']:
            model_type = DEFAULT_MODEL
        
        # Make prediction
        result = predict_phishing(text, model_type)
        
        return jsonify({
            'success': True,
            'prediction': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Predict multiple emails at once."""
    try:
        data = request.get_json()
        
        if not data or 'emails' not in data:
            return jsonify({'error': 'No emails array provided'}), 400
        
        emails = data.get('emails', [])
        if not isinstance(emails, list):
            return jsonify({'error': 'emails must be an array'}), 400
        
        results = []
        for idx, email in enumerate(emails):
            text = email.get('text', '')
            if not text:
                subject = email.get('subject', '')
                body = email.get('body', '')
                text = f"{subject} {body}".strip()
            
            if text:
                model_type = email.get('model', DEFAULT_MODEL)
                if model_type not in ['logistic', 'random_forest']:
                    model_type = DEFAULT_MODEL
                
                prediction = predict_phishing(text, model_type)
                results.append({
                    'index': idx,
                    'prediction': prediction
                })
            else:
                results.append({
                    'index': idx,
                    'error': 'No text provided'
                })
        
        return jsonify({
            'success': True,
            'total': len(emails),
            'analyzed': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Get API statistics."""
    return jsonify({
        'models': {
            'logistic_regression': {
                'available': True,
                'accuracy': 0.9951,
                'f1_score': 0.9904
            },
            'random_forest': {
                'available': True,
                'accuracy': 0.9962,
                'f1_score': 0.9927
            }
        },
        'default_model': DEFAULT_MODEL,
        'vectorizer': {
            'type': 'TF-IDF',
            'max_features': 5000,
            'ngram_range': '(1, 2)'
        }
    })


@app.route('/test', methods=['GET'])
def test():
    """Test endpoint with sample predictions."""
    test_samples = [
        {
            "description": "Phishing email - Urgent account suspension",
            "text": "URGENT: Your account has been suspended. Click here immediately to restore access: http://suspicious-link.com/restore. Your account will be permanently deleted if you do not verify within 24 hours."
        },
        {
            "description": "Legitimate email - Meeting invitation",
            "text": "Hi team, please review the quarterly report attached. Let's discuss in tomorrow's meeting at 3pm. Thanks, Sarah"
        },
        {
            "description": "Phishing - Prize scam",
            "text": "CONGRATULATIONS! You have been selected as the winner of our $1,000,000 lottery. Click here to claim your prize immediately: http://free-prize-claim.com/winner. Provide your bank details to receive the funds."
        },
        {
            "description": "Legitimate - Project update",
            "text": "Good morning, I've uploaded the latest design mockups to the shared drive. Please review when you get a chance and let me know your thoughts. No rush on this."
        }
    ]
    
    results = []
    for sample in test_samples:
        prediction = predict_phishing(sample['text'], DEFAULT_MODEL)
        results.append({
            'description': sample['description'],
            'text': sample['text'][:120] + '...',
            'prediction': prediction
        })
    
    return jsonify({
        'success': True,
        'test_results': results
    })


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Starting PhishGuard API Server...")
    print("=" * 80)
    print(f"\n  API:           http://localhost:5000")
    print(f"  Test Interface: http://localhost:5000/")
    print(f"  Popup Preview:  http://localhost:5000/popup")
    print(f"  Health Check:   http://localhost:5000/health")
    print(f"  API Scan:       POST http://localhost:5000/api/scan")
    print(f"  Predict:        POST http://localhost:5000/predict")
    print(f"\n" + "=" * 80 + "\n")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
