// ═══════════════════════════════════════════════════════════
// PhishGuard — Popup Controller v2.1
// Premium animated Chrome Extension logic
// ═══════════════════════════════════════════════════════════

// ── DOM References ──
const scanBtn = document.getElementById('scanCurrentEmail');
const loadingOverlay = document.getElementById('loadingOverlay');
const recentResults = document.getElementById('recentResults');
const safeCount = document.getElementById('safeCount');
const threatCount = document.getElementById('threatCount');
const autoScanCheckbox = document.getElementById('autoScan');
const showNotificationsCheckbox = document.getElementById('showNotifications');
const darkOverlayCheckbox = document.getElementById('darkOverlay');
const apiEndpointInput = document.getElementById('apiEndpoint');
const saveSettingsBtn = document.getElementById('saveSettings');
const statusIndicator = document.getElementById('statusIndicator');
const toastContainer = document.getElementById('toastContainer');

// ── Settings ──
let settings = {
  autoScan: true,
  showNotifications: true,
  darkOverlay: true,
  apiEndpoint: 'http://localhost:5000/analyze'
};

let currentFormattedReport = '';
let currentHtmlReport = '';
// ═══════════════════════════════════════════════════════════
// PARTICLE SYSTEM — Ambient floating particles
// ═══════════════════════════════════════════════════════════
(function initParticles() {
  const canvas = document.getElementById('particleCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let particles = [];
  const PARTICLE_COUNT = 35;

  function resize() {
    canvas.width = 380;
    canvas.height = 600;
  }
  resize();

  class Particle {
    constructor() {
      this.reset();
    }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.vx = (Math.random() - 0.5) * 0.3;
      this.vy = (Math.random() - 0.5) * 0.3;
      this.radius = Math.random() * 1.5 + 0.5;
      this.opacity = Math.random() * 0.4 + 0.1;
      this.hue = Math.random() > 0.7 ? 160 : 240; // green or indigo
    }
    update() {
      this.x += this.vx;
      this.y += this.vy;
      if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
      if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${this.hue}, 70%, 65%, ${this.opacity})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(new Particle());
  }

  function drawLines() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 80) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(99, 102, 241, ${0.06 * (1 - dist / 80)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    drawLines();
    requestAnimationFrame(animate);
  }
  animate();
})();

