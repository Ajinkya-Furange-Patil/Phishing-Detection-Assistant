# Design Document: Email Phishing Detection Pipeline

## Overview

The Email Phishing Detection Pipeline is a browser extension system that provides real-time phishing detection for Gmail and Outlook web clients. The system implements a three-layer architecture: a browser extension frontend for email extraction and result display, a Gemini API integration layer for content normalization, and a Flask backend server hosting a BERT-based machine learning model for phishing classification.

This Phase 1 implementation focuses on a single-module MVP using only content analysis (Module 1) with BERT, establishing the foundational pipeline architecture that can be extended with additional detection modules (URL analysis, header verification, attachment scanning, behavioral analysis) in future phases.

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Extension Layer                   │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Popup UI  │  │   Content    │  │    Background    │   │
│  │ (popup.js) │  │   Scripts    │  │  Service Worker  │   │
│  │            │  │ (Gmail/      │  │  (background.js) │   │
│  │            │  │  Outlook)    │  │                  │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
│         │                │                    │             │
│         └────────────────┴────────────────────┘             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ HTTP/JSON
                          │
         ┌────────────────┴────────────────┐
         │                                  │
         ▼                                  ▼
┌──────────────────┐              ┌─────────────────┐
│   Gemini API     │              │  Flask Backend  │
│   (Formatting)   │◄─────────────│     Server      │
│                  │              │  (localhost:    │
│  - HTML Strip    │              │   5000)         │
│  - Normalize     │              │                 │
│  - Structure     │              │  ┌───────────┐  │
└──────────────────┘              │  │   BERT    │  │
                                  │  │   Model   │  │
                                  │  │  (Module  │  │
                                  │  │     1)    │  │
                                  │  └───────────┘  │
                                  └─────────────────┘
```

### Component Responsibilities

1. **Content Scripts** (`content-gmail.js`, `content-outlook.js`)
   - Extract email data from DOM structures
   - Display detection results as visual banners
   - Platform-specific DOM traversal logic

2. **Background Service Worker** (`background.js`)
   - Coordinate communication between popup and content scripts
   - Manage extension lifecycle and statistics
   - Handle badge updates and notifications

3. **Popup Interface** (`popup.js`, `popup.html`)
   - User-facing control panel
   - Manual scan triggering
   - Statistics display and settings management

4. **Gemini API Integration Layer**
   - HTML tag removal and text normalization
   - Content structuring into standardized JSON schema
   - Suspicious pattern highlighting
   - Fallback to basic cleaning on API failure

5. **Flask Backend Server**
   - BERT model hosting and inference execution
   - Request validation and CORS handling
   - Response formatting with phishing classification

6. **BERT Model (Module 1)**
   - Content-based phishing detection
   - Trained on final_unique_sample_25.csv dataset
   - Text tokenization and forward pass inference

## Data Models

### Email Data Structure (ExtractedEmail)

```python
{
    "subject": str,           # Email subject line
    "sender": str,            # Sender email address
    "body": str,              # Complete email body text
    "links": List[str],       # All URLs found in email
    "headers": {              # Email headers
        "from": str,
        "to": str,
        "date": str
    },
    "attachments": [          # Attachment metadata
        {
            "name": str,
            "size": str
        }
    ],
    "platform": str           # "gmail" or "outlook"
}
```

### Gemini API Request/Response

**Request:**
```python
{
    "raw_email": ExtractedEmail
}
```

**Response:**
```python
{
    "cleaned_subject": str,      # HTML-stripped subject
    "cleaned_body": str,         # Normalized body text
    "suspicious_patterns": [     # Highlighted suspicious text
        {
            "pattern": str,
            "confidence": float
        }
    ],
    "metadata": {
        "platform": str,
        "timestamp": str
    }
}
```

### Backend API Request/Response

**POST /api/scan Request:**
```python
{
    "subject": str,
    "body": str,
    "sender": str,
    "links": List[str],
    "headers": dict,
    "attachments": List[dict],
    "platform": str
}
```

**POST /api/scan Response:**
```python
{
    "isPhishing": bool,           # Classification result
    "confidence": float,          # Score in [0.0, 1.0]
    "module_scores": {            # Phase 1: only content
        "content": float
    },
    "threats": List[str]          # Human-readable threat descriptions
}
```

**GET /api/health Response:**
```python
{
    "status": str,                # "healthy" or "unhealthy"
    "message": str,
    "model_loaded": bool
}
```

### Browser Storage Schema

**chrome.storage.sync (Settings):**
```python
{
    "settings": {
        "autoScan": bool,
        "showNotifications": bool,
        "apiEndpoint": str
    }
}
```

**chrome.storage.local (Statistics):**
```python
{
    "stats": {
        "safe": int,
        "threats": int
    },
    "recentScans": [
        {
            "subject": str,
            "isPhishing": bool,
            "confidence": float,
            "timestamp": int
        }
    ]
}
```

## Components and Interfaces

This section defines the key components and their interfaces for the Email Phishing Detection Pipeline.

### EmailExtractor Interface

```typescript
interface EmailExtractor {
    /**
     * Extracts email data from the current DOM
     * @returns Extracted email data or null on failure
     */
    extractEmailData(): ExtractedEmail | null;
    
