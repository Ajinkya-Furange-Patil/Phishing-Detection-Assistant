# 🧪 Console Test Script

## Copy and paste this entire script into Gmail console (F12)

```javascript
console.log('');
console.log('═══════════════════════════════════════════════════════');
console.log('🧪 PHISHING DETECTION - COMPREHENSIVE TEST');
console.log('═══════════════════════════════════════════════════════');
console.log('');

// Test 1: Check if content script is loaded
console.log('TEST 1: Content Script Status');
console.log('─────────────────────────────────────────────────────');
if (typeof analyzeCurrentEmail === 'function') {
    console.log('✅ analyzeCurrentEmail function: FOUND');
} else {
    console.log('❌ analyzeCurrentEmail function: NOT FOUND');
    console.log('   Solution: Reload extension and refresh page');
}

if (typeof scrapeEmailPage === 'function') {
    console.log('✅ scrapeEmailPage function: FOUND');
} else {
    console.log('❌ scrapeEmailPage function: NOT FOUND');
}

if (typeof displayAnalysisResults === 'function') {
    console.log('✅ displayAnalysisResults function: FOUND');
} else {
    console.log('❌ displayAnalysisResults function: NOT FOUND');
}

const button = document.getElementById('phishing-scan-btn');
if (button) {
    console.log('✅ Scan button: FOUND');
    console.log('   ID:', button.id);
    console.log('   Text:', button.textContent);
    console.log('   Visible:', button.offsetParent !== null);
} else {
    console.log('❌ Scan button: NOT FOUND');
    console.log('   Solution: Wait 2 seconds and try again');
}

console.log('');

// Test 2: Test backend connectivity
console.log('TEST 2: Backend Connectivity');
console.log('─────────────────────────────────────────────────────');

fetch('http://localhost:5000/health')
    .then(response => {
        console.log('✅ Backend /health status:', response.status, response.statusText);
        return response.json();
    })
    .then(data => {
        console.log('   Response:', data);
    })
    .catch(error => {
        console.error('❌ Backend /health failed:', error.message);
        console.error('   Make sure Flask is running: python app.py');
    });

setTimeout(() => {
    console.log('');
    
    // Test 3: Test scraping
    console.log('TEST 3: Email Page Scraping');
    console.log('─────────────────────────────────────────────────────');
    
    if (typeof scrapeEmailPage === 'function') {
        try {
            const scraped = scrapeEmailPage();
            console.log('✅ Scraping successful!');
            console.log('   HTML length:', scraped.emailHTML.length, 'characters');
            console.log('   Page title:', scraped.pageTitle);
            console.log('   URL:', scraped.url);
            
            if (scraped.emailHTML.length > 1000) {
                console.log('✅ Sufficient content scraped');
            } else {
                console.log('⚠️  Warning: Very little content scraped');
                console.log('   Make sure an email is open (not inbox view)');
            }
        } catch (error) {
            console.error('❌ Scraping failed:', error.message);
        }
    } else {
        console.log('❌ Scraping function not available');
    }
    
    console.log('');
    
    // Test 4: Full workflow test
    console.log('TEST 4: Full Workflow Test');
    console.log('─────────────────────────────────────────────────────');
    console.log('Starting full analysis test...');
    console.log('');
    
    if (typeof analyzeCurrentEmail === 'function') {
        analyzeCurrentEmail()
            .then(result => {
                console.log('');
                console.log('═══════════════════════════════════════════════════════');
                console.log('🎉 TEST COMPLETE - ANALYSIS RESULT:');
                console.log('═══════════════════════════════════════════════════════');
                console.log('Success:', result.success);
                
                if (result.success) {
                    console.log('Risk Level:', result.analysis.risk_level);
                    console.log('Phishing Probability:', (result.analysis.phishing_probability * 100).toFixed(1) + '%');
                    console.log('Red Flags:', result.analysis.red_flags.length);
                    console.log('Social Engineering Techniques:', result.analysis.social_engineering.techniques_detected);
                    console.log('');
                    console.log('✅ ALL TESTS PASSED! Extension is working correctly.');
                    console.log('');
                    console.log('Now displaying the result...');
                    displayAnalysisResults(result);
                } else {
                    console.error('❌ Analysis failed:', result.error);
                    
                    if (result.error.includes('Failed to fetch')) {
                        console.error('');
                        console.error('DIAGNOSIS: Backend not reachable');
                        console.error('SOLUTION:');
                        console.error('  1. Make sure Flask is running: cd backend && python app.py');
                        console.error('  2. Check if http://localhost:5000/health works in browser');
                        console.error('  3. Check firewall settings');
                    } else if (result.error.includes('extract email content')) {
                        console.error('');
                        console.error('DIAGNOSIS: Could not extract email content');
                        console.error('SOLUTION:');
                        console.error('  1. Make sure an email is open (not inbox view)');
                        console.error('  2. Wait for email to fully load');
                        console.error('  3. Try a different email');
                    }
                }
                
                console.log('═══════════════════════════════════════════════════════');
            })
            .catch(error => {
                console.error('');
                console.error('═══════════════════════════════════════════════════════');
                console.error('💥 TEST FAILED - EXCEPTION:');
                console.error('═══════════════════════════════════════════════════════');
                console.error('Error:', error.message);
                console.error('Stack:', error.stack);
                console.error('═══════════════════════════════════════════════════════');
            });
    } else {
        console.log('❌ Cannot run full test - analyzeCurrentEmail not available');
        console.log('   Reload extension and refresh page');
    }
}, 1000);
```

## Instructions:

1. **Open Gmail** and open any email (make sure email body is visible)
2. **Press F12** to open Developer Tools
3. **Go to Console tab**
4. **Copy the entire script above** (everything inside the triple backticks)
5. **Paste it into the console** and press Enter
6. **Watch the output** - it will run all tests automatically

## What to Look For:

### ✅ **If All Tests Pass:**
- You'll see green checkmarks ✅
- Analysis result will display
- Animated popup will appear on screen
- **Your extension is working!**

### ❌ **If Tests Fail:**
Look for red X marks and error messages:

- **"Backend /health failed"** → Flask not running
- **"Scraping function not available"** → Extension not loaded
- **"Scan button: NOT FOUND"** → Wait 2 seconds and retry
- **"Failed to fetch"** → Backend connectivity issue
- **"Could not extract email content"** → Email not open or loaded

## Share Results:

After running the test, copy and paste **ALL** the console output and share it. This will show me exactly what's happening!