// ═══════════════════════════════════════════════════════════
// ANIMATED COUNTER
// ═══════════════════════════════════════════════════════════
function animateCounter(element, target) {
  const start = parseInt(element.textContent) || 0;
  const duration = 600;
  const startTime = performance.now();

  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    element.textContent = Math.round(start + (target - start) * eased);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ═══════════════════════════════════════════════════════════
// TOAST NOTIFICATION SYSTEM
// ═══════════════════════════════════════════════════════════
function showToast(message, type = 'info', duration = 3500) {
  const icons = { safe: '✅', threat: '🚨', info: '🛡️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || '🛡️'}</span>
    <span>${message}</span>
  `;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('leaving');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ═══════════════════════════════════════════════════════════
// SCAN STEP ANIMATION
// ═══════════════════════════════════════════════════════════
function animateScanSteps() {
  return new Promise(resolve => {
    const steps = document.querySelectorAll('.scan-step');
    const progressFill = document.getElementById('scanProgressFill');
    const percentText = document.getElementById('scanPercentText');
    let current = 0;
    const totalSteps = steps.length;
    const stepDuration = 500;

    function nextStep() {
      if (current >= totalSteps) {
        resolve();
        return;
      }

      // Mark previous as done
      if (current > 0) {
        steps[current - 1].classList.remove('active');
        steps[current - 1].classList.add('done');
        steps[current - 1].querySelector('.step-icon').textContent = '✓';
      }

      // Activate current
      steps[current].classList.add('active');

      // Update progress
      const pct = Math.round(((current + 1) / totalSteps) * 100);
      progressFill.style.width = `${pct}%`;
      percentText.textContent = `${pct}%`;

      current++;
      setTimeout(nextStep, stepDuration);
    }

    // Reset all steps
    steps.forEach(s => {
      s.classList.remove('active', 'done');
      s.querySelector('.step-icon').textContent = '⬡';
    });
    progressFill.style.width = '0%';
    percentText.textContent = '0%';

    setTimeout(nextStep, 300);
  });
}

// ═══════════════════════════════════════════════════════════
// HEATMAP GENERATION
// ═══════════════════════════════════════════════════════════
function generateHeatmap() {
  const grid = document.getElementById('heatmapGrid');
  if (!grid) return;
  grid.innerHTML = '';

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const today = new Date();

  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dayName = days[d.getDay() === 0 ? 6 : d.getDay() - 1];

    // Generate random threat level for demo (0-4)
    const level = Math.floor(Math.random() * 5);
    const cell = document.createElement('div');
    cell.className = `heatmap-cell lvl-${level}`;
    cell.setAttribute('data-tooltip', `${dayName}: ${level} threats`);
    cell.style.animationDelay = `${(6 - i) * 0.05}s`;
    grid.appendChild(cell);
  }
}

// ═══════════════════════════════════════════════════════════
// CHROME STORAGE INTEGRATION
// ═══════════════════════════════════════════════════════════

// Safely access chrome storage (graceful fallback for non-extension context)
function chromeStorageGet(area, keys, callback) {
  try {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage[area]) {
      chrome.storage[area].get(keys, callback);
    } else {
      callback({});
    }
  } catch (e) {
    callback({});
  }
}

function chromeStorageSet(area, data, callback) {
  try {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage[area]) {
      chrome.storage[area].set(data, callback || (() => {}));
    } else if (callback) {
      callback();
    }
  } catch (e) {
    if (callback) callback();
  }
}

// Load settings
chromeStorageGet('sync', ['settings'], (result) => {
  if (result.settings) {
    settings = { ...settings, ...result.settings };
    if (autoScanCheckbox) autoScanCheckbox.checked = settings.autoScan;
    if (showNotificationsCheckbox) showNotificationsCheckbox.checked = settings.showNotifications;
    if (darkOverlayCheckbox) darkOverlayCheckbox.checked = settings.darkOverlay;
    if (apiEndpointInput) apiEndpointInput.value = settings.apiEndpoint;
    applyOverlayTheme();
  }
});

// Apply loading overlay theme styling (dark cyber-dark vs light glassmorphism)
function applyOverlayTheme() {
  if (!loadingOverlay) return;
  if (settings.darkOverlay) {
    loadingOverlay.classList.remove('light');
  } else {
    loadingOverlay.classList.add('light');
  }
}

// Load statistics
chromeStorageGet('local', ['stats'], (result) => {
  if (result.stats) {
    animateCounter(safeCount, result.stats.safe || 0);
    animateCounter(threatCount, result.stats.threats || 0);
  }
});

// ═══════════════════════════════════════════════════════════
// RESULTS DISPLAY
// ═══════════════════════════════════════════════════════════
function loadRecentResults() {
  chromeStorageGet('local', ['recentScans'], (result) => {
    if (result.recentScans && result.recentScans.length > 0) {
      displayResults(result.recentScans);
    }
  });
}

function displayResults(scans) {
  recentResults.innerHTML = '';

  scans.slice(0, 5).forEach((scan, index) => {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    resultItem.style.animationDelay = `${index * 0.08}s`;

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

function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;

  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
}

// ═══════════════════════════════════════════════════════════
// // Context of the scanned email
let currentEmailData = null;

// Real-time progress check visual manager
function updateScanStep(stepNumber, status) {
  const steps = document.querySelectorAll('.scan-step');
  if (stepNumber < 1 || stepNumber > steps.length) return;
  
  const step = steps[stepNumber - 1];
  const icon = step.querySelector('.step-icon');
  const progressFill = document.getElementById('scanProgressFill');
  const percentText = document.getElementById('scanPercentText');
  
  step.classList.remove('active', 'done', 'failed');
  
  if (status === 'active') {
    step.classList.add('active');
    icon.textContent = '⬡';
  } else if (status === 'done') {
    step.classList.add('done');
    icon.textContent = '✓';
  } else if (status === 'failed') {
    step.classList.add('failed');
    icon.textContent = '✗';
  } else {
    icon.textContent = '⬡';
  }
  
  // Calculate real percentage based on step states
  const completedCount = document.querySelectorAll('.scan-step.done').length;
  const activeCount = document.querySelectorAll('.scan-step.active').length;
  const failedCount = document.querySelectorAll('.scan-step.failed').length;
  
  let pct = 0;
  if (failedCount > 0) {
    pct = Math.round(((stepNumber - 1) / steps.length) * 100);
  } else {
    pct = Math.round(((completedCount + (activeCount * 0.5)) / steps.length) * 100);
  }
  progressFill.style.width = `${pct}%`;
  percentText.textContent = `${pct}%`;
}

// Helper to extract email components from HTML using backend Gemini endpoint
async function extractEmailFields(emailHTML) {
  try {
    const apiUrl = new URL(settings.apiEndpoint);
    const extractUrl = `${apiUrl.origin}/extract-fields`;
    
    const response = await fetch(extractUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_html: emailHTML })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Extraction API error (${response.status}): ${errorText}`);
    }

    const result = await response.json();
    if (result.success && result.extracted_email) {
      return result.extracted_email;
    } else {
      throw new Error(result.error || 'Failed to extract email components');
    }
  } catch (e) {
    throw e;
  }
}

