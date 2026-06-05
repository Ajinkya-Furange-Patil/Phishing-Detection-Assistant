# 🛡️ Phishing Detection Assistant

AI-powered phishing email detection system with browser extension and REST API.

## 📊 Project Status

✅ **Dataset**: 144,513 emails processed and cleaned  
✅ **Models Trained**: 2 ML models with 99%+ accuracy  
✅ **Backend API**: Flask REST API running  
✅ **Frontend**: Browser extension ready  
✅ **Test Interface**: Web-based testing UI  

## 🎯 Performance Metrics

| Model | Accuracy | Precision | Recall | F1 Score | ROC AUC |
|-------|----------|-----------|--------|----------|---------|
| **Random Forest** | **99.62%** | **99.55%** | **98.98%** | **99.27%** | **99.86%** |
| Logistic Regression | 99.51% | 99.39% | 98.68% | 99.04% | 99.84% |

## 📁 Project Structure

```
Phishing Detection Assistant/
├── backend/                    # Flask API server
│   ├── app.py                 # Main API application
│   ├── requirements.txt       # Python dependencies
│   ├── test_interface.html    # Web testing UI
│   └── README.md             # API documentation
│
├── models/                    # ML models and training
│   ├── train_phishing_model.py   # Training script
│   ├── test_model.py             # Model testing
│   ├── saved_models/             # Trained models (.pkl files)
│   └── results/                  # Training results & visualizations
│
├── datasets/                  # Dataset processing
│   └── combine dataset/
│       ├── extract_simple_dataset.py   # Dataset extraction
│       └── simple_dataset.csv          # Processed dataset
│
├── frontend/                  # Browser extension
│   ├── manifest.json         # Extension configuration
│   ├── popup.html/js         # Extension UI
│   ├── background.js         # Background service worker
│   └── content-*.js          # Gmail/Outlook integration
│
└── START_SERVER.bat          # Quick server startup
```

## 🚀 Quick Start

### 1. Start the Backend API

**Option A: Double-click**
```
START_SERVER.bat
```

**Option B: Command line**
```bash
cd backend
python app.py
```

Server will start at: `http://localhost:5000`

### 2. Test the API

**Option A: Web Interface**
- Open `backend/test_interface.html` in your browser
- Enter email text and click "Analyze"

**Option B: PowerShell**
```powershell
$body = @{text="Your email text here"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Option C: Python**
```python
import requests

response = requests.post('http://localhost:5000/predict', json={
    'text': 'URGENT! Click here now!',
    'model': 'random_forest'
})

print(response.json())
```

### 3. Use Browser Extension

1. Open Chrome/Edge and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `frontend` folder
5. Visit Gmail or Outlook
6. Extension will automatically scan emails

## 🔧 API Endpoints

### Health Check
```bash
GET http://localhost:5000/health
```

### Analyze Email
```bash
POST http://localhost:5000/predict
Content-Type: application/json

{
  "text": "Email content here",
  "model": "random_forest"
}
```

### Get Statistics
```bash
GET http://localhost:5000/stats
```

### Test Samples
```bash
GET http://localhost:5000/test
```

## 📦 Dependencies

### Backend
```
Flask >= 3.0.0
flask-cors >= 4.0.0
scikit-learn >= 1.2.0
numpy >= 1.23.0
pandas >= 1.5.0
```

### Models Training
```
matplotlib >= 3.6.0
seaborn >= 0.12.0
```

## 🎓 How It Works

### 1. Data Processing
- Combines multiple phishing datasets
- Extracts subject + body + label
- Cleans and normalizes text
- Result: 144,513 clean samples

### 2. Feature Extraction
- **TF-IDF Vectorization**: Converts text to numerical features
- **5,000 features**: Most important words/phrases
- **Bi-grams**: Captures word pairs (e.g., "click here")
- **Additional features**: URLs, urgency keywords, suspicious words

### 3. Model Training
- **Random Forest**: 100 decision trees, ensemble voting
- **Logistic Regression**: Fast linear classifier
- **Class balancing**: Handles imbalanced data
- **Train/Test split**: 80/20 with stratification

### 4. Prediction
- Text → TF-IDF vector → Model → Probability
- Risk levels: Low (<30%), Medium (30-70%), High (>70%)
- Real-time analysis in <100ms

## 🧪 Testing

### Test Phishing Emails
```python
# Example 1: Account suspension
text = "URGENT! Your account has been suspended. Click here immediately!"