    /**
     * Displays a detection result banner in the email interface
     * @param result Detection result from backend
     */
    displayBanner(result: DetectionResult): void;
    
    /**
     * Removes any existing detection banners
     */
    clearBanner(): void;
}
```

### GeminiAPIClient Interface

```typescript
interface GeminiAPIClient {
    /**
     * Formats and normalizes extracted email data
     * @param emailData Raw extracted email
     * @returns Formatted email data
     * @throws APIError if request fails after retries
     */
    async formatEmail(emailData: ExtractedEmail): Promise<FormattedEmail>;
    
    /**
     * Applies basic text cleaning as fallback
     * @param emailData Raw extracted email
     * @returns Minimally cleaned email data
     */
    fallbackClean(emailData: ExtractedEmail): FormattedEmail;
}
```

### BackendAPIClient Interface

```typescript
interface BackendAPIClient {
    /**
     * Sends formatted email to backend for inference
     * @param emailData Formatted email data
     * @returns Detection result with classification
     * @throws NetworkError if backend unreachable
     */
    async scanEmail(emailData: FormattedEmail): Promise<DetectionResult>;
    
    /**
     * Checks backend server health
     * @returns Health status
     */
    async healthCheck(): Promise<HealthStatus>;
}
```

### BERTModel Interface

```python
class BERTModel:
    """BERT-based phishing content classifier"""
    
    def __init__(self, model_path: str):
        """Loads trained BERT model from disk"""
        pass
    
    def tokenize(self, text: str) -> torch.Tensor:
        """
        Tokenizes input text using BERT tokenizer
        
        Args:
            text: Input text to tokenize
            
        Returns:
            Tokenized tensor with max_length=512
        """
        pass
    
    def predict(self, tokens: torch.Tensor) -> float:
        """
        Performs inference on tokenized input
        
        Args:
            tokens: Tokenized input tensor
            
        Returns:
            Phishing probability score in [0.0, 1.0]
        """
        pass
```

## Data Flow

### End-to-End Workflow

```
1. User opens email in Gmail/Outlook
   │
   ├─► Content script detects email view
   │
2. User clicks "Scan Email" in popup
   │
   ├─► popup.js sends message to content script
   │
3. Content script extracts email data
   │
   ├─► extractGmailEmailData() / extractOutlookEmailData()
   │   └─► Returns ExtractedEmail object
   │
4. Data sent to background service worker
   │
   ├─► background.js receives extraction
   │
5. Background worker calls Gemini API
   │
   ├─► GeminiAPIClient.formatEmail()
   │   ├─► Success: Returns FormattedEmail
   │   └─► Failure (3 retries): Falls back to basic cleaning
   │
6. Formatted data sent to Flask backend
   │
   ├─► POST http://localhost:5000/api/scan
   │
7. Backend validates request
   │
   ├─► Check required fields present
   │   ├─► Missing fields: Return HTTP 400
   │   └─► Valid: Continue to inference
   │