// SCAN HANDLER
// ═══════════════════════════════════════════════════════════
scanBtn.addEventListener('click', async () => {
  // Show overlay and start scanner styling
  loadingOverlay.style.display = 'flex';
  const radarEl = document.getElementById('radarScan');
  if (radarEl) radarEl.classList.add('scanning');

  // Reset steps to pending
  const steps = document.querySelectorAll('.scan-step');
  steps.forEach(s => {
    s.classList.remove('active', 'done', 'failed');
    s.querySelector('.step-icon').textContent = '⬡';
  });

  // Step 1: Initializing scan engine...
  updateScanStep(1, 'active');

  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.id || tab.url.startsWith('chrome://')) {
      updateScanStep(1, 'failed');
      throw new Error('Please navigate to Gmail or Outlook to scan emails.');
    }

    // Step 1 done, Step 2 active: Extracting email content...
    updateScanStep(1, 'done');
    updateScanStep(2, 'active');

    // Send message to content script to extract email HTML
    let response;
    try {
      response = await chrome.tabs.sendMessage(tab.id, { action: 'extractEmail' });
    } catch (msgErr) {
      updateScanStep(2, 'failed');
      throw new Error('Could not establish connection with email page. Please refresh the Gmail/Outlook tab.');
    }

    if (response && response.emailData) {
      currentEmailData = response.emailData;
      
      // Run clean extraction via Gemini on Flask backend
      let extracted;
      try {
        extracted = await extractEmailFields(currentEmailData.emailHTML || currentEmailData.fullHTML);
      } catch (err) {
        updateScanStep(2, 'failed');
        throw err;
      }

      // Finish Step 2
      updateScanStep(2, 'done');

      // Populate editable fields
      document.getElementById('confirmSender').value = extracted.sender || '';
      document.getElementById('confirmSubject').value = extracted.subject || '';
      document.getElementById('confirmBody').value = extracted.body || '';

      // Close scanner loading and show Confirmation Panel
      loadingOverlay.style.display = 'none';
      document.querySelector('.scan-radar-wrapper').style.display = 'none';
      document.getElementById('diagnosticsPanel').style.display = 'none';
      document.getElementById('confirmationPanel').style.display = 'block';

      showToast('Email content parsed. Please verify details.', 'info');
    } else {
      updateScanStep(2, 'failed');
      throw new Error('No email content could be found. Open an email thread.');
    }
  } catch (error) {
    console.error('Scan error:', error);
    let msg = error.message || 'Extraction failed.';
    showToast(msg, 'warning');
    
    // Hold loading screen for 2.2 seconds to allow reading which step failed
    await new Promise(resolve => setTimeout(resolve, 2200));
    loadingOverlay.style.display = 'none';
  } finally {
    if (radarEl) radarEl.classList.remove('scanning');
  }
});
// Confirmation Cancel Handler
document.getElementById('confirmCancel').addEventListener('click', () => {
  document.getElementById('confirmationPanel').style.display = 'none';
  document.querySelector('.scan-radar-wrapper').style.display = 'flex';
  showToast('Scan cancelled', 'info');
});

