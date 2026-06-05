from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension

# Paths to models
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models', 'saved_models')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
LOGISTIC_MODEL_PATH = os.path.join(MODEL_DIR, 'logistic_regression_model.pkl')
RANDOM_FOREST_PATH = os.path.join(MODEL_DIR, 'random_forest_model.pkl')

# Load models at startup
print("=" * 80)
print("PHISHING DETECTION API - Starting Up")
print("=" * 80)

try:
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    print("✓ TF-IDF Vectorizer loaded")
    
    with open(LOGISTIC_MODEL_PATH, 'rb') as f:
        logistic_model = pickle.load(f)
    print("✓ Logistic Regression model loaded")
    
    with open(RANDOM_FOREST_PATH, 'rb') as f:
        random_forest_model = pickle.load(f)
    print("✓ Random Forest model loaded")
    
    print("\nModels loaded successfully!")
    print("=" * 80)
    
except Exception as e:
    print(f"✗ Error loading models: {e}")
    print("Please ensure models are trained and saved in the correct location.")
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
    
    result = {
        'is_phishing': bool(prediction == 1),
        'confidence': float(probabilities[prediction]),
        'phishing_probability': float(probabilities[1]),
        'legitimate_probability': float(probabilities[0]),
        'risk_level': 'High' if probabilities[1] > 0.7 else 'Medium' if probabilities[1] > 0.3 else 'Low',
        'model_used': model_type,
        'features': features,
        'timestamp': datetime.now().isoformat()
    }
    
    return result

@app.route('/')
def home():
    """API home endpoint."""
    return jsonify({
        'status': 'running',
        'service': 'Phishing Detection API',
        'version': '1.0',
        'models_available': ['logistic', 'random_forest'],
        'default_model': DEFAULT_MODEL,
        'endpoints': {
            'POST /predict': 'Analyze email text for phishing',
            'POST /predict/batch': 'Analyze multiple emails',
            'GET /health': 'Check API health',
            'GET /stats': 'Get API statistics'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'models_loaded': True,
        'timestamp': datetime.now().isoformat()
    })

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
            # Try to combine subject and body
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
    """
    Predict multiple emails at once.
    
    Request body:
    {
        "emails": [
            {"text": "Email 1 text"},
            {"text": "Email 2 text", "model": "logistic"}
        ]
    }
    """
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
            "text": "URGENT: Your account has been suspended. Click here immediately to restore access: http://suspicious-link.com/restore"
        },
        {
            "description": "Legitimate email - Meeting invitation",
            "text": "Hi team, please review the quarterly report attached. Let's discuss in tomorrow's meeting at 3pm. Thanks, Sarah"
        }
    ]
    
    results = []
    for sample in test_samples:
        prediction = predict_phishing(sample['text'], DEFAULT_MODEL)
        results.append({
            'description': sample['description'],
            'text': sample['text'][:100] + '...',
            'prediction': prediction
        })
    
    return jsonify({
        'success': True,
        'test_results': results
    })

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Starting Flask API Server...")
    print("API will be available at: http://localhost:5000")
    print("=" * 80 + "\n")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
