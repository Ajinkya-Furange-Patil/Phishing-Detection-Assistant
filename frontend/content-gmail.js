// Content script for Gmail integration
console.log('Phishing Detection: Gmail content script loaded');

// Function to scrape entire email page
function scrapeEmailPage() {
    try {
        // Get the entire page HTML
        const pageHTML = document.documentElement.outerHTML;
        
        // Also try to get specific email elements for fallback
        const emailView = document.querySelector('[role="main"]') || 
                         document.querySelector('.nH.aHU') ||
                         document.body;
        
        const emailHTML = emailView ? emailView.outerHTML : pageHTML;
        
        return {
            fullHTML: pageHTML,
            emailHTML: emailHTML,
            pageTitle: document.title,
            url: window.location.href
        };
    } catch (error) {
        console.error('Error scraping email page:', error);
        return {
            fullHTML: document.body.innerHTML,
            emailHTML: document.body.innerHTML,
            error: error.message
        };
    }
}

// Function to send to backend for extraction and analysis
async function analyzeCurrentEmail() {
    try {
        console.log('🔍 Starting phishing analysis...');
        console.log('📧 Step 1: Scraping email page...');
        const scrapedData = scrapeEmailPage();
        console.log('✅ Scraped', scrapedData.emailHTML.length, 'characters');
        
        // Retrieve endpoint and model from sync settings dynamically
        const settings = await chrome.storage.sync.get(['settings']);
        const customEndpoint = settings.settings?.apiEndpoint || 'http://localhost:5000/analyze';
        const modelEngine = settings.settings?.analysisEngine || 'random_forest';
        const apiUrl = new URL(customEndpoint);
        const extractAndAnalyzeUrl = `${apiUrl.origin}/extract-and-analyze`;
        
        console.log('🌐 Step 2: Sending to backend for analysis...');
        console.log('   Backend URL:', extractAndAnalyzeUrl);
        
        // Send to our backend API
        const response = await fetch(extractAndAnalyzeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                page_html: scrapedData.emailHTML,
                model: modelEngine
            })
        });
        
        console.log('📡 Backend response status:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ API error response:', errorText);
            throw new Error(`API returned ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        console.log('📊 Analysis result:', result);
        
        if (result.success) {
            console.log('✅ Analysis complete successfully!');
            console.log('   Risk Level:', result.analysis?.risk_level);
            console.log('   Probability:', result.analysis?.phishing_probability);
            return result;
        } else {
            console.error('❌ Analysis failed:', result.error);
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('💥 Analysis error:', error);
        console.error('   Error type:', error.name);
        console.error('   Error message:', error.message);
        
        // Check for common errors
        if (error.message.includes('Failed to fetch')) {
            console.error('⚠️  Backend not reachable. Is Flask running on port 5000?');
        } else if (error.message.includes('CORS')) {
            console.error('⚠️  CORS error. Check backend CORS configuration.');
        }
        
        return {
            success: false,
            error: error.message
        };
    }
}

// Function to display results
function displayAnalysisResults(result) {
    // Remove existing warning if any
    const existingWarning = document.getElementById('phishing-detection-warning');
    if (existingWarning) {
        existingWarning.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => existingWarning.remove(), 300);
    }
    
    if (!result || !result.success) {
        const errorMsg = result?.error || 'Analysis failed';
        console.error('❌ Cannot display results:', errorMsg);
        
        // Show detailed error to user
        if (errorMsg.includes('Failed to fetch') || errorMsg.includes('not reachable')) {
            showNotification('❌ Backend server not reachable. Is Flask running?', 'error');
        } else if (errorMsg.includes('extract email content')) {
            showNotification('❌ Could not extract email content from page', 'error');
        } else {
            showNotification(`❌ Analysis failed: ${errorMsg}`, 'error');
        }
        return;
    }
    
    const analysis = result.analysis;
    const extracted = result.extracted_email;
    
    // Determine risk color
    const riskLevel = analysis.risk_level;
    const riskColor = riskLevel === 'HIGH' ? '#ef4444' : 
                     riskLevel === 'MEDIUM' ? '#f59e0b' : '#10b981';
    
    // Create warning banner
    const warning = document.createElement('div');
    warning.id = 'phishing-detection-warning';
    warning.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        max-width: 420px;
        background: white;
        border-left: 5px solid ${riskColor};
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        animation: slideInBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        transform-origin: top right;
    `;
    
    const probability = (analysis.phishing_probability * 100).toFixed(1);
    const threatScore = analysis.threat_indicators.score;
    const redFlagsCount = analysis.red_flags.length;
    const socialEngCount = analysis.social_engineering.techniques_detected;
    
    warning.innerHTML = `
        <style>
            @keyframes slideInBounce {
                0% { 
                    transform: translateX(120%) scale(0.8);
                    opacity: 0;
                }
                50% {
                    transform: translateX(-10px) scale(1.05);
                }
                100% { 
                    transform: translateX(0) scale(1);
                    opacity: 1;
                }
            }
            
            @keyframes slideOut {
                from { 
                    transform: translateX(0) scale(1);
                    opacity: 1;
                }
                to { 
                    transform: translateX(120%) scale(0.8);
                    opacity: 0;
                }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            @keyframes shimmer {
                0% { background-position: -200% center; }
                100% { background-position: 200% center; }
            }
            
            .fade-in-item {
                animation: fadeIn 0.4s ease-out forwards;
                opacity: 0;
            }
            
            .fade-in-item:nth-child(1) { animation-delay: 0.1s; }
            .fade-in-item:nth-child(2) { animation-delay: 0.2s; }
            .fade-in-item:nth-child(3) { animation-delay: 0.3s; }
            .fade-in-item:nth-child(4) { animation-delay: 0.4s; }
            
            .pulse-badge {
                animation: pulse 2s ease-in-out infinite;
            }
            
            .shimmer-text {
                background: linear-gradient(
                    90deg,
                    ${riskColor} 0%,
                    ${riskColor}dd 50%,
                    ${riskColor} 100%
                );
                background-size: 200% auto;
                animation: shimmer 2s linear infinite;
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .btn-hover:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: all 0.2s ease;
            }
            
            .btn-hover:active {
                transform: translateY(0);
                transition: all 0.1s ease;
            }
            
            .progress-bar {
                width: 0%;
                height: 4px;
                background: ${riskColor};
                border-radius: 2px;
                animation: progressFill 1s ease-out forwards;
                margin-top: 8px;
            }
            
            @keyframes progressFill {
                to { width: ${probability}%; }
            }
            
            .badge-float {
                animation: float 3s ease-in-out infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-5px); }
            }
        </style>
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 18px;" class="fade-in-item">
            <div>
                <h3 style="margin: 0 0 8px 0; color: #1f2937; font-size: 20px; font-weight: 700;">
                    🛡️ Phishing Analysis
                </h3>
                <div style="font-size: 13px; color: #6b7280; font-weight: 500;">
                    AI-Powered Detection • Real-time
                </div>
            </div>
            <button id="close-warning" style="
                background: none;
                border: none;
                font-size: 28px;
                cursor: pointer;
                color: #9ca3af;
                padding: 0;
                line-height: 1;
                transition: all 0.2s;
            " class="btn-hover" onmouseover="this.style.color='#ef4444'; this.style.transform='rotate(90deg)'" 
               onmouseout="this.style.color='#9ca3af'; this.style.transform='rotate(0deg)'">×</button>
        </div>
        
        <div class="fade-in-item" style="background: ${riskColor}15; padding: 18px; border-radius: 10px; margin-bottom: 16px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; right: 0; font-size: 80px; opacity: 0.1; line-height: 1;">
                ${riskLevel === 'HIGH' ? '⚠️' : riskLevel === 'MEDIUM' ? '⚡' : '✓'}
            </div>
            <div style="position: relative; z-index: 1;">
                <div class="shimmer-text" style="font-size: 28px; font-weight: 800; margin-bottom: 8px;">
                    ${riskLevel} RISK
                </div>
                <div style="font-size: 14px; color: #4b5563; margin-bottom: 6px;">
                    <strong>Phishing Probability:</strong> <span style="color: ${riskColor}; font-weight: 700;">${probability}%</span>
                </div>
                <div class="progress-bar"></div>
                <div style="font-size: 14px; color: #4b5563; margin-top: 10px;">
                    <strong>Threat Score:</strong> <span style="color: ${riskColor}; font-weight: 700;">${threatScore}/100</span>
                </div>
            </div>
        </div>
        
        <div class="fade-in-item" style="font-size: 13px; color: #4b5563; margin-bottom: 16px; background: #f9fafb; padding: 14px; border-radius: 8px;">
            <div style="margin-bottom: 10px;">
                <strong style="color: #1f2937; font-size: 14px;">📧 Extracted Email</strong>
            </div>
            <div style="margin-bottom: 6px;">
                <span style="opacity: 0.7;">Subject:</span> <strong>${extracted.subject || 'N/A'}</strong>
            </div>
            <div style="margin-bottom: 6px;">
                <span style="opacity: 0.7;">Sender:</span> <strong>${extracted.sender || 'N/A'}</strong>
            </div>
        </div>
        
        <div class="fade-in-item" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px;">
            <div style="background: #fef3c7; padding: 12px; border-radius: 8px; text-align: center;" class="badge-float">
                <div style="font-size: 24px; font-weight: 800; color: #92400e;">${redFlagsCount}</div>
                <div style="font-size: 12px; color: #78350f; font-weight: 600;">🚩 Red Flags</div>
            </div>
            <div style="background: #dbeafe; padding: 12px; border-radius: 8px; text-align: center;" class="badge-float" style="animation-delay: 0.5s;">
                <div style="font-size: 24px; font-weight: 800; color: #1e40af;">${socialEngCount}</div>
                <div style="font-size: 12px; color: #1e3a8a; font-weight: 600;">🎭 Techniques</div>
            </div>
        </div>
        
        <div class="fade-in-item" style="font-size: 12px; color: #6b7280; margin-bottom: 14px; line-height: 1.6;">
            ${analysis.red_flags.slice(0, 2).map(flag => 
                `<div style="margin-bottom: 6px;">• <strong>${flag.type}</strong> [${flag.severity}]</div>`
            ).join('')}
            ${redFlagsCount > 2 ? `<div style="opacity: 0.7;">+ ${redFlagsCount - 2} more red flags...</div>` : ''}
        </div>
        
        <div style="display: flex; gap: 10px;">
            <button id="view-details-btn" style="
                flex: 1;
                background: linear-gradient(135deg, ${riskColor} 0%, ${riskColor}dd 100%);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 700;
                font-size: 14px;
                transition: all 0.3s;
            " class="btn-hover">
                📊 View Full Report
            </button>
            <button id="dismiss-btn" style="
                flex: 1;
                background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                color: #4b5563;
                border: none;
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 700;
                font-size: 14px;
                transition: all 0.3s;
            " class="btn-hover">
                ✓ Dismiss
            </button>
        </div>
        
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #9ca3af; text-align: center;">
            Analyzed by AI • ${new Date().toLocaleTimeString()}
        </div>
    `;
    
    document.body.appendChild(warning);
    
    // Add event listeners
    document.getElementById('close-warning').addEventListener('click', () => {
        warning.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => warning.remove(), 300);
    });
    
    document.getElementById('dismiss-btn').addEventListener('click', () => {
        warning.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => warning.remove(), 300);
    });
    
    document.getElementById('view-details-btn').addEventListener('click', () => {
        showDetailedReport(result);
    });
    
    // Auto-dismiss after 45 seconds for low risk
    if (riskLevel === 'LOW') {
        setTimeout(() => {
            if (warning.parentNode) {
                warning.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => warning.remove(), 300);
            }
        }, 45000);
    }
}