// Confirmation Send/Analyze Handler
document.getElementById('confirmSend').addEventListener('click', async () => {
  const senderVal = document.getElementById('confirmSender').value;
  const subjectVal = document.getElementById('confirmSubject').value;
  const bodyVal = document.getElementById('confirmBody').value;

  loadingOverlay.style.display = 'flex';

  // Mark step 1 and 2 as done, and start step 3
  updateScanStep(1, 'done');
  updateScanStep(2, 'done');
  updateScanStep(3, 'active');

  // Timed visual transitions for steps 4 and 5 while waiting for network
  let step3Timeout, step4Timeout;
  let currentActiveStep = 3;

  step3Timeout = setTimeout(() => {
    updateScanStep(3, 'done');
    updateScanStep(4, 'active');
    currentActiveStep = 4;
  }, 500);

  step4Timeout = setTimeout(() => {
    updateScanStep(4, 'done');
    updateScanStep(5, 'active');
    currentActiveStep = 5;
  }, 1000);

  try {
    const apiUrl = new URL(settings.apiEndpoint);
    const analyzeUrl = `${apiUrl.origin}/analyze`;

    const response = await fetch(analyzeUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email_content: bodyVal,
        subject: subjectVal,
        sender: senderVal,
        model: 'random_forest'
      })
    });

    // Clear step transition timeouts
    clearTimeout(step3Timeout);
    clearTimeout(step4Timeout);

    if (!response.ok) {
      updateScanStep(currentActiveStep, 'failed');
      const errorText = await response.text();
      throw new Error(`API error (${response.status}): ${errorText}`);
    }

    const result = await response.json();
    if (result.success && result.analysis) {
      // Complete all steps
      updateScanStep(3, 'done');
      updateScanStep(4, 'done');
      updateScanStep(5, 'done');

      const analysis = result.analysis;
      const ml = analysis.ml_prediction || {};
      
      const totalUrls = analysis.url_analysis?.total_urls || 0;
      const urlRisk = analysis.url_analysis?.risk || 'LOW';
      const senderRisk = analysis.sender_analysis?.risk || 'LOW';
      const socialEngCount = analysis.social_engineering?.techniques_detected || 0;
      
      const modules = {
        content: analysis.phishing_probability || 0,
        url: totalUrls > 0 ? (urlRisk === 'HIGH' ? 0.9 : urlRisk === 'MEDIUM' ? 0.5 : 0.2) : 0.0,
        header: senderRisk === 'HIGH' ? 0.9 : senderRisk === 'MEDIUM' ? 0.5 : 0.1,
        attachment: (currentEmailData && currentEmailData.attachments && currentEmailData.attachments.length > 0) ? 0.6 : 0.0,
        behavioral: Math.min(1.0, socialEngCount / 4.0)
      };
      
      const scanResult = {
        isPhishing: analysis.phishing_probability >= 0.5,
        confidence: analysis.phishing_probability || 0,
        subject: subjectVal || 'No Subject',
        timestamp: Date.now(),
        modules: modules,
        risk_level: analysis.risk_level || 'Low',
        analysis: analysis,
        formatted_report: result.formatted_report,
        html_report: result.html_report
      };

      updateStats(scanResult.isPhishing);
      saveScanResult(scanResult);

      if (settings.showNotifications) {
        showChromeNotification(scanResult);
      }

      loadRecentResults();
      
      // Hide confirmation view, show diagnostics
      document.getElementById('confirmationPanel').style.display = 'none';
      showDiagnostics(scanResult);

      if (scanResult.isPhishing) {
        showToast('Phishing threat detected!', 'threat');
      } else {
        showToast('Email verified as safe', 'safe');
      }
    } else {
      updateScanStep(currentActiveStep, 'failed');
      throw new Error(result.error || 'Invalid API response structure');
    }
  } catch (error) {
    console.error('Confirm scan error:', error);
    updateScanStep(currentActiveStep, 'failed');
    let msg = error.message || 'Analysis failed.';
    showToast(msg, 'warning');
    
    // Hold loading screen for 2.2 seconds to allow reading which step failed
    await new Promise(resolve => setTimeout(resolve, 2200));
  } finally {
    loadingOverlay.style.display = 'none';
    if (radarEl) radarEl.classList.remove('scanning');
  }
});

