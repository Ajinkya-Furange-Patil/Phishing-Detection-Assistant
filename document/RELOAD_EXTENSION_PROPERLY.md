# 🔄 How to Properly Reload Extension

## The Problem
Content script is NOT loading into Gmail. Functions are undefined, button is invisible.

## The Solution: Proper Reload Sequence

Follow these steps **EXACTLY** in this order:

---

### **Step 1: Close ALL Gmail Tabs**
```
1. Close EVERY Gmail tab in Chrome
2. Make sure NO gmail.com tabs are open
3. This is CRITICAL - the old script is stuck in memory
```

---

### **Step 2: Reload Extension**
```
1. Open a NEW tab
2. Go to: chrome://extensions/
3. Find "Phishing Detection Assistant"
4. Click the RELOAD button (🔄 circular arrow)
5. Wait 2 seconds
```

---

### **Step 3: Check for Errors**
```
On chrome://extensions/ page:
1. Look for any RED error messages under the extension
2. If you see errors, click "Errors" to see details
3. Share any errors you see
```

---

### **Step 4: Open Fresh Gmail Tab**
```
1. Open a BRAND NEW tab
2. Go to: https://mail.google.com/
3. Wait for Gmail to fully load
4. Open any email (click on an email to view it)
```

---

### **Step 5: Open Console Immediately**
```
1. Press F12 (or right-click → Inspect)
2. Go to Console tab
3. Look for this message:
   ═══════════════════════════════════════════════════════
   🛡️  PHISHING DETECTION: Gmail content script loaded!
   ═══════════════════════════════════════════════════════
```

---

### **Step 6: Verify Loading**

In the console, type this and press Enter:

```javascript
window.PHISHING_DETECTION_LOADED
```

**Should return:** `true`

**If it returns:** `undefined` → Script NOT loaded, see troubleshooting below

---

### **Step 7: Check Functions**

In the console, type each of these:

```javascript
typeof analyzeCurrentEmail
typeof scrapeEmailPage  
typeof displayAnalysisResults
```

**Each should return:** `"function"`

**If returns:** `"undefined"` → Script has errors, see troubleshooting

---

### **Step 8: Find the Button**

In the console, type:

```javascript
document.getElementById('phishing-scan-btn')
```

**Should return:** `<button id="phishing-scan-btn">...</button>`

**If returns:** `null` → Wait 2 more seconds and try again

---

## ✅ Success Checklist

After following ALL steps above, you should have:

- [ ] All old Gmail tabs closed
- [ ] Extension reloaded at chrome://extensions/
- [ ] Fresh Gmail tab opened
- [ ] Console shows "Gmail content script loaded!" message
- [ ] `window.PHISHING_DETECTION_LOADED` returns `true`
- [ ] All functions return `"function"`
- [ ] Button is found in DOM

---

## 🐛 Troubleshooting

### Issue 1: No "script loaded" message in console

**Cause:** Content script not injecting

**Solutions:**
1. Check chrome://extensions/ for errors (red text)
2. Make sure you're on https://mail.google.com (not http)
3. Try disabling other Gmail extensions temporarily
4. Check manifest.json is valid (no syntax errors)

### Issue 2: "Script loaded" shows but functions undefined

**Cause:** JavaScript error in content-gmail.js

**Solutions:**
1. Look for RED error messages in console
2. Check the error message carefully
3. Share the error with me

### Issue 3: Functions defined but button not found

**Cause:** Button injection timing issue

**Solutions:**
1. Wait 5 seconds after Gmail loads
2. Try scrolling the email
3. Look for the button manually in Gmail toolbar
4. Check console for "addScanButton() called" message

---

## 📸 What to Share if Still Not Working

After following ALL steps above, if it's still not working, share:

1. **Screenshot of chrome://extensions/** showing the extension
2. **Console output** right after opening Gmail (all messages)
3. **Result of these commands in console:**
   ```javascript
   window.PHISHING_DETECTION_LOADED
   typeof analyzeCurrentEmail
   document.getElementById('phishing-scan-btn')
   ```
4. **Any RED error messages** in console

---

## 🎯 Quick Verification Command

Paste this into console after reload:

```javascript
console.log('Verification Check:');
console.log('  Script loaded:', window.PHISHING_DETECTION_LOADED === true ? '✅' : '❌');
console.log('  analyzeCurrentEmail:', typeof analyzeCurrentEmail === 'function' ? '✅' : '❌');
console.log('  scrapeEmailPage:', typeof scrapeEmailPage === 'function' ? '✅' : '❌');
console.log('  displayAnalysisResults:', typeof displayAnalysisResults === 'function' ? '✅' : '❌');
console.log('  Button:', document.getElementById('phishing-scan-btn') ? '✅' : '❌');
```

**All should show ✅**

---

## 💡 Why This Happens

Chrome caches content scripts in memory. When you:
- Modify content-gmail.js
- Reload the extension
- But keep the old Gmail tab open

The OLD script stays in memory and the NEW script doesn't load. **You MUST close all Gmail tabs** before reloading the extension.

---

## ✨ After Successful Reload

Once everything shows ✅, run the full test:

```javascript
analyzeCurrentEmail().then(result => {
    console.log('Test result:', result);
    if (result.success) {
        displayAnalysisResults(result);
    }
});
```

This should:
1. Show progress in console
2. Display animated popup
3. Show risk analysis

🎉 **If this works, your extension is fully functional!**