8. BERT model performs inference
   │
   ├─► BERTModel.tokenize(subject + body)
   ├─► BERTModel.predict(tokens)
   └─► Returns confidence score in [0.0, 1.0]
   │
9. Backend classifies email
   │
   ├─► isPhishing = (confidence > 0.5)
   └─► Returns DetectionResult
   │
10. Response sent to extension
    │
    ├─► Background worker receives result
    ├─► Updates statistics in chrome.storage.local
    └─► Sends result to content script
    │
11. Content script displays banner
    │
    ├─► Red warning if isPhishing == true
    ├─► Green safe if isPhishing == false
    └─► Confidence displayed as percentage
```

## Error Handling

The system implements comprehensive error handling at each layer to ensure graceful degradation and user-friendly error messages.

### Error Handling Flow

```
┌─────────────────────────────────────────┐
│  Extraction Fails                       │
│  ├─► Log error to console              │
│  └─► Display "Unable to extract email" │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Gemini API Unavailable                 │
│  ├─► Retry 3 times (exponential)       │
│  ├─► Fall back to basic text cleaning  │
│  └─► Continue with inference            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Backend Server Offline                 │
│  ├─► NetworkError caught                │
│  └─► Display "Backend unavailable"      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Inference Timeout (>5s)                │
│  ├─► Backend returns HTTP 500           │
│  └─► Display "Scan timeout" error       │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Network Request Fails                  │
│  ├─► Retry once                         │
│  ├─► If still fails: Show error         │
│  └─► Allow manual retry                 │
└─────────────────────────────────────────┘
```

### Error Types and Responses

**ExtractionError**: Returned when email data cannot be extracted from DOM
- User Message: "Unable to extract email data"
- Action: Return null, log error
- Recovery: Allow manual retry

**APIError**: Gemini API failures
- User Message: None (transparent fallback)
- Action: Fall back to basic text cleaning
- Recovery: Continue with inference

**NetworkError**: Backend unreachable
- User Message: "Phishing detection unavailable - please start the backend server"
- Action: Display error banner
- Recovery: Allow manual retry, check backend health

**TimeoutError**: Inference takes > 5 seconds
- User Message: "Scan timeout"
- Action: Return HTTP 500
- Recovery: Allow retry with shorter input

**ValidationError**: Missing required fields
- User Message: "Invalid request format"
- Action: Return HTTP 400
- Recovery: None (developer error)

## Implementation Details

### Email Extraction Logic

**Gmail DOM Selectors:**
```javascript
const GMAIL_SELECTORS = {
    subject: ['h2.hP', '[data-legacy-thread-id] h2'],
    sender: ['span.gD[email]', 'span.go'],
    body: ['div.a3s.aiL', '.gs .ii.gt'],
    links: 'div.a3s.aiL a, .gs .ii.gt a',
    attachments: 'div.aZo'
};
```

**Outlook DOM Selectors:**
```javascript
const OUTLOOK_SELECTORS = {
    subject: '[role="heading"]',
    sender: '[aria-label*="From"]',
    body: '[role="document"]',
    links: '[role="document"] a',
    attachments: '[aria-label*="Attachment"]'
};
```

### BERT Model Training Configuration

```python
# Training hyperparameters
BERT_CONFIG = {
    "model_name": "bert-base-uncased",
    "max_length": 512,
    "learning_rate": 2e-5,
    "batch_size": 16,
    "epochs": 3,
    "train_split": 0.8,
    "val_split": 0.1,
    "test_split": 0.1,
    "stratify": True,
    "random_seed": 42
}

# Dataset
DATASET_PATH = "datasets/combine dataset/final_unique_sample_25.csv"
```

### Gemini API Integration

```python
# Gemini API configuration
GEMINI_CONFIG = {
    "model": "gemini-pro",
    "max_retries": 3,
    "retry_backoff": [1, 2, 4],  # seconds
    "timeout": 2,  # seconds
    "api_key_storage": "chrome.storage.sync.gemini_api_key"
}

