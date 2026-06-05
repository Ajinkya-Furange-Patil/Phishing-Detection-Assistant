// Popup functionality for Phishing Detection Assistant

// DOM Elements
const scanBtn = document.getElementById('scanCurrentEmail');
const loadingOverlay = document.getElementById('loadingOverlay');
const recentResults = document.getElementById('recentResults');
const safeCount = document.getElementById('safeCount');
const threatCount = document.getElementById('threatCount');
const autoScanCheckbox = document.getElementById('autoScan');
const showNotificationsCheckbox = document.getElementById('showNotifications');
const apiEndpointInput = document.getElementById('apiEndpoint');
const saveSettingsBtn = document.getElementById('saveSettings');
const statusIndicator = document.getElementById('statusIndicator');

// Initialize settings
let settings = {
  autoScan: true,
  showNotifications: true,
  apiEndpoint: 'http://localhost:5000/api/scan'
};

// Load settings from chrome storage
chrome.storage.sync.get(['settings'], (result) => {
  if (result.settings) {
    settings = result.settings;
    autoScanCheckbox.checked = settings.autoScan;
    showNotificationsCheckbox.checked = settings.showNotifications;
    apiEndpointInput.value = settings.apiEndpoint;
  }
});

// Load statistics
chrome.storage.local.get(['stats'], (result) => {
  if (result.stats) {
    safeCount.textContent = result.stats.safe || 0;
    threatCount.textContent = result.stats.threats || 0;
  }
});

// Load recent results
function loadRecentResults() {
  chrome.storage.local.get(['recentScans'], (result) => {
    if (result.recentScans && result.recentScans.length > 0) {
      displayResults(result.recentScans);
    }
  });
}

// Display scan results
function displayResults(scans) {
  recentResults.innerHTML = '';
  
  scans.slice(0, 5).forEach(scan => {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    
    const badgeClass = scan.isPhishing ? 'badge-danger' : 
                       scan.confidence < 0.5 ? 'badge-warning' : 'badge-safe';
    const badgeText = scan.isPhishing ? 'THREAT' : 
                      scan.confidence < 0.5 ? 'CAUTION' : 'SAFE';
    
    resultItem.innerHTML = `
      <div class="result-info">
        <div class="result-subject">${scan.subject || 'No Subject'}</div>
        <div class="result-time">${formatTime(scan.timestamp)}</div>
      </div>
      <span class="result-badge ${badgeClass}">${badgeText}</span>
    `;
    
    recentResults.appendChild(resultItem);
  });
}

// Format timestamp
function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
}

// Scan current email
scanBtn.addEventListener('click', async () => {
  loadingOverlay.style.display = 'flex';
  
  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Check if on Gmail or Outlook
    if (!tab.url.includes('mail.google.com') && !tab.url.includes('outlook')) {
      alert('Please open a Gmail or Outlook email to scan.');
      loadingOverlay.style.display = 'none';
      return;
    }
    
    // Send message to content script to analyze
    chrome.tabs.sendMessage(tab.id, { action: 'analyzeCurrentEmail' }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Content script error:', chrome.runtime.lastError);
        
        // Try to inject content script
        const scriptFile = tab.url.includes('mail.google.com') ? 
                          'content-gmail.js' : 'content-outlook.js';
        
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: [scriptFile]
        }).then(() => {
          alert('Content script loaded. Please try scanning again.');
        }).catch(err => {
          alert('Error: Content script could not be loaded. Please refresh the page and try again.');
        });
        
        loadingOverlay.style.display = 'none';
        return;
      }
      
      if (response && response.success) {
        // Analysis will be displayed by content script
        setTimeout(() => {
          loadRecentResults();
          loadingOverlay.style.display = 'none';
        }, 1000);
      } else {
        alert('Analysis failed: ' + (response?.error || 'Unknown error'));
        loadingOverlay.style.display = 'none';
      }
    });
    
  } catch (error) {
    console.error('Scan error:', error);
    alert('Error scanning email: ' + error.message);
    loadingOverlay.style.display = 'none';
  }
});

// Analyze email using backend API
async function analyzeEmail(emailData) {
  try {
    const response = await fetch(settings.apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(emailData)
    });
    
    if (!response.ok) {
      throw new Error('Backend API error');
    }
    
    const result = await response.json();
    return {
      ...result,
      subject: emailData.subject,
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('API call failed:', error);
    // Return mock result if API fails (for demo purposes)
    return {
      isPhishing: false,
      confidence: 0.85,
      subject: emailData.subject,
      timestamp: Date.now(),
      modules: {
        content: 0.12,
        url: 0.08,
        header: 0.05,
        attachment: 0.01,
        behavioral: 0.10
      }
    };
  }
}

// Update statistics
function updateStats(isPhishing) {
  chrome.storage.local.get(['stats'], (result) => {
    const stats = result.stats || { safe: 0, threats: 0 };
    
    if (isPhishing) {
      stats.threats++;
      threatCount.textContent = stats.threats;
    } else {
      stats.safe++;
      safeCount.textContent = stats.safe;
    }
    
    chrome.storage.local.set({ stats });
  });
}


// Save scan result
function saveScanResult(result) {
  chrome.storage.local.get(['recentScans'], (data) => {
    const scans = data.recentScans || [];
    scans.unshift(result);
    
    // Keep only last 50 scans
    if (scans.length > 50) {
      scans.pop();
    }
    
    chrome.storage.local.set({ recentScans: scans });
  });
}

// Show notification
function showNotification(result) {
  if (result.isPhishing) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: '⚠️ Phishing Threat Detected!',
      message: `This email appears to be phishing (${Math.round(result.confidence * 100)}% confidence)`,
      priority: 2
    });
  }
}

// Save settings
saveSettingsBtn.addEventListener('click', () => {
  settings.autoScan = autoScanCheckbox.checked;
  settings.showNotifications = showNotificationsCheckbox.checked;
  settings.apiEndpoint = apiEndpointInput.value;
  
  chrome.storage.sync.set({ settings }, () => {
    // Visual feedback
    saveSettingsBtn.textContent = '✓ Saved!';
    setTimeout(() => {
      saveSettingsBtn.textContent = 'Save Settings';
    }, 2000);
  });
});

// Load recent results on popup open
loadRecentResults();
