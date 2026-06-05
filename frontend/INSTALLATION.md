# Browser Extension Installation Guide

## Quick Start (5 minutes)

### Step 1: Start the Backend API

1. **Install Flask and dependencies:**
   ```bash
   pip install flask flask-cors
   ```

2. **Run the example API:**
   ```bash
   cd frontend
   python api-example.py
   ```

3. **Verify it's running:**
   Open `http://localhost:5000/api/health` in your browser
   You should see: `{"status": "healthy"}`

### Step 2: Install the Extension

#### For Chrome / Edge

1. Open your browser and go to:
   - **Chrome**: `chrome://extensions/`
   - **Edge**: `edge://extensions/`

2. Enable "Developer mode" (toggle in top-right corner)

3. Click "Load unpacked"

4. Navigate to and select the `frontend` folder

5. The extension icon should appear in your toolbar

#### For Firefox

1. Open `about:debugging#/runtime/this-firefox`

2. Click "Load Temporary Add-on..."

3. Navigate to the `frontend` folder and select `manifest.json`

4. Note: Extension will be removed when Firefox closes (temporary)

### Step 3: Configure the Extension

1. Click the extension icon in your browser toolbar

2. Go to Settings section

3. Verify API Endpoint is set to: `http://localhost:5000/api/scan`

4. Enable "Auto-scan emails" and "Show notifications"

5. Click "Save Settings"

### Step 4: Test It!

1. Open Gmail or Outlook in your browser

2. Open any email

3. Click the extension icon

4. Click "Scan Current Email"

5. View the analysis results

## Detailed Setup

### Creating Extension Icons

The extension needs icons in multiple sizes. You can:

**Option 1: Use online icon generator**
- Go to https://favicon.io/favicon-generator/
- Create a shield/security icon
- Generate and download

**Option 2: Create manually**
Required sizes:
- `icon16.png` (16x16)
- `icon32.png` (32x32)
- `icon48.png` (48x48)
- `icon128.png` (128x128)

Place all icons in `frontend/icons/` folder

### Integrating with Your ML Backend

Replace `api-example.py` with your actual implementation:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import your_ml_models  # Your trained models

app = Flask(__name__)
CORS(app)

@app.route('/api/scan', methods=['POST'])
def scan_email():
    email_data = request.get_json()
    
    # Load your trained models
    bert_model = your_ml_models.load_bert()
    url_model = your_ml_models.load_url_classifier()
    # ... load other models
    
    # Run inference
    content_score = bert_model.predict(email_data['body'])
    url_score = url_model.predict(email_data['links'])
    # ... other predictions
    
    # Meta-learner
    final_prediction = meta_learner.predict([
        content_score, url_score, header_score,
        attachment_score, behavioral_score
    ])
    
    return jsonify({
        "isPhishing": bool(final_prediction),
        "confidence": float(final_prediction),
        "modules": {...}
    })
```

## Platform-Specific Instructions

### Gmail

1. Go to https://mail.google.com
2. Open any email
3. Extension automatically injects detection capabilities
4. Click extension icon to manually scan

### Outlook / Office 365

1. Go to:
   - https://outlook.live.com
   - https://outlook.office365.com
   - https://outlook.office.com

2. Open any email
3. Right-click and select "Scan this email for phishing"
4. Or use extension popup

## Troubleshooting

### Extension not loading

**Problem**: "Manifest version 3 is required"
**Solution**: Update your browser to latest version

**Problem**: "Failed to load extension"
**Solution**: Check all files are in correct locations:
```
frontend/
├── manifest.json ✓
├── popup.html ✓
├── popup.js ✓
├── background.js ✓
├── content-gmail.js ✓
├── content-outlook.js ✓
└── styles/ ✓
```

### API connection errors

**Problem**: "Failed to fetch"
**Solution 1**: Check backend is running
```bash
curl http://localhost:5000/api/health
```

**Solution 2**: Check CORS is enabled in Flask:
```python
from flask_cors import CORS
CORS(app)
```

**Solution 3**: Mixed content (HTTPS/HTTP)
- If testing on HTTPS email site, use HTTPS for API too
- Or use browser flag to allow mixed content (development only)

### Email not being extracted

**Problem**: Extension can't read email content
**Solution**: 
1. Refresh the email page after installing extension
2. Check browser console (F12) for errors
3. Verify content script is injecting:
   - Gmail: Look for console message "Gmail content script loaded"
   - Outlook: Look for "Outlook content script loaded"

### Permissions errors

**Problem**: "Cannot access contents of url"
**Solution**: Add domain to `host_permissions` in `manifest.json`:
```json
"host_permissions": [
  "https://mail.google.com/*",
  "https://your-email-domain.com/*"
]
```

## Advanced Configuration

### Using Remote API

1. Deploy your backend to cloud (AWS, Heroku, etc.)

2. Update API endpoint in extension settings:
   ```
   https://your-api-domain.com/api/scan
   ```

3. Ensure CORS headers allow extension origin

### Custom Warning Styles

Edit `styles/content.css` to customize warning banners:

```css
.phishing-warning-banner.danger {
  background: linear-gradient(135deg, #YOUR_COLOR 0%, #YOUR_COLOR2 100%);
  border: 2px solid #YOUR_BORDER_COLOR;
}
```

### Performance Optimization

**Reduce API calls:**
```javascript
// In content scripts, add debouncing
let scanTimeout;
function debouncedScan() {
  clearTimeout(scanTimeout);
  scanTimeout = setTimeout(() => {
    // Perform scan
  }, 1000);
}
```

**Cache results:**
```javascript
// Store recent scans to avoid re-scanning
const scanCache = new Map();
const emailHash = hashEmail(emailData);
if (scanCache.has(emailHash)) {
  return scanCache.get(emailHash);
}
```

## Security Best Practices

1. **Never log sensitive email content**
   ```python
   # DON'T
   print(f"Scanning email: {email_data}")
   
   # DO
   print(f"Scanning email from {email_data['sender'][:20]}...")
   ```

2. **Use HTTPS in production**
   ```python
   # Production backend should use SSL
   app.run(ssl_context='adhoc')
   ```

3. **Validate input**
   ```python
   from flask import abort
   
   if not email_data.get('body'):
       abort(400, 'Missing email body')
   ```

4. **Rate limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, default_limits=["100 per hour"])
   ```

## Testing Checklist

- [ ] Backend API responds to health check
- [ ] Extension loads without errors
- [ ] Gmail integration works
- [ ] Outlook integration works
- [ ] Warning banners display correctly
- [ ] Statistics update properly
- [ ] Settings save and load
- [ ] Notifications appear (if enabled)
- [ ] Context menu works
- [ ] Badge updates on threats

## Next Steps

1. **Implement full ML pipeline**
   - Train BERT model (Module 1)
   - Train URL classifier (Module 2)
   - Implement header verification (Module 3)
   - Build attachment analyzer (Module 4)
   - Create behavioral profiler (Module 5)
   - Train XGBoost meta-learner

2. **Enhance extension**
   - Add detailed threat reports
   - Implement email whitelist/blacklist
   - Add export functionality
   - Create dashboard page

3. **Deploy to production**
   - Set up cloud backend
   - Get SSL certificate
   - Submit to Chrome Web Store
   - Create promotional materials

## Support

If you encounter issues:

1. Check browser console (F12 → Console)
2. Check backend logs
3. Review this guide's troubleshooting section
4. Open GitHub issue with:
   - Browser and version
   - Error messages
   - Steps to reproduce

---

**Happy phishing hunting! 🎣🛡️**