# Example 2: Prize winner
text = "Congratulations! You've won $1,000,000! Claim now!"

# Example 3: Password reset scam
text = "Your password expired. Reset at: http://fake-bank.com/reset"
```

### Test Legitimate Emails
```python
# Example 1: Business meeting
text = "Hi team, quarterly review meeting tomorrow at 3pm. Thanks!"

# Example 2: Invoice
text = "Your invoice #12345 is attached. Payment due in 30 days."
```

## 📊 Model Performance Details

### Confusion Matrix (Random Forest)
```
                Predicted
              Legit  Phishing
Actual Legit   21381     76
      Phishing   76   7370
```

### Key Metrics
- **True Positives**: 7,370 (phishing correctly identified)
- **True Negatives**: 21,381 (legitimate correctly identified)
- **False Positives**: 76 (0.35% - legitimate flagged as phishing)
- **False Negatives**: 76 (1.02% - phishing missed)

## 🎨 Features Analyzed

The model examines:
- ✉️ **Text content**: TF-IDF features from subject/body
- 🔗 **URLs**: Number and patterns
- ⚠️ **Urgent keywords**: "urgent", "immediate", "act now"
- 🚨 **Suspicious words**: "click here", "verify", "suspend"
- 💰 **Money symbols**: $, €, £
- ❗ **Punctuation**: Excessive exclamation/question marks
- 📏 **Text length**: Typical phishing patterns

## 🌐 Browser Extension Features

- ✅ Auto-scans emails in Gmail and Outlook
- 🎯 Real-time phishing detection
- 📊 Dashboard with statistics
- 🔔 Notifications for threats
- 📈 Scan history tracking
- ⚙️ Customizable settings

## 🔒 Security Notes

- All processing happens locally (models run on your machine)
- No email data sent to external servers
- API runs on localhost by default
- CORS enabled for browser extension only

## 🐛 Troubleshooting

### API Won't Start
```
Error: Models not found
```
**Solution**: Train models first
```bash
cd models
python train_phishing_model.py
```

### Extension Not Working
1. Check API is running: `http://localhost:5000/health`
2. Check browser console for errors
3. Ensure extension has permissions for Gmail/Outlook

### Low Accuracy on Your Emails
- Model trained on specific dataset
- May need retraining with your data
- Consider fine-tuning with domain-specific emails

## 📈 Future Enhancements

- [ ] URL reputation checking
- [ ] Attachment analysis
- [ ] Email header analysis (SPF, DKIM, DMARC)
- [ ] Sender reputation scoring
- [ ] Deep learning models (BERT, GPT)
- [ ] Multi-language support
- [ ] Cloud deployment
- [ ] Mobile app
- [ ] Integration with email clients

## 📝 Training Your Own Model

```bash
# 1. Prepare your dataset (CSV with 'text' and 'label' columns)
# 2. Place in datasets/combine dataset/
# 3. Train models
cd models
python train_phishing_model.py

# 4. Models will be saved to saved_models/
# 5. Restart API to load new models
```

## 🤝 Contributing

This is an internship project. Feel free to:
- Report bugs
- Suggest features
- Improve documentation
- Add test cases

## 📄 License

Educational/Internship Project

## 🙏 Acknowledgments

- **Datasets**: Multiple public phishing datasets combined
- **ML Libraries**: scikit-learn, pandas, numpy
- **Web Framework**: Flask
- **Visualization**: matplotlib, seaborn

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation in `backend/README.md`
3. Check model training logs in `models/results/`

---

**Built with ❤️ for Email Security**
