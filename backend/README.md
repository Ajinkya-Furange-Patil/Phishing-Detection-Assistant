# Phishing Detection Backend API

Flask-based REST API that serves the trained ML models for phishing email detection.

## Features

- **Dual Model Support**: Logistic Regression and Random Forest models
- **High Accuracy**: 99.62% accuracy with Random Forest
- **RESTful API**: Easy integration with any frontend
- **CORS Enabled**: Works with browser extensions
- **Feature Extraction**: Analyzes URLs, suspicious words, urgency indicators
- **Batch Processing**: Analyze multiple emails at once

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- Flask >= 3.0.0
- flask-cors >= 4.0.0
- scikit-learn >= 1.2.0
- numpy >= 1.23.0
- pandas >= 1.5.0

### 2. Ensure Models Are Trained

The API requires trained models in `../models/saved_models/`:
- `tfidf_vectorizer.pkl`
- `logistic_regression_model.pkl`
- `random_forest_model.pkl`

If models don't exist, train them first:
```bash
cd ../models
python train_phishing_model.py
```

### 3. Start the Server

```bash
python app.py
```

Server will start at: `http://localhost:5000`

## API Endpoints

### 1. **GET /** - API Information
Get API status and available endpoints.

**Response:**
```json
{
  "status": "running",
  "service": "Phishing Detection API",
  "version": "1.0",
  "models_available": ["logistic", "random_forest"],
  "default_model": "random_forest"
}
```

### 2. **GET /health** - Health Check
Check if API is running and models are loaded.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. **POST /predict** - Analyze Single Email
Analyze an email for phishing.

**Request:**
```json
{
  "text": "Email subject and body combined",
  "subject": "Optional: just the subject",
  "body": "Optional: just the body",
  "model": "random_forest"
}
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "is_phishing": false,
    "confidence": 0.9823,
    "phishing_probability": 0.0177,
    "legitimate_probability": 0.9823,
    "risk_level": "Low",
    "model_used": "random_forest",
    "features": {
      "num_urls": 1,
      "num_exclamation": 0,
      "has_urgent": false,
      "has_suspicious_words": false
    },
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### 4. **POST /predict/batch** - Analyze Multiple Emails
Analyze multiple emails in one request.

**Request:**
```json
{
  "emails": [
    {"text": "Email 1 text"},
    {"text": "Email 2 text", "model": "logistic"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "total": 2,
  "analyzed": 2,
  "results": [
    {
      "index": 0,
      "prediction": { /* prediction object */ }
    },
    {
      "index": 1,
      "prediction": { /* prediction object */ }
    }
  ]
}
```

### 5. **GET /stats** - Model Statistics
Get information about the models.

**Response:**
```json
{
  "models": {
    "logistic_regression": {
      "available": true,
      "accuracy": 0.9951,
      "f1_score": 0.9904
    },
    "random_forest": {
      "available": true,
      "accuracy": 0.9962,
      "f1_score": 0.9927
    }
  },
  "default_model": "random_forest"
}
```

### 6. **GET /test** - Test Endpoint
Run quick tests with sample emails.

## Usage Examples

### Using cURL

```bash
# Test single email
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent Account Verification",
    "body": "Your account will be suspended. Click here immediately!"
  }'

# Check health
curl http://localhost:5000/health

# Get stats
curl http://localhost:5000/stats
```

### Using Python

```python
import requests

# Analyze email
response = requests.post('http://localhost:5000/predict', json={
    'text': 'URGENT: Your account has been suspended!',
    'model': 'random_forest'
})

result = response.json()
print(f"Is Phishing: {result['prediction']['is_phishing']}")
print(f"Confidence: {result['prediction']['confidence']:.2%}")
```

### Using JavaScript (Fetch API)

```javascript
// Analyze email from browser extension
fetch('http://localhost:5000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    subject: emailSubject,
    body: emailBody,
    model: 'random_forest'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Is Phishing:', data.prediction.is_phishing);
  console.log('Confidence:', data.prediction.confidence);
});
```

## Risk Levels

The API categorizes emails into risk levels:

- **Low**: Phishing probability < 30%
- **Medium**: Phishing probability 30% - 70%
- **High**: Phishing probability > 70%

## Model Selection

Two models are available:

1. **Logistic Regression** (`logistic`)
   - Faster prediction time (~0.001s)
   - Accuracy: 99.51%
   - Best for: High-volume processing

2. **Random Forest** (`random_forest`) - **Default**
   - Slightly slower (~0.01s)
   - Accuracy: 99.62%
   - Best for: Maximum accuracy

## Features Analyzed

The API extracts and analyzes:
- Number of URLs in the email
- Presence of urgent/suspicious keywords
- Exclamation and question marks
- Money symbols ($, €, £)
- Text length
- TF-IDF features (5000 features)

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing/invalid data)
- `500`: Server error

Error response format:
```json
{
  "success": false,
  "error": "Error description"
}
```

## Production Deployment

For production use:

1. **Use WSGI Server** (Gunicorn, uWSGI):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Enable HTTPS**
3. **Add Authentication** (API keys, OAuth)
4. **Rate Limiting**
5. **Logging and Monitoring**
6. **Load Balancing** for high traffic

## Troubleshooting

### Models Not Found
```
✗ Error loading models: [Errno 2] No such file or directory
```
**Solution**: Train models first by running `python train_phishing_model.py` in the models directory.

### CORS Errors
If browser extension can't connect, ensure:
- API is running on `localhost:5000`
- CORS is enabled (flask-cors installed)
- Extension has permission for `http://localhost:5000/*`

### Port Already in Use
```
OSError: [Errno 98] Address already in use
```
**Solution**: Change port in `app.py` or kill the process using port 5000.

## License

Part of the Phishing Detection Assistant project.