# Request structure
def format_gemini_request(email_data):
    prompt = f"""
    Extract and normalize the following email content.
    Remove all HTML tags and format as clean text.
    Identify any suspicious patterns or phishing indicators.
    
    Subject: {email_data['subject']}
    Body: {email_data['body']}
    """
    return {
        "contents": [{"parts": [{"text": prompt}]}]
    }
```

### Backend Flask Application Structure

```python
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from bert_model import BERTModel
import logging

app = Flask(__name__)
CORS(app)

# Global model instance
model = None

@app.before_first_request
def load_model():
    global model
    model = BERTModel("models/bert_phishing_detector.pth")
    logging.info("BERT model loaded successfully")

@app.route('/api/scan', methods=['POST'])
def scan_email():
    # Validate request
    data = request.get_json()
    required_fields = ['subject', 'body', 'sender']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Prepare input
    text = f"{data['subject']} {data['body']}"
    
    # Inference
    try:
        confidence = model.predict(text)
        is_phishing = confidence > 0.5
        
        return jsonify({
            "isPhishing": is_phishing,
            "confidence": float(confidence),
            "module_scores": {
                "content": float(confidence)
            },
            "threats": []
        }), 200
    except Exception as e:
        logging.error(f"Inference error: {str(e)}")
        return jsonify({"error": "Inference failed"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Backend running",
        "model_loaded": model is not None
    }), 200
```

### Browser Extension Message Protocol

```javascript
// Message types
const MessageTypes = {
    // Popup -> Content Script
    EXTRACT_EMAIL: 'extractEmail',
    
    // Content Script -> Popup
    EMAIL_EXTRACTED: 'emailExtracted',
    
    // Popup -> Background
    ANALYZE_EMAIL: 'analyzeEmail',
    
    // Background -> Content Script
    SHOW_RESULT: 'showWarning',
    
    // Any -> Background
    GET_STATS: 'getStats'
};

// Example message flow
// 1. Popup sends to content script
chrome.tabs.sendMessage(tabId, {
    action: MessageTypes.EXTRACT_EMAIL
});

// 2. Content script responds
sendResponse({
    action: MessageTypes.EMAIL_EXTRACTED,
    emailData: extractedEmail
});

// 3. Popup sends to background
chrome.runtime.sendMessage({
    action: MessageTypes.ANALYZE_EMAIL,
    emailData: emailData
});

// 4. Background sends to content script
chrome.tabs.sendMessage(tabId, {
    action: MessageTypes.SHOW_RESULT,
    result: detectionResult
});
```

## Cross-Browser Compatibility

### Manifest Configuration

**Chrome (Manifest V3):**
```json
{
    "manifest_version": 3,
    "background": {
        "service_worker": "background.js"
    },
    "action": {
        "default_popup": "popup.html"
    }
}
```

**Firefox (Manifest V2 Compatibility):**
```json
{
    "manifest_version": 2,
    "background": {
        "scripts": ["background.js"]
    },
    "browser_action": {
        "default_popup": "popup.html"
    }
}
```

### API Compatibility Layer

```javascript
// browser-compat.js
const browser = window.browser || window.chrome;

// Storage API normalization
const storage = {
    sync: {
        get: (keys) => browser.storage.sync.get(keys),
        set: (data) => browser.storage.sync.set(data)
    },
    local: {
        get: (keys) => browser.storage.local.get(keys),
        set: (data) => browser.storage.local.set(data)
    }
};

// Messaging API normalization
const messaging = {
    sendMessage: (message, callback) => {
        if (typeof browser.runtime.sendMessage === 'function') {
            return browser.runtime.sendMessage(message, callback);
        }
    },
    sendTabMessage: (tabId, message, callback) => {
        return browser.tabs.sendMessage(tabId, message, callback);
    }
};
```

## Security Considerations

### API Key Storage

```javascript
// Secure storage of Gemini API key
async function storeAPIKey(apiKey) {
    await chrome.storage.sync.set({
        gemini_api_key: apiKey
    });
}

