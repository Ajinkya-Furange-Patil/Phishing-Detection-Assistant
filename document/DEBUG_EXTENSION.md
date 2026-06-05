# Extension Debugging Guide

## Problem: Scan button shows "Scanning..." but nothing loads

Your backend is running (health checks working), but the scan isn't completing. Let's debug step by step.

## Step 1: Check Browser Console

1. Open Gmail in Chrome
2. Press `F12` to open Developer Tools
3. Go to the **Console** tab
4. Click the **Scan for Phishing** button
5. Look for error messages

### What to look for:
- ❌ **CORS errors** - "has been blocked by CORS policy"
- ❌ **Network errors** - "Failed to fetch" or "net::ERR_CONNECTION_REFUSED"
- ❌ **JavaScript errors** - Any red error messages
- ✅ **Success messages** - "Scraping email page...", "Sending to backend for analysis...", "Analysis complete:"

## Step 2: Check Network Tab

1. In Developer Tools, go to **Network** tab
2. Click the **Scan for Phishing** button
3. Look for the request to `http://localhost:5000/extract-and-analyze`

### What to check:
- Does the request appear? (If NO, JavaScript error is blocking it)
- What's the status code? (Should be 200, if 400/500 there's an error)
- Click on the request and check the **Response** tab to see what the backend returned

## Step 3: Check Extension Console

1. Go to `chrome://extensions/`
2. Find "Phishing Detection Assistant"
3. Click **Details**
4. Click **Inspect views: background page** (opens extension's console)
5. Try scanning again
6. Look for errors in this console

## Step 4: Verify Content Script Loaded

In the Gmail console (F12 while on Gmail), type:
```javascript
chrome.runtime.sendMessage({action: 'test'}, (response) => {
    console.log('Extension communication:', response);
});
```

If you get an error about "Could not establish connection", the content script isn't loaded.

## Common Fixes

### Fix 1: Reload Extension
1. Go to `chrome://extensions/`
2. Find "Phishing Detection Assistant"
3. Click the **Reload** button (circular arrow icon)
4. Refresh Gmail page
5. Try scanning again

### Fix 2: Verify Backend is Running
Open a new terminal and test:
```bash
curl http://localhost:5000/health
```

Should return:
```json
{"models_loaded":true,"status":"healthy","timestamp":"..."}
```

### Fix 3: Check if Port 5000 is Blocked
Try accessing in browser: `http://localhost:5000/health`

If it doesn't load, the backend isn't accessible.

### Fix 4: Test with Simple Email
The issue might be with HTML extraction. Try this in Gmail console:
```javascript
// Test scraping
function scrapeEmailPage() {
    const emailView = document.querySelector('[role="main"]') || document.body;
    return {
        emailHTML: emailView.outerHTML,
        pageTitle: document.title,
        url: window.location.href
    };
}

const data = scrapeEmailPage();
console.log('Scraped data length:', data.emailHTML.length);

// Test backend call
fetch('http://localhost:5000/extract-and-analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        page_html: data.emailHTML,
        model: 'random_forest'
    })
})
.then(r => r.json())
.then(result => console.log('Backend response:', result))
.catch(err => console.error('Backend error:', err));
```

## Step 5: Backend Logs

Check your backend terminal where Flask is running. When you click scan, you should see:
```
Using Gemini API for extraction...
OR
Using fallback extraction...
```

If you see nothing, the request isn't reaching the backend.

---

## Quick Test Script

Run this in Gmail console to test everything:

```javascript
async function testFullWorkflow() {
    console.log('🔍 Testing phishing detection workflow...');
    
    // Test 1: Scraping
    console.log('1️⃣ Testing scraping...');
    const pageHTML = document.body.innerHTML;
    console.log('✅ Scraped', pageHTML.length, 'characters');
    
    // Test 2: Backend connectivity
    console.log('2️⃣ Testing backend...');
    try {
        const healthCheck = await fetch('http://localhost:5000/health');
        const healthData = await healthCheck.json();
        console.log('✅ Backend healthy:', healthData);
    } catch (err) {
        console.error('❌ Backend not reachable:', err.message);
        return;
    }
    
    // Test 3: Analysis
    console.log('3️⃣ Testing analysis...');
    try {
        const response = await fetch('http://localhost:5000/extract-and-analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                page_html: pageHTML,
                model: 'random_forest'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Analysis successful!');
            console.log('📊 Risk Level:', result.analysis.risk_level);
            console.log('📧 Extracted:', result.extracted_email);
        } else {
            console.error('❌ Analysis failed:', result.error);
        }
    } catch (err) {
        console.error('❌ Analysis error:', err.message);
    }
}

testFullWorkflow();
```

---

## What to Report Back

After running the tests above, tell me:
1. What errors appear in the Gmail console?
2. What errors appear in the extension background console?
3. Does the test script work?
4. What do you see in the backend logs when clicking scan?
