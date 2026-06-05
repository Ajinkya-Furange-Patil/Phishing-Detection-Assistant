# 🔌 Browser Extension Installation Guide

## ✅ Fixed Issues
The background.js file has been updated to fix the `chrome.contextMenus` error.

## 📋 Prerequisites
1. ✅ Backend API must be running on `http://localhost:5000`
2. ✅ Chrome, Edge, or Chromium-based browser

## 🚀 Installation Steps

### Step 1: Start the Backend Server
```bash
# Open PowerShell and run:
cd "c:\Users\Ajinkya Patil\OneDrive\Desktop\Internship\Phishing Detection Assistant\backend"
python app.py
```

Or double-click: `START_SERVER.bat`

Wait until you see:
```
✓ TF-IDF Vectorizer loaded
✓ Logistic Regression model loaded
✓ Random Forest model loaded
 * Running on http://127.0.0.1:5000
```

### Step 2: Open Chrome/Edge Extensions Page
1. Open your browser
2. Type in address bar:
   - **Chrome**: `chrome://extensions/`
   - **Edge**: `edge://extensions/`
3. Press Enter

### Step 3: Enable Developer Mode
1. Look for **"Developer mode"** toggle in the top-right corner
2. **Turn it ON** (slide the toggle to the right)

### Step 4: Load the Extension
1. Click **"Load unpacked"** button (top-left area)
2. Navigate to:
   ```
   c:\Users\Ajinkya Patil\OneDrive\Desktop\Internship\Phishing Detection Assistant\frontend
   ```
3. Select the **`frontend`** folder
4. Click **"Select Folder"**

### Step 5: Verify Installation
You should see:
- ✅ **Phishing Detection Assistant** card in extensions list
- ✅ Shield icon in your browser toolbar
- ✅ No errors displayed

If you see errors:
- Click **"Errors"** button to view details
- Most common: "Service worker registration failed" - This is usually temporary, try reloading
- Click the **refresh icon** on the extension card

### Step 6: Pin the Extension (Optional)
1. Click the **puzzle piece icon** 🧩 in browser toolbar
2. Find **"Phishing Detection Assistant"**
3. Click the **pin icon** 📌 next to it
4. Icon will now appear in toolbar

## 🧪 Test the Extension

### Test 1: Check Extension Popup
1. Click the extension icon in toolbar
2. You should see:
   - Statistics (Safe/Threats)
   - Status indicator
   - Scan button
   - Settings

### Test 2: Open Gmail/Outlook
1. Go to https://mail.google.com or https://outlook.com
2. Open any email
3. Right-click on the page
4. You should see: **"Scan this email for phishing"** in context menu

### Test 3: Manual Scan
1. Click the extension icon
2. The popup should show stats
3. API status should show "Connected" or "Online"

## 🐛 Troubleshooting

### Error: "Service worker registration failed"
**Solution**: 
1. Go to `chrome://extensions/`
2. Find "Phishing Detection Assistant"
3. Click the **refresh icon** (circular arrow)
4. If still fails, click **"Remove"** and re-install (Step 4)

### Error: "contextMenus is not defined"
**Solution**: The background.js has been fixed. Re-install the extension:
1. Remove the extension
2. Reload the extension folder (Step 4)

### Error: "Failed to connect to API"
**Solution**:
1. Make sure backend server is running
2. Test API: Open browser and go to `http://localhost:5000/health`
3. Should see: `{"status": "healthy"}`
4. If not working, restart the backend server

### Extension Icon Not Showing
**Solution**:
1. Check if icons folder exists in frontend/
2. Verify icon files: icon16.png, icon32.png, icon48.png, icon128.png
3. Reload the extension

### Context Menu Not Appearing
**Solution**:
1. Make sure you're on Gmail or Outlook website
2. The context menu only works on:
   - https://mail.google.com/*
   - https://outlook.live.com/*
   - https://outlook.office365.com/*
   - https://outlook.office.com/*

### API Not Responding
**Solution**:
1. Check if backend is running:
   ```powershell
   Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing
   ```
2. Should return: `{"status": "healthy"}`
3. If not, restart backend server

### "Manifest version 3" errors
**Solution**: The manifest.json is already configured for V3. If errors persist:
1. Make sure you're using Chrome 88+ or Edge 88+
2. Update your browser to the latest version

## 📊 Verifying It Works

### Method 1: Use Test Interface
1. Keep backend running
2. Open `backend/test_interface.html` in browser
3. Paste email text and click "Analyze"
4. Should see prediction results

### Method 2: Use PowerShell
```powershell
$body = @{text="URGENT! Your account is suspended!"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5000/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

### Method 3: Check Extension Popup
1. Click extension icon
2. Should show:
   - Safe: 0
   - Threats: 0
   - Status: Connected/Online

## 🎯 Using the Extension

### Scan Email in Gmail
1. Open Gmail
2. Click on an email to open it
3. **Option A**: Click extension icon → Click "Scan Current Email"
4. **Option B**: Right-click on page → "Scan this email for phishing"
5. Results will appear in notification or popup

### Scan Email in Outlook
1. Open Outlook
2. Click on an email
3. Same process as Gmail

### View Statistics
1. Click extension icon
2. View scan history
3. See total safe vs threats detected

## 🔒 Permissions Explained

The extension requests:
- **`storage`**: Save settings and scan history locally
- **`notifications`**: Show phishing alerts
- **`contextMenus`**: Add "Scan email" to right-click menu
- **`tabs`**: Read active tab for email scanning
- **`alarms`**: Periodic cleanup of old scans
- **Gmail/Outlook URLs**: Only works on these email sites

**Privacy**: No data is sent to external servers. All processing happens locally via your localhost API.

## ✅ Success Checklist

- [ ] Backend server running (`http://localhost:5000/health` works)
- [ ] Extension loaded without errors
- [ ] Extension icon visible in toolbar
- [ ] Popup opens when clicking icon
- [ ] Context menu appears on Gmail/Outlook
- [ ] API status shows "Connected"

If all checked ✅, you're ready to go! 🎉

## 🆘 Still Having Issues?

1. **Check browser console**:
   - Right-click on extension icon → "Inspect popup"
   - Look for errors in Console tab

2. **Check service worker**:
   - Go to `chrome://extensions/`
   - Click "Service worker" link under extension
   - Check for errors

3. **Restart everything**:
   - Close browser completely
   - Stop backend server (Ctrl+C)
   - Start backend server again
   - Reopen browser
   - Reload extension

4. **Clean install**:
   - Remove extension
   - Clear browser cache
   - Restart browser
   - Re-install extension

---

**Need Help?** Check the error console or backend logs for specific error messages.