async function getAPIKey() {
    const result = await chrome.storage.sync.get(['gemini_api_key']);
    return result.gemini_api_key;
}
```

### Content Security Policy

```json
{
    "content_security_policy": {
        "extension_pages": "script-src 'self'; object-src 'self'"
    }
}
```

### CORS Configuration

```python
# Flask CORS setup
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "chrome-extension://*",
            "moz-extension://*"
        ],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

## Performance Optimization

### Model Loading Strategy

```python
# Lazy loading with caching
class BERTModel:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self):
        if self._model is None:
            self._model = torch.load("models/bert_model.pth")
            self._model.eval()
```

### Request Debouncing

```javascript
// Debounce scan requests to prevent rapid-fire API calls
let scanTimeout = null;

function debouncedScan(emailData, delay = 500) {
    clearTimeout(scanTimeout);
    scanTimeout = setTimeout(() => {
        performScan(emailData);
    }, delay);
}
```

### Caching Strategy

```javascript
// Cache recent scan results by email hash
const scanCache = new Map();

function getCachedResult(emailHash) {
    const cached = scanCache.get(emailHash);
    if (cached && Date.now() - cached.timestamp < 300000) { // 5 min TTL
        return cached.result;
    }
    return null;
}

function cacheResult(emailHash, result) {
    scanCache.set(emailHash, {
        result: result,
        timestamp: Date.now()
    });
}
```

## Testing Strategy

### Unit Testing

**Frontend Components:**
- Email extraction functions with mock DOM structures
- Message passing between components
- Storage operations
- UI rendering logic

**Backend Components:**
- Request validation
- Model tokenization
- Response formatting
- Error handling

### Integration Testing

**Full Pipeline:**
- End-to-end workflow from extraction to display
- Gemini API integration with mocks
- Backend API integration
- Cross-browser compatibility

**Error Scenarios:**
- Extraction failures
- API unavailability
- Network errors
- Timeout handling

### Property-Based Testing

Property-based tests will validate universal properties across many randomized inputs. Each property test must run a minimum of 100 iterations and reference its design document property number.

**Frontend Properties:**
- Email extraction preserves data integrity
- Banner rendering matches detection result
- Error messages are never exposed to users

**Backend Properties:**
- Inference output is always in [0.0, 1.0] range
- Classification matches threshold rule
- Response structure contains required fields

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Email Extraction Structure Validity

*For any* successful email extraction from Gmail or Outlook, the returned object SHALL be valid JSON containing all required fields (subject, sender, body, links, headers, attachments, platform) with correct types.

**Validates: Requirements 1.1-1.12, 1.14**

### Property 2: Extraction Error Handling

*For any* email extraction failure, the system SHALL return null and log an error message without throwing an exception.

**Validates: Requirements 1.13**

### Property 3: Gemini API HTML Normalization

*For any* email body containing HTML tags, the Gemini API formatting SHALL return text with all HTML tags removed.

**Validates: Requirements 3.2**

### Property 4: Gemini API Schema Conformance

*For any* valid input to Gemini API formatting, the response SHALL conform to the FormattedEmail JSON schema with cleaned_subject, cleaned_body, suspicious_patterns, and metadata fields.

**Validates: Requirements 3.3, 3.9**

### Property 5: BERT Tokenization Length Constraint

*For any* input text, BERT tokenization SHALL produce tokens with length not exceeding 512 tokens.

**Validates: Requirements 4.3, 4.7**

### Property 6: BERT Output Range Invariant

*For any* tokenized input, BERT model inference SHALL output a confidence score in the range [0.0, 1.0].

**Validates: Requirements 4.5**

### Property 7: Inference Response Structure

*For any* successful BERT inference, the Backend_Server response SHALL contain isPhishing (boolean), confidence (float), and module_scores (dict) fields.

**Validates: Requirements 4.9**

### Property 8: Backend Request Validation

*For any* POST request to /api/scan missing required fields (subject, body, or sender), the Backend_Server SHALL return HTTP 400 with an error message.

**Validates: Requirements 5.7, 5.8**

### Property 9: Backend Success Response

