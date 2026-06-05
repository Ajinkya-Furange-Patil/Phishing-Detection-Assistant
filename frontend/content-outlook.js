// Content script for Outlook
console.log('Phishing Detection Assistant: Outlook content script loaded');

// Email data extraction for Outlook
function extractOutlookEmailData() {
  try {
    // Outlook's DOM structure (handles both Outlook.com and Office 365)
    const subject = document.querySelector('[role="heading"]')?.textContent || 
                   document.querySelector('.rps_76cb')?.textContent || 
                   document.querySelector('span[id*="Subject"]')?.textContent || '';
    
    const sender = document.querySelector('[aria-label*="Sender"]')?.textContent || 
                  document.querySelector('.rps_76cb + div')?.textContent || 
                  document.querySelector('span[id*="From"]')?.textContent || '';
    
    const body = document.querySelector('[role="document"]')?.textContent || 
                document.querySelector('.rps_42b4')?.textContent || 
                document.querySelector('div[id*="Body"]')?.textContent || '';
    
    // Extract links
    const links = Array.from(document.querySelectorAll('[role="document"] a, .rps_42b4 a, div[id*="Body"] a'))
      .map(a => a.href)
      .filter(href => href && !href.startsWith('mailto:'));
    
    // Extract headers
    const headers = {
      from: sender,
      to: document.querySelector('span[id*="To"]')?.textContent || '',
      date: document.querySelector('span[id*="Date"]')?.textContent || ''
    };
    
    // Check for attachments
    const attachments = Array.from(document.querySelectorAll('[data-attachment-name], .rps_e5b6'))
      .map(att => {
        const name = att.getAttribute('data-attachment-name') || att.textContent || '';
        const size = att.getAttribute('data-attachment-size') || '';
        return { name, size };
      });
    
    return {
      subject,
      sender,
      body,
      links,
      headers,
      attachments,
      platform: 'outlook'
    };
  } catch (error) {
    console.error('Error extracting Outlook email:', error);
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
  
  if (result.isPhishing) {
    const banner = document.createElement('div');
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
        <button class="banner-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;
    
    // Insert banner at the top of email
    const emailContainer = document.querySelector('[role="main"]') || document.querySelector('div[class*="ReadingPane"]');
    if (emailContainer) {
      emailContainer.insertBefore(banner, emailContainer.firstChild);
    }
  } else if (result.confidence < 0.7) {
    const banner = document.createElement('div');
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
        <button class="banner-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;
    
    const emailContainer = document.querySelector('[role="main"]') || document.querySelector('div[class*="ReadingPane"]');
    if (emailContainer) {
      emailContainer.insertBefore(banner, emailContainer.firstChild);
    }
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractEmail') {
    const emailData = extractOutlookEmailData();
    sendResponse({ emailData });
  } else if (request.action === 'showWarning') {
    addWarningBanner(request.result);
    sendResponse({ success: true });
  }
  return true;
});

// Auto-scan if enabled
chrome.storage.sync.get(['settings'], (result) => {
  if (result.settings && result.settings.autoScan) {
    // Monitor for email changes
    const observer = new MutationObserver(() => {
      // Auto-scan logic can be implemented here
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
});
