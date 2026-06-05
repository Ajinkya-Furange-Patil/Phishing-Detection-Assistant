// Background service worker for Phishing Detection Assistant

console.log('Phishing Detection Assistant: Background service worker initialized');

// Initialize extension
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // First time installation
    console.log('Extension installed for the first time');
    
    // Set default settings
    chrome.storage.sync.set({
      settings: {
        autoScan: true,
        showNotifications: true,
        apiEndpoint: 'http://localhost:5000/api/scan'
      }
    });
    
    // Initialize stats
    chrome.storage.local.set({
      stats: {
        safe: 0,
        threats: 0
      },
      recentScans: []
    });
    
    // Show welcome notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: 'Phishing Detection Assistant Installed',
      message: 'Your email security is now protected by AI-powered detection!',
      priority: 1
    });
    
  } else if (details.reason === 'update') {
    console.log('Extension updated to version', chrome.runtime.getManifest().version);
  }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeEmail') {
    // Forward analysis request to backend
    analyzeEmailBackground(request.emailData)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'getStats') {
    chrome.storage.local.get(['stats'], (data) => {
      sendResponse({ stats: data.stats || { safe: 0, threats: 0 } });
    });
    return true;
  }
});


// Analyze email using backend API
async function analyzeEmailBackground(emailData) {
  try {
    const settings = await chrome.storage.sync.get(['settings']);
    const apiEndpoint = settings.settings?.apiEndpoint || 'http://localhost:5000/api/scan';
    
    const response = await fetch(apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(emailData)
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Background analysis error:', error);
    throw error;
  }
}

// Badge management
function updateBadge(threatCount) {
  if (threatCount > 0) {
    chrome.action.setBadgeText({ text: String(threatCount) });
    chrome.action.setBadgeBackgroundColor({ color: '#EF4444' });
  } else {
    chrome.action.setBadgeText({ text: '' });
  }
}

// Update badge when stats change
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.stats) {
    const newStats = changes.stats.newValue;
    if (newStats && newStats.threats) {
      updateBadge(newStats.threats);
    }
  }
});

// Context menu for quick scan
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'scanEmail',
    title: 'Scan this email for phishing',
    contexts: ['page'],
    documentUrlPatterns: [
      'https://mail.google.com/*',
      'https://outlook.live.com/*',
      'https://outlook.office365.com/*',
      'https://outlook.office.com/*'
    ]
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'scanEmail') {
    chrome.tabs.sendMessage(tab.id, { action: 'extractEmail' }, (response) => {
      if (response && response.emailData) {
        analyzeEmailBackground(response.emailData)
          .then(result => {
            chrome.tabs.sendMessage(tab.id, { action: 'showWarning', result });
          })
          .catch(error => {
            console.error('Scan error:', error);
          });
      }
    });
  }
});

// Alarm for periodic cleanup of old scan data
chrome.alarms.create('cleanupOldScans', { periodInMinutes: 1440 }); // Daily

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'cleanupOldScans') {
    chrome.storage.local.get(['recentScans'], (data) => {
      if (data.recentScans) {
        // Keep only scans from last 7 days
        const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
        const filtered = data.recentScans.filter(scan => scan.timestamp > sevenDaysAgo);
        chrome.storage.local.set({ recentScans: filtered });
      }
    });
  }
});
