# 🔧 Troubleshooting: Extension Scan Not Working

## Your Issue
Backend is healthy (getting `/health` requests), but when clicking "Scan for Phishing" button, it just shows "Scanning..." and nothing happens.

---

## ✅ Step-by-Step Fix

### Step 1: Update Extension Code (Already Done!)
I've added better error logging to the extension. Now you need to reload it.

### Step 2: Reload Extension
1. Open Chrome
2. Go to `chrome://extensions/`
3. Find "Phishing Detection Assistant"
4. Click the **🔄 Reload** button (circular arrow icon)
5. ✅ Extension updated!

### Step 3: Refresh Gmail
1. Go to your Gmail tab
2. Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac) for hard refresh
3. Wait 2 seconds for the extension to load
4. ✅ Page refreshed!

### Step 4: Open Developer Tools
1. On Gmail page, press `F12` (or right-click → Inspect)
2. Click on the **Console** tab
3. You should see: `Phishing Detection: Gmail content script loaded`
4. ✅ Console ready!

### Step 5: Test Backend (Optional but Recommended)
1. Open `test_backend.html` in Chrome (double-click the file)
2. It will automatically test the `/health` endpoint
3. Click "Test /predict" and "Test /extract-and-analyze"
4. All tests should show ✅ SUCCESS!

### Step 6: Click Scan Button in Gmail
1. Open any email in Gmail
2. Click the **🛡️ Scan for Phishing** button in the toolbar
3. Watch the Console (F12) for messages
4. You should see:
   ```
   🔍 Starting phishing analysis...
   📧 Step 1: Scraping email page...
   ✅ Scraped XXXXX characters
   🌐 Step 2: Sending to backend for analysis...
   📡 Backend response status: 200 OK
   📊 Analysis result: {...}
   ✅ Analysis complete successfully!
   ```

---

## 🐛 Common Errors & Solutions

### Error 1: "Backend not reachable"
**Console shows**: `❌ Backend not reachable. Is Flask running?`

**Solution**:
```bash
# Start backend
cd backend
python app.py

# Should see:
# ✓ TF-IDF Vectorizer loaded
# ✓ Logistic Regression model loaded
# ✓ Random Forest model loaded
# * Running on http://0.0.0.0:5000
```

---

### Error 2: "Could not establish connection. Receiving end does not exist."
**This means**: Content script not loaded

**Solution**:
1. Reload extension at `chrome://extensions/`
2. Hard refresh Gmail (`Ctrl+Shift+R`)
3. Wait 2 seconds
4. Try again

---

### Error 3: CORS Error
**Console shows**: `Access to fetch... has been blocked by CORS policy`

**Solution**: Backend has CORS enabled, but if you see this:
```python
# In backend/app.py, verify this line exists:
CORS(app)  # Enable CORS for browser extension
```

---

### Error 4: "Failed to extract email content"
**Console shows**: `❌ Failed to extract email content from HTML`

**This means**: The HTML scraping worked, but backend couldn't parse it

**Check**:
1. Open email in Gmail (make sure an email is actually open)
2. The backend logs should show:
   ```
   Using fallback extraction...
   ```
3. This is OK! Fallback works fine without Gemini API

---

### Error 5: Nothing happens at all
**No console messages, button stays on "Scanning..."**

**Solution**:
1. Check if button click handler is working:
   ```javascript
   // In Gmail console (F12), type:
   document.getElementById('phishing-scan-btn')
   ```
   Should return: `<button id="phishing-scan-btn">...</button>`
   
2. If it returns `null`, the button wasn't added. Wait 2 more seconds or refresh page.

---

## 🧪 Manual Test Commands

### Test 1: Is content script loaded?
```javascript
// In Gmail console (F12):
console.log('Content script loaded:', typeof analyzeCurrentEmail === 'function');
```
Should show: `Content script loaded: true`

---

### Test 2: Manual scan trigger
```javascript
// In Gmail console (F12):
analyzeCurrentEmail().then(result => {
    console.log('Manual scan result:', result);
    displayAnalysisResults(result);
});
```

---

### Test 3: Check scraping
```javascript
// In Gmail console (F12):
function scrapeEmailPage() {
    const emailView = document.querySelector('[role="main"]') || document.body;
    return {
        emailHTML: emailView.outerHTML,
        pageTitle: document.title,
        url: window.location.href
    };
}

const data = scrapeEmailPage();
console.log('Scraped', data.emailHTML.length, 'characters');
console.log('Title:', data.pageTitle);
```

---

### Test 4: Direct backend call
```javascript
// In Gmail console (F12):
fetch('http://localhost:5000/extract-and-analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        page_html: document.body.innerHTML,
        model: 'random_forest'
    })
})
.then(r => r.json())
.then(result => console.log('Backend response:', result))
.catch(err => console.error('Error:', err));
```

---

## 📋 Checklist

Before asking for help, verify:

- [ ] Backend is running (`python app.py` in `backend/` folder)
- [ ] Backend is accessible (open `http://localhost:5000/health` in browser)
- [ ] Extension is reloaded at `chrome://extensions/`
- [ ] Gmail page is hard-refreshed (`Ctrl+Shift+R`)
- [ ] Console is open (F12) to see error messages
- [ ] An email is actually open in Gmail (not inbox view)
- [ ] `test_backend.html` tests pass (all ✅ SUCCESS)

---

## 🆘 What to Share if Still Stuck

If it's still not working, share:

1. **Console output** when clicking scan:
   ```
   Copy all red error messages from Gmail console (F12)
   ```

2. **Backend logs** (what you see in terminal where `python app.py` is running)

3. **test_backend.html results** (screenshot or copy the results)

4. **Extension background console**:
   - Go to `chrome://extensions/`
   - Click "Inspect views: background page"
   - Copy any error messages

---

## 🎯 Expected Working Flow

When everything works correctly:

1. Click "🛡️ Scan for Phishing" button
2. Button changes to "⏳ Scanning..."
3. Console shows progress messages
4. After 1-3 seconds, animated popup appears on right side
5. Shows risk level, probability, red flags, etc.
6. Button returns to "🛡️ Scan for Phishing"

**If this happens, it's working perfectly!** 🎉