// Function to show detailed report in modal
function showDetailedReport(result) {
    const analysis = result.analysis;
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.7);
        z-index: 10001;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        border-radius: 12px;
        max-width: 800px;
        max-height: 90vh;
        overflow-y: auto;
        padding: 30px;
    `;
    
    content.innerHTML = `
        <h2 style="margin-top: 0;">📊 Detailed Phishing Analysis Report</h2>
        <pre style="white-space: pre-wrap; font-family: monospace; font-size: 12px; background: #f3f4f6; padding: 20px; border-radius: 8px; overflow-x: auto;">
${result.formatted_report}
        </pre>
        <div style="display: flex; gap: 12px; margin-top: 20px;">
            <button id="download-modal-report" style="
                flex: 1;
                background: #10b981;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: background 0.2s;
            " onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'">
                📥 Download Report
            </button>
            <button id="close-modal" style="
                flex: 1;
                background: #6b7280;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-size: 16px;
                transition: background 0.2s;
            " onmouseover="this.style.background='#4b5563'" onmouseout="this.style.background='#6b7280'">
                Close
            </button>
        </div>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
    
    document.getElementById('close-modal').addEventListener('click', () => modal.remove());
    
    document.getElementById('download-modal-report').addEventListener('click', () => {
        const textContent = result.html_report || '';
        const blob = new Blob([textContent], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const element = document.createElement('a');
        element.setAttribute('href', url);
        element.setAttribute('download', `phishguard_report_${Date.now()}.html`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        URL.revokeObjectURL(url);
    });
}

// Function to show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        max-width: 400px;
        background: ${type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.5;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // For errors, show longer and add dismiss button
    const duration = type === 'error' ? 8000 : 3000;
    
    if (type === 'error') {
        const dismissBtn = document.createElement('button');
        dismissBtn.textContent = '×';
        dismissBtn.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            line-height: 1;
            padding: 0;
            width: 24px;
            height: 24px;
        `;
        dismissBtn.onclick = () => notification.remove();
        notification.appendChild(dismissBtn);
        notification.style.paddingRight = '40px';
    }
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'analyzeCurrentEmail') {
        analyzeCurrentEmail().then(result => {
            displayAnalysisResults(result);
            sendResponse({ success: true });
        }).catch(error => {
            console.error('Analysis failed:', error);
            showNotification('Analysis failed: ' + error.message, 'error');
            sendResponse({ success: false, error: error.message });
        });
        return true; // Keep channel open for async response
    }
    
    if (request.action === 'extractEmail') {
        const scrapedData = scrapeEmailPage();
        const gmailData = extractGmailEmailData() || {};
        sendResponse({ 
            success: true, 
            emailData: {
                subject: gmailData.subject || scrapedData.pageTitle || '',
                sender: gmailData.sender || '',
                body: gmailData.body || '',
                links: gmailData.links || [],
                headers: gmailData.headers || {},
                attachments: gmailData.attachments || [],
                platform: 'gmail',
                emailHTML: scrapedData.emailHTML,
                fullHTML: scrapedData.fullHTML,
                pageTitle: scrapedData.pageTitle,
                url: scrapedData.url
            }
        });
    }

    if (request.action === 'showWarning') {
        addWarningBanner(request.result);
        sendResponse({ success: true });
    }
    return true; // Keep channel open for async response
});

// Add scan button to Gmail interface (safely next to the subject line to prevent misclicks with the toolbar back button)
function addScanButton() {
    // Check if button already exists
    if (document.getElementById('phishing-scan-btn')) return;
    
    // Target the email subject title header to place the button securely inline
    const subjectHeader = document.querySelector('h2.hP') || 
                          document.querySelector('[data-legacy-thread-id]')?.querySelector('h2');
    
    if (subjectHeader) {
        const scanBtn = document.createElement('button');
        scanBtn.id = 'phishing-scan-btn';
        scanBtn.innerHTML = '🛡️ Scan for Phishing';
        scanBtn.style.cssText = `
            background: #2563eb;
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 600;
            font-size: 12px;
            margin-left: 18px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
            transition: all 0.2s ease;
            vertical-align: middle;
        `;
        
        scanBtn.addEventListener('mouseenter', () => {
            scanBtn.style.background = '#1d4ed8';
            scanBtn.style.transform = 'translateY(-1px)';
            scanBtn.style.boxShadow = '0 4px 6px rgba(37, 99, 235, 0.3)';
        });
        scanBtn.addEventListener('mouseleave', () => {
            scanBtn.style.background = '#2563eb';
            scanBtn.style.transform = 'none';
            scanBtn.style.boxShadow = '0 2px 4px rgba(37, 99, 235, 0.2)';
        });
        
        scanBtn.addEventListener('click', async () => {
            scanBtn.textContent = '⏳ Scanning...';
            scanBtn.disabled = true;
            
            const result = await analyzeCurrentEmail();
            displayAnalysisResults(result);
            
            scanBtn.innerHTML = '🛡️ Scan for Phishing';
            scanBtn.disabled = false;
        });
        
        // Ensure flex layout parent style so items line up nicely
        if (subjectHeader.parentElement) {
            subjectHeader.parentElement.style.display = 'flex';
            subjectHeader.parentElement.style.alignItems = 'center';
            subjectHeader.parentElement.style.flexWrap = 'wrap';
            subjectHeader.parentElement.style.gap = '8px';
        }
        
        // Append next to the subject header
        subjectHeader.parentNode.insertBefore(scanBtn, subjectHeader.nextSibling);
    }
}

// Initialize
setTimeout(addScanButton, 2000);

// Re-add button when navigating between emails
const observer = new MutationObserver(() => {
    addScanButton();
});

observer.observe(document.body, { childList: true, subtree: true });

console.log('Phishing Detection: Ready! Click the scan button or use right-click menu.');

// Email data extraction for Gmail
function extractGmailEmailData() {
  try {
    // Gmail's DOM structure
    const subject = document.querySelector('h2.hP')?.textContent || 
                   document.querySelector('[data-legacy-thread-id]')?.querySelector('h2')?.textContent || '';
    
    const sender = document.querySelector('span.gD')?.getAttribute('email') || 
                  document.querySelector('span.go')?.textContent || '';
    
    const body = document.querySelector('div.a3s.aiL')?.textContent || 
                document.querySelector('.gs .ii.gt')?.textContent || '';
    
    // Extract links
    const links = Array.from(document.querySelectorAll('div.a3s.aiL a, .gs .ii.gt a'))
      .map(a => a.href)
      .filter(href => href && !href.startsWith('mailto:'));
    
    // Extract headers (if available)
    const headers = {
      from: sender,
      to: document.querySelector('span.hb')?.textContent || '',
      date: document.querySelector('span.g3')?.getAttribute('title') || ''
    };
    
    // Check for attachments
    const attachments = Array.from(document.querySelectorAll('div.aZo'))
      .map(att => {
        const name = att.querySelector('span.aV3')?.textContent || '';
        const size = att.querySelector('span.SaH2Ve')?.textContent || '';
        return { name, size };
      });
    
    return {
      subject,
      sender,
      body,
      links,
      headers,
      attachments,
      platform: 'gmail'
    };
  } catch (error) {
    console.error('Error extracting Gmail email:', error);
    return null;
  }
}


// Add phishing warning banner
function addWarningBanner(result) {
  // Remove existing banner if present
  const existingBanner = document.getElementById('phishing-detection-banner');
  if (existingBanner) {
    existingBanner.remove();
  }
  
  let banner = null;
  if (result.isPhishing) {
    banner = document.createElement('div');
    banner.id = 'phishing-detection-banner';
    banner.className = 'phishing-warning-banner danger';
    banner.innerHTML = `
      <div class="banner-content">
        <svg class="banner-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div class="banner-text">
          <strong>⚠️ PHISHING THREAT DETECTED</strong>
          <p>This email has been flagged as potential phishing (${Math.round(result.confidence * 100)}% confidence). Do not click links or download attachments.</p>
        </div>
        <button class="banner-close">×</button>
      </div>
    `;
    
    // Insert banner at the top of email
    const emailContainer = document.querySelector('div.nH.if') || document.querySelector('.gs');
    if (emailContainer) {
      emailContainer.insertBefore(banner, emailContainer.firstChild);
    }
  } else if (result.confidence < 0.7) {
    banner = document.createElement('div');
    banner.id = 'phishing-detection-banner';
    banner.className = 'phishing-warning-banner warning';
    banner.innerHTML = `
      <div class="banner-content">
        <svg class="banner-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="banner-text">
          <strong>⚠ CAUTION</strong>
          <p>This email contains some suspicious elements. Verify sender before taking action.</p>
        </div>
        <button class="banner-close">×</button>
      </div>
    `;
    
    const emailContainer = document.querySelector('div.nH.if') || document.querySelector('.gs');
    if (emailContainer) {
      emailContainer.insertBefore(banner, emailContainer.firstChild);
    }
  }
  
  if (banner) {
    const closeBtn = banner.querySelector('.banner-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        banner.remove();
      });
    }
  }
}

// Messaging channels are handled by the main listener above.

let isAutoScanEnabled = false;
let lastScannedEmailKey = '';
let autoScanTimeout = null;

function runGmailAutoScan() {
  const emailData = extractGmailEmailData();
  if (!emailData || !emailData.subject || !emailData.body) return;
  
  const currentKey = `${emailData.sender}_${emailData.subject}_${emailData.body.substring(0, 100)}`;
  if (currentKey === lastScannedEmailKey) return;
  
  lastScannedEmailKey = currentKey;
  console.log('🔄 Auto-scanning new email:', emailData.subject);
  
  chrome.runtime.sendMessage({
    action: 'analyzeEmail',
    emailData: {
      subject: emailData.subject,
      sender: emailData.sender,
      body: emailData.body
    }
  }, (response) => {
    if (response && response.success && response.result) {
      const analysisResult = response.result;
      console.log('📊 Auto-scan analysis result:', analysisResult);
      
      const bannerResult = {
        isPhishing: analysisResult.isPhishing,
        confidence: analysisResult.confidence !== undefined ? analysisResult.confidence : (analysisResult.phishingProbability || 0)
      };
      
      addWarningBanner(bannerResult);
      
      // Trigger desktop notification if threat detected and settings allow it
      if (analysisResult.isPhishing) {
        chrome.runtime.sendMessage({
          action: 'showNotification',
          isPhishing: analysisResult.isPhishing,
          confidence: analysisResult.confidence !== undefined ? analysisResult.confidence : (analysisResult.phishingProbability || 0)
        });
      }
    }
  });
}

// Auto-scan live storage tracking
chrome.storage.sync.get(['settings'], (result) => {
  if (result.settings) {
    isAutoScanEnabled = !!result.settings.autoScan;
  }
});

chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'sync' && changes.settings) {
    isAutoScanEnabled = !!changes.settings.newValue?.autoScan;
  }
});

// Monitor for email changes
const autoScanObserver = new MutationObserver(() => {
  if (!isAutoScanEnabled) return;
  if (autoScanTimeout) clearTimeout(autoScanTimeout);
  autoScanTimeout = setTimeout(runGmailAutoScan, 1000);
});

autoScanObserver.observe(document.body, {
  childList: true,
  subtree: true
});