*For any* valid POST request to /api/scan with all required fields, the Backend_Server SHALL return HTTP 200 with detection results.

**Validates: Requirements 5.9**

### Property 10: Phase 1 Module Exclusivity

*For any* email data received in Phase 1, the Inference_Pipeline SHALL send only subject and body fields to the BERT_Model, excluding URL, header, attachment, and behavioral data.

**Validates: Requirements 6.6**

### Property 11: Phase 1 Response Module Constraint

*For any* Detection_Result in Phase 1, the response SHALL contain only the content module score and SHALL NOT include scores for modules 2-5 (URL, header, attachment, behavioral).

**Validates: Requirements 6.7, 6.8**

### Property 12: Classification Threshold Rule

*For any* BERT confidence score, the isPhishing classification SHALL equal true if and only if the confidence score exceeds 0.5.

**Validates: Requirements 6.9**

### Property 13: Phishing Banner Display Rule

*For any* detection result where isPhishing is true, the Extension SHALL display a red warning banner in the email interface.

**Validates: Requirements 7.8**

### Property 14: Safe Banner Display Rule

*For any* detection result where isPhishing is false, the Extension SHALL display a green safe banner in the email interface.

**Validates: Requirements 7.9**

### Property 15: Confidence Score Display Format

*For any* detection result confidence score, the Extension SHALL display the score as a percentage (confidence * 100) in the result banner.

**Validates: Requirements 7.10**

### Property 16: Error Message Privacy

*For any* error that occurs in the Extension, the user interface SHALL NOT display internal error details, stack traces, or system information.

**Validates: Requirements 10.9**

## Future Expansion

### Multi-Module Architecture (Phase 2+)

```python
# Future multi-module inference
class MultiModuleDetector:
    def __init__(self):
        self.module1 = BERTModel()      # Content analysis
        self.module2 = URLAnalyzer()    # URL features
        self.module3 = HeaderVerifier() # SPF/DKIM/DMARC
        self.module4 = AttachmentScanner() # File analysis
        self.module5 = BehavioralAnalyzer() # Psychological triggers
        self.meta_learner = XGBoostModel() # Combines all modules
    
    def predict(self, email_data):
        scores = {
            "content": self.module1.predict(email_data),
            "url": self.module2.predict(email_data),
            "header": self.module3.predict(email_data),
            "attachment": self.module4.predict(email_data),
            "behavioral": self.module5.predict(email_data)
        }
        
        # Meta-learner combines module scores
        final_score = self.meta_learner.predict(scores)
        return final_score, scores
```

### API Response Evolution

```python
# Phase 1 response (current)
{
    "isPhishing": bool,
    "confidence": float,
    "module_scores": {
        "content": float
    },
    "threats": []
}

# Phase 2+ response (future)
{
    "isPhishing": bool,
    "confidence": float,
    "module_scores": {
        "content": float,
        "url": float,
        "header": float,
        "attachment": float,
        "behavioral": float
    },
    "threats": [
        {
            "type": str,
            "severity": str,
            "description": str,
            "module": str
        }
    ],
    "details": {
        "suspicious_urls": [],
        "header_authentication": {},
        "risky_attachments": [],
        "psychological_triggers": []
    }
}
```

## Deployment

### Development Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Train BERT model
python train_bert.py --dataset datasets/combine\ dataset/final_unique_sample_25.csv

# 3. Start Flask backend
python app.py

# 4. Load extension in Chrome
# Navigate to chrome://extensions/
# Enable Developer Mode
# Click "Load unpacked"
# Select frontend/ directory

# 5. Configure API endpoint
# Click extension icon
# Set API endpoint to http://localhost:5000/api/scan
```

### Production Deployment Considerations

- **Backend Hosting**: Deploy Flask server to cloud platform (AWS, GCP, Azure)
- **Model Serving**: Use TensorFlow Serving or TorchServe for production inference
- **API Gateway**: Add authentication and rate limiting
- **HTTPS**: Enable SSL/TLS for API endpoints
- **Monitoring**: Implement logging and performance monitoring
- **Auto-scaling**: Configure based on request load

