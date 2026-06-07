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
        darkOverlay: true,
        apiEndpoint: 'http://localhost:5000/analyze',
        analysisEngine: 'random_forest'
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
  
  // Create context menu for quick scan (with error handling)
  try {
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
    }, () => {
      if (chrome.runtime.lastError) {
        console.log('Context menu creation note:', chrome.runtime.lastError.message);
      } else {
        console.log('Context menu created successfully');
      }
    });
  } catch (error) {
    console.error('Error creating context menu:', error);
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

  if (request.action === 'showNotification') {
    chrome.storage.sync.get(['settings'], (result) => {
      const settings = result.settings || {};
      if (settings.showNotifications) {
        showChromeNotification({
          isPhishing: request.isPhishing,
          confidence: request.confidence
        });
      }
    });
    sendResponse({ success: true });
    return true;
  }
});


// Analyze email using backend API
async function analyzeEmailBackground(emailData) {
  try {
    const settings = await chrome.storage.sync.get(['settings']);
    const apiEndpoint = settings.settings?.apiEndpoint || 'http://localhost:5000/analyze';
    const analysisEngine = settings.settings?.analysisEngine || 'random_forest';
    
    // Prepare payload for our comprehensive backend
    const payload = {
      email_content: emailData.body || '',
      subject: emailData.subject || '',
      sender: emailData.sender || '',
      model: analysisEngine
    };
    
    const response = await fetch(apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      throw new Error(`API request failed with status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Transform response to match expected format
    const analysis = result.analysis || {};
    const ml = analysis.ml_prediction || {};
    
    const transformedResult = {
      isPhishing: analysis.phishing_probability >= 0.5,
      confidence: analysis.phishing_probability || 0,
      riskLevel: analysis.risk_level || 'Low',
      phishingProbability: analysis.phishing_probability || 0,
      legitimateProbability: 1.0 - (analysis.phishing_probability || 0),
      features: ml.features || {},
      modelUsed: ml.model_used || 'unknown',
      timestamp: ml.timestamp || new Date().toISOString()
    };
    
    // Update stats
    updateStatsAfterScan(transformedResult);
    
    return transformedResult;
  } catch (error) {
    console.error('Background analysis error:', error);
    
    // Return fallback result
    return {
      isPhishing: false,
      confidence: 0,
      riskLevel: 'Unknown',
      error: error.message,
      fallback: true
    };
  }
}

// Update statistics after scan
async function updateStatsAfterScan(result) {
  const data = await chrome.storage.local.get(['stats', 'recentScans']);
  const stats = data.stats || { safe: 0, threats: 0 };
  const recentScans = data.recentScans || [];
  
  if (result.isPhishing) {
    stats.threats++;
  } else {
    stats.safe++;
  }
  
  // Add to recent scans (keep last 50)
  recentScans.unshift({
    ...result,
    timestamp: Date.now()
  });
  
  if (recentScans.length > 50) {
    recentScans.pop();
  }
  
  await chrome.storage.local.set({ stats, recentScans });
  updateBadge(stats.threats);
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

// Handle context menu clicks (with error handling)
if (chrome.contextMenus) {
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'scanEmail') {
      // Check if tab is valid and content script is loaded
      if (!tab || !tab.id) {
        console.error('Invalid tab');
        return;
      }
      
      // Send message with better error handling
      chrome.tabs.sendMessage(tab.id, { action: 'analyzeCurrentEmail' }, (response) => {
        if (chrome.runtime.lastError) {
          console.log('Content script not ready:', chrome.runtime.lastError.message);
          
          // Try to inject content script and retry
          chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['content-gmail.js']
          }).then(() => {
            // Retry after injection
            setTimeout(() => {
              chrome.tabs.sendMessage(tab.id, { action: 'analyzeCurrentEmail' });
            }, 500);
          }).catch(err => {
            console.error('Failed to inject content script:', err);
          });
          
          return;
        }
        
        if (response && response.success) {
          console.log('Analysis triggered successfully');
        }
      });
    }
  });
} else {
  console.warn('contextMenus API not available');
}

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

// Chrome Desktop Notification helper
function showChromeNotification(result) {
  const confidence = result.confidence !== undefined ? result.confidence : (result.phishingProbability || 0);
  try {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '⚠️ Phishing Threat Detected!',
      message: `This email appears to be phishing (${Math.round(confidence * 100)}% confidence)`,
      priority: 2
    });
  } catch (e) {
    console.warn('Notifications API unavailable:', e);
  }
}