function renderDetailedReportUI(result) {
  const reportSection = document.getElementById('detailedReportSection');
  if (!reportSection) return;

  reportSection.style.display = 'block';

  const analysis = result.analysis || {};
  
  // 1. Render Red Flags
  const redFlagsList = document.getElementById('redFlagsList');
  redFlagsList.innerHTML = '';
  if (analysis.red_flags && analysis.red_flags.length > 0) {
    analysis.red_flags.forEach(flag => {
      const severityClass = flag.severity === 'HIGH' ? 'flag-high' : flag.severity === 'MEDIUM' ? 'flag-medium' : 'flag-low';
      const severityLabelClass = flag.severity === 'HIGH' ? 'sev-high' : flag.severity === 'MEDIUM' ? 'sev-medium' : 'sev-low';
      
      const flagEl = document.createElement('div');
      flagEl.className = `red-flag-card ${severityClass}`;
      flagEl.innerHTML = `
        <div class="red-flag-header">
          <span class="red-flag-title">${flag.type}</span>
          <span class="red-flag-severity ${severityLabelClass}">${flag.severity}</span>
        </div>
        <div class="red-flag-desc">${flag.description}</div>
        <div class="red-flag-indicator">${flag.indicator}</div>
      `;
      redFlagsList.appendChild(flagEl);
    });
  } else {
    redFlagsList.innerHTML = '<div style="font-size: 10.5px; color: var(--text-dim); text-align: center; padding: 10px;">No critical red flags detected.</div>';
  }

  // 2. Render Social Engineering Techniques
  const socialEngList = document.getElementById('socialEngList');
  socialEngList.innerHTML = '';
  const socialDetails = analysis.social_engineering?.details || [];
  if (socialDetails.length > 0) {
    socialDetails.forEach(tech => {
      const tagEl = document.createElement('span');
      tagEl.className = 'tech-tag';
      tagEl.textContent = tech.technique;
      tagEl.title = tech.description;
      socialEngList.appendChild(tagEl);
    });
  } else {
    socialEngList.innerHTML = '<div style="font-size: 10.5px; color: var(--text-dim); text-align: center; padding: 10px; width: 100%;">No social engineering techniques found.</div>';
  }

  // 3. Render Recommended Actions
  const recommendationsList = document.getElementById('recommendationsList');
  recommendationsList.innerHTML = '';
  const recommendations = analysis.recommended_actions || [];
  if (recommendations.length > 0) {
    recommendations.forEach(rec => {
      const prioClass = rec.priority === 'CRITICAL' ? 'pri-critical' : rec.priority === 'HIGH' ? 'pri-high' : rec.priority === 'MEDIUM' ? 'pri-medium' : 'pri-low';
      
      const recEl = document.createElement('div');
      recEl.className = 'rec-item';
      
      let stepsHtml = '';
      if (rec.steps && rec.steps.length > 0) {
        stepsHtml = `
          <div class="rec-steps">
            ${rec.steps.map(step => `<div class="rec-step">${step}</div>`).join('')}
          </div>
        `;
      }

      recEl.innerHTML = `
        <div class="rec-header">
          <span class="rec-bullet">▶</span>
          <span class="rec-action">${rec.action}</span>
          <span class="rec-priority ${prioClass}">${rec.priority}</span>
        </div>
        ${stepsHtml}
      `;
      recommendationsList.appendChild(recEl);
    });
  } else {
    recommendationsList.innerHTML = '<div style="font-size: 10.5px; color: var(--text-dim); text-align: center; padding: 10px;">No specific recommendations required.</div>';
  }

  // 4. Render Employee Awareness Advice (Bonus)
  const awarenessAdviceBox = document.getElementById('awarenessAdviceBox');
  awarenessAdviceBox.innerHTML = '';
  const awareness = analysis.employee_awareness || {};
  const learningPoints = awareness.learning_points || [];
  
  if (learningPoints.length > 0) {
    learningPoints.forEach(point => {
      const lpEl = document.createElement('div');
      lpEl.className = 'learning-point';
      lpEl.innerHTML = `
        <div class="lp-topic">💡 ${point.topic}</div>
        <div class="lp-lesson">${point.lesson}</div>
        <div class="lp-tip"><strong>Awareness Tip:</strong> ${point.tip}</div>
      `;
      awarenessAdviceBox.appendChild(lpEl);
    });
  } else {
    const general = awareness.general_advice || [];
    if (general.length > 0) {
      const generalHtml = general.slice(0, 3).map(adv => `<div style="margin-bottom: 4px;">${adv}</div>`).join('');
      awarenessAdviceBox.innerHTML = generalHtml;
    } else {
      awarenessAdviceBox.innerHTML = '<div style="font-size: 10.5px; color: var(--text-dim); text-align: center;">Vigilance and regular training are advised.</div>';
    }
  }
}
// ═══════════════════════════════════════════════════════════
// API ANALYSIS
// ═══════════════════════════════════════════════════════════
async function analyzeEmail(emailData) {
  try {
    let payload;
    
    // Check if we are using the extract-and-analyze endpoint
    if (settings.apiEndpoint.includes('/extract-and-analyze')) {
      payload = {
        page_html: emailData.emailHTML || emailData.fullHTML || '',
        model: 'random_forest'
      };
    } else {
      payload = {
        email_content: emailData.body || '',
        subject: emailData.subject || '',
        sender: emailData.sender || '',
        model: 'random_forest'
      };
    }
    
    const response = await fetch(settings.apiEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error (${response.status}): ${errorText}`);
    }

    const result = await response.json();
    if (result.success && result.analysis) {
      const analysis = result.analysis;
      const ml = analysis.ml_prediction || {};
      
      // Calculate modules breakdown scores based on real backend analysis details
      const totalUrls = analysis.url_analysis?.total_urls || 0;
      const urlRisk = analysis.url_analysis?.risk || 'LOW';
      const senderRisk = analysis.sender_analysis?.risk || 'LOW';
      const socialEngCount = analysis.social_engineering?.techniques_detected || 0;
      
      const modules = {
        content: analysis.phishing_probability || 0,
        url: totalUrls > 0 ? (urlRisk === 'HIGH' ? 0.9 : urlRisk === 'MEDIUM' ? 0.5 : 0.2) : 0.0,
        header: senderRisk === 'HIGH' ? 0.9 : senderRisk === 'MEDIUM' ? 0.5 : 0.1,
        attachment: (emailData.attachments && emailData.attachments.length > 0) ? 0.6 : 0.0,
        behavioral: Math.min(1.0, socialEngCount / 4.0)
      };
      
      return {
        isPhishing: analysis.phishing_probability >= 0.5,
        confidence: analysis.phishing_probability || 0,
        subject: emailData.subject || 'No Subject',
        timestamp: Date.now(),
        modules: modules,
        risk_level: analysis.risk_level || 'Low',
        analysis: analysis,
        formatted_report: result.formatted_report,
        html_report: result.html_report
      };
    } else {
      throw new Error(result.error || 'Invalid API response structure');
    }
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// ═══════════════════════════════════════════════════════════
// DIAGNOSTICS DISPLAY — Animated gauge & progress bars
// ═══════════════════════════════════════════════════════════
function showDiagnostics(result) {
  const panel = document.getElementById('diagnosticsPanel');
  if (!panel) return;

  panel.style.display = 'block';
  currentFormattedReport = result.formatted_report || '';
  currentHtmlReport = result.html_report || '';

  // Animated risk percentage
  const overallRisk = document.getElementById('overallRiskValue');
  const riskPct = Math.round(result.confidence * 100);

  // Animate the number
  animateValue(overallRisk, 0, riskPct, 1200);

  // SVG arc gauge animation
  const arcFill = document.getElementById('gaugeArcFill');
  if (arcFill) {
    const circumference = 2 * Math.PI * 52; // ~326.73
    const offset = circumference - (riskPct / 100) * circumference;
    arcFill.style.strokeDashoffset = offset;

    // Color based on threat level
    if (result.isPhishing || riskPct > 60) {
      arcFill.style.stroke = 'var(--danger-color)';
      overallRisk.style.color = 'var(--danger-color)';
    } else if (riskPct > 35) {
      arcFill.style.stroke = 'var(--warning-color)';
      overallRisk.style.color = 'var(--warning-color)';
    } else {
      arcFill.style.stroke = 'var(--success-color)';
      overallRisk.style.color = 'var(--success-color)';
    }
  }

  // Verdict badge
  const verdictBadge = document.getElementById('verdictBadge');
  if (verdictBadge) {
    if (result.isPhishing) {
      verdictBadge.textContent = 'THREAT';
      verdictBadge.className = 'verdict-badge threat';
    } else if (result.confidence > 0.4) {
      verdictBadge.textContent = 'CAUTION';
      verdictBadge.className = 'verdict-badge caution';
    } else {
      verdictBadge.textContent = 'SAFE';
      verdictBadge.className = 'verdict-badge';
    }
  }

  // Modules breakdown with staggered animation
  const mods = result.modules || { content: 0, url: 0, header: 0, attachment: 0, behavioral: 0 };
  const mappings = [
    { fill: 'riskContentFill', val: 'riskContentVal', score: mods.content },
    { fill: 'riskUrlFill', val: 'riskUrlVal', score: mods.url },
    { fill: 'riskHeaderFill', val: 'riskHeaderVal', score: mods.header },
    { fill: 'riskAttachmentFill', val: 'riskAttachmentVal', score: mods.attachment },
    { fill: 'riskBehavioralFill', val: 'riskBehavioralVal', score: mods.behavioral }
  ];

  mappings.forEach((item, index) => {
    setTimeout(() => {
      const fillEl = document.getElementById(item.fill);
      const valEl = document.getElementById(item.val);

      if (fillEl && valEl) {
        const pct = Math.round(item.score * 100);
        animateValue(valEl, 0, pct, 800, '%');
        fillEl.style.width = `${pct}%`;

        // Color coding
        if (pct > 70) {
          fillEl.style.background = 'var(--danger-color)';
          fillEl.style.boxShadow = '0 0 8px rgba(239, 68, 68, 0.4)';
        } else if (pct > 30) {
          fillEl.style.background = 'var(--warning-color)';
          fillEl.style.boxShadow = '0 0 8px rgba(245, 158, 11, 0.4)';
        } else {
          fillEl.style.background = 'var(--success-color)';
          fillEl.style.boxShadow = '0 0 8px rgba(16, 185, 129, 0.4)';
        }
      }
    }, index * 150);
  });
  // Render detailed phishing analysis report
  if (result.analysis) {
    renderDetailedReportUI(result);
  } else {
    const reportSection = document.getElementById('detailedReportSection');
    if (reportSection) reportSection.style.display = 'none';
  }
}

// Animate a numeric value display
function animateValue(element, start, end, duration, suffix = '%') {
  const startTime = performance.now();
  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (end - start) * eased);
    element.textContent = `${current}${suffix}`;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ═══════════════════════════════════════════════════════════
// STATISTICS
// ═══════════════════════════════════════════════════════════
function updateStats(isPhishing) {
  chromeStorageGet('local', ['stats'], (result) => {
    const stats = result.stats || { safe: 0, threats: 0 };

    if (isPhishing) {
      stats.threats++;
      animateCounter(threatCount, stats.threats);
    } else {
      stats.safe++;
      animateCounter(safeCount, stats.safe);
    }

    chromeStorageSet('local', { stats });
  });
}

function saveScanResult(result) {
  chromeStorageGet('local', ['recentScans'], (data) => {
    const scans = data.recentScans || [];
    scans.unshift(result);
    if (scans.length > 50) scans.pop();
    chromeStorageSet('local', { recentScans: scans });
  });
}

function showChromeNotification(result) {
  if (result.isPhishing) {
    try {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: '⚠️ Phishing Threat Detected!',
        message: `This email appears to be phishing (${Math.round(result.confidence * 100)}% confidence)`,
        priority: 2
      });
    } catch (e) {
      console.warn('Notifications API unavailable:', e);
    }
  }
}

// ═══════════════════════════════════════════════════════════
// SETTINGS SAVE — With animated feedback
// ═══════════════════════════════════════════════════════════
saveSettingsBtn.addEventListener('click', () => {
  settings.autoScan = autoScanCheckbox.checked;
  settings.showNotifications = showNotificationsCheckbox.checked;
  settings.darkOverlay = darkOverlayCheckbox ? darkOverlayCheckbox.checked : true;
  settings.apiEndpoint = apiEndpointInput.value;

  applyOverlayTheme();
  chromeStorageSet('sync', { settings }, () => {
    // Animated save feedback
    saveSettingsBtn.innerHTML = `
      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      Settings Saved!
    `;
    saveSettingsBtn.style.borderColor = 'rgba(16, 185, 129, 0.4)';
    saveSettingsBtn.style.color = 'var(--success-color)';

    showToast('Configuration saved successfully', 'info');

    setTimeout(() => {
      saveSettingsBtn.innerHTML = `
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
        </svg>
        Save Configuration
      `;
      saveSettingsBtn.style.borderColor = '';
      saveSettingsBtn.style.color = '';
    }, 2000);
  });
});

// ═══════════════════════════════════════════════════════════
// TAB NAVIGATION — Animated transitions
// ═══════════════════════════════════════════════════════════
document.querySelectorAll('.nav-item').forEach(button => {
  button.addEventListener('click', () => {
    // Deactivate all
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');

    // Animate tab content
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    const targetTabId = button.dataset.tab;
    const targetPane = document.getElementById(targetTabId);
    if (targetPane) {
      targetPane.classList.add('active');

      // Generate heatmap when stats tab opens
      if (targetTabId === 'tab-stats') {
        generateHeatmap();
      }
    }
  });
});

// ═══════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════
loadRecentResults();
generateHeatmap();

const downloadReportBtn = document.getElementById('downloadReportBtn');
if (downloadReportBtn) {
  downloadReportBtn.addEventListener('click', () => {
    if (!currentHtmlReport) {
      showToast('No active report available to download', 'warning');
      return;
    }
    const blob = new Blob([currentHtmlReport], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const element = document.createElement('a');
    element.setAttribute('href', url);
    element.setAttribute('download', `phishguard_report_${Date.now()}.html`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    URL.revokeObjectURL(url);
    showToast('Report downloaded successfully', 'safe');
  });
}
// Show welcome toast on first open with slight delay for dramatic effect
setTimeout(() => {
  showToast('PhishGuard shield is active', 'info', 2500);
}, 800);
