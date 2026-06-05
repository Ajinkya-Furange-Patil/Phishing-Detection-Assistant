# Phishing Detection Assistant - Browser Extension

A professional browser extension that uses AI to detect phishing emails across Gmail, Outlook, and other webmail platforms.

## Features

- 🛡️ **Real-time Phishing Detection** - AI-powered analysis of emails
- 📧 **Multi-Platform Support** - Works with Gmail, Outlook, Office 365
- 🎯 **5-Module Analysis** - Content, URL, Header, Attachment, Behavioral
- 📊 **Statistics Dashboard** - Track safe emails and threats blocked
- ⚡ **Auto-Scan** - Automatic scanning of opened emails
- 🔔 **Smart Notifications** - Alerts for detected threats
- 🎨 **Professional UI** - Modern, clean interface

## Installation

### For Development

1. **Install Dependencies**
   - Ensure your backend API is running (see main README.md)

2. **Load Extension in Chrome/Edge**
   - Open `chrome://extensions/` (Chrome) or `edge://extensions/` (Edge)
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `frontend` folder

3. **Configure API Endpoint**
   - Click the extension icon
   - Go to Settings
   - Set API Endpoint to your backend URL (default: `http://localhost:5000/api/scan`)

### For Firefox

1. Open `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `manifest.json` from the `frontend` folder

## Usage

### Quick Scan
1. Open an email in Gmail or Outlook
2. Click the extension icon
3. Click "Scan Current Email"
4. View the analysis results

### Auto-Scan
- Enable "Auto-scan emails" in settings
- Extension will automatically analyze emails as you open them

### Context Menu
- Right-click on an email page
- Select "Scan this email for phishing"

## File Structure

```
frontend/
├── manifest.json           # Extension configuration
├── popup.html              # Main popup interface
├── popup.js                # Popup logic
├── background.js           # Background service worker
├── content-gmail.js        # Gmail integration
├── content-outlook.js      # Outlook integration
├── styles/
│   ├── popup.css          # Popup styling
│   └── content.css        # Content script styling
├── icons/                 # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
└── README.md              # This file
```

## How It Works

### 1. Email Extraction
Content scripts extract email data from the webpage:
- Subject line
- Sender information
- Email body text
- Links and URLs
- Attachments metadata
- Email headers

### 2. Backend Analysis
Data is sent to the Python backend API which runs:
- **Module 1**: BERT content analysis
- **Module 2**: URL feature extraction
- **Module 3**: Header verification (SPF/DKIM/DMARC)
- **Module 4**: Attachment analysis
- **Module 5**: Behavioral profiling
- **Meta-Learner**: XGBoost ensemble decision

### 3. Results Display
- Visual warning banners for threats
- Statistics tracking
- Recent scan history
- Confidence scores

## API Response Format

The backend should return:

```json
{
  "isPhishing": true,
  "confidence": 0.96,
  "modules": {
    "content": 0.89,
    "url": 0.94,
    "header": 0.98,
    "attachment": 0.85,
    "behavioral": 0.91
  },
  "threats": [
    "Suspicious URL detected",
    "Failed DMARC authentication",
    "High urgency language"
  ]
}
```

## Settings

### Auto-scan emails
Automatically analyze emails as you open them (requires page reload after enabling)

### Show notifications
Display browser notifications for detected phishing threats

### API Endpoint
URL of your backend phishing detection API
- Default: `http://localhost:5000/api/scan`
- Production: Update to your deployed API URL

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Manifest V3 |
| Edge | ✅ Full | Chromium-based |
| Firefox | ⚠️ Partial | Requires manifest adjustments |
| Safari | ❌ Not yet | Different extension format |

## Security & Privacy

- ✅ **No data storage** - Emails are not stored, only analyzed
- ✅ **Local processing** - All data sent to your own backend
- ✅ **No tracking** - No analytics or user tracking
- ✅ **Minimal permissions** - Only requires access to email domains

## Permissions Explained

- **storage** - Save settings and statistics
- **activeTab** - Read email content from current tab
- **scripting** - Inject content scripts
- **host_permissions** - Access Gmail and Outlook domains

## Troubleshooting

### Extension not detecting emails
- Ensure you're on a supported email platform (Gmail, Outlook)
- Refresh the email page after installing the extension
- Check browser console for errors

### API connection failed
- Verify backend is running (`python app.py`)
- Check API endpoint URL in settings
- Ensure CORS is enabled on backend
- Check browser console for network errors

### No scan results showing
- Open browser DevTools (F12)
- Check Console tab for errors
- Verify email data is being extracted

## Development

### Adding Support for New Email Platforms

1. Create new content script (e.g., `content-yahoo.js`)
2. Implement email extraction for that platform's DOM
3. Add to `manifest.json`:
   ```json
   {
     "matches": ["https://mail.yahoo.com/*"],
     "js": ["content-yahoo.js"],
     "css": ["styles/content.css"]
   }
   ```

### Customizing UI

Edit `styles/popup.css` to change colors, fonts, layout:
- CSS variables in `:root` control theme colors
- Responsive design with flexbox
- Modern gradient backgrounds

### Testing

```bash
# Test backend API
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"subject":"Test","body":"Hello","sender":"test@example.com"}'
```

## Deployment

### Building for Production

1. **Update manifest.json**
   - Change API endpoint to production URL
   - Update version number

2. **Create icons**
   - Generate icons in required sizes (16, 32, 48, 128)
   - Use shield/security themed icons

3. **Package extension**
   - Zip the `frontend` folder
   - Submit to Chrome Web Store / Edge Add-ons

4. **Backend deployment**
   - Deploy Python backend to cloud (AWS, Heroku, etc.)
   - Update API endpoint in extension settings

## Performance

- ⚡ **Fast scanning** - < 2 seconds per email
- 💾 **Lightweight** - < 1MB extension size
- 🔋 **Low CPU usage** - Efficient content scripts

## Future Enhancements

- [ ] Support for more email platforms (Yahoo, ProtonMail)
- [ ] Offline mode with client-side ML models
- [ ] Detailed threat analysis reports
- [ ] Export scan history
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Custom scanning rules

## Contributing

Contributions welcome! Areas to improve:
- Email extraction accuracy
- UI/UX enhancements
- New platform support
- Performance optimization

## License

Part of the Phishing Detection Assistant project.
See main repository for license information.

## Support

For issues or questions:
- Check browser console for errors
- Review backend logs
- Open GitHub issue with error details

## Version History

### v1.0.0 (June 2026)
- Initial release
- Gmail and Outlook support
- 5-module AI detection
- Auto-scan functionality
- Statistics dashboard

---

**Made with ❤️ for Email Security**

*Protecting inboxes, one email at a time* 📧🛡️
