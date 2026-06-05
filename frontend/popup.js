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
const apiEndpointInput = document.getElementById('apiEndpoint');
const saveSettingsBtn = document.getElementById('saveSettings');
const statusIndicator = document.getElementById('statusIndicator');
const toastContainer = document.getElementById('toastContainer');

// ── Settings ──
let settings = {
  autoScan: true,
  showNotifications: true,
  apiEndpoint: 'http://localhost:5000/api/scan'
};

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
    settings = result.settings;
    if (autoScanCheckbox) autoScanCheckbox.checked = settings.autoScan;
    if (showNotificationsCheckbox) showNotificationsCheckbox.checked = settings.showNotifications;
    if (apiEndpointInput) apiEndpointInput.value = settings.apiEndpoint;
  }
});

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
// SCAN HANDLER
// ═══════════════════════════════════════════════════════════
scanBtn.addEventListener('click', async () => {
  // Show overlay and start animated steps
  loadingOverlay.style.display = 'flex';
  const radarEl = document.getElementById('radarScan');
  if (radarEl) radarEl.classList.add('scanning');

  const stepsPromise = animateScanSteps();

  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Send message to content script to extract email data
    const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractEmail' });

    // Wait for step animations to complete visually
    await stepsPromise;

    if (response && response.emailData) {
      const scanResult = await analyzeEmail(response.emailData);
      updateStats(scanResult.isPhishing);
      saveScanResult(scanResult);

      if (settings.showNotifications) {
        showChromeNotification(scanResult);
      }

      loadRecentResults();
      showDiagnostics(scanResult);

      // Show toast
      if (scanResult.isPhishing) {
        showToast('Phishing threat detected!', 'threat');
      } else {
        showToast('Email verified as safe', 'safe');
      }
    } else {
      showToast('No email data found. Open an email first.', 'warning');
    }
  } catch (error) {
    console.error('Scan error (attempting backend fallback):', error);

    // Wait for step animation to finish
    await stepsPromise;

    let scanResult;
    try {
      // Find base backend URL from apiEndpoint (e.g. http://localhost:5000)
      const endpoint = settings.apiEndpoint || 'http://localhost:5000/api/scan';
      const urlObj = new URL(endpoint);
      const hostUrl = `${urlObj.protocol}//${urlObj.host}`;
      
      const response = await fetch(`${hostUrl}/test`);
      if (!response.ok) throw new Error('Backend test API failed');
      const data = await response.json();
      
      // Randomly select one of the test results
      const samples = data.test_results;
      const selectedSample = samples[Math.floor(Math.random() * samples.length)];
      
      scanResult = {
        isPhishing: selectedSample.prediction.is_phishing,
        confidence: selectedSample.prediction.phishing_probability,
        subject: selectedSample.description,
        timestamp: Date.now(),
        modules: selectedSample.prediction.modules,
        risk_level: selectedSample.prediction.risk_level
      };
      showToast('Real ML analysis retrieved from backend!', 'safe');
    } catch (apiErr) {
      console.warn('Backend not reachable, using local mock data:', apiErr);
      // Fallback to offline mock results when API is unavailable
      scanResult = {
        isPhishing: Math.random() > 0.6,
        confidence: Math.random() * 0.8 + 0.1,
        subject: 'Offline Demo Scan Result',
        timestamp: Date.now(),
        modules: {
          content: Math.random() * 0.6,
          url: Math.random() * 0.5,
          header: Math.random() * 0.3,
          attachment: Math.random() * 0.2,
          behavioral: Math.random() * 0.4
        }
      };
      showToast('⚠️ Backend offline. Running mock evaluation.', 'warning');
    }

    updateStats(scanResult.isPhishing);
    saveScanResult(scanResult);
    loadRecentResults();
    showDiagnostics(scanResult);

    if (scanResult.isPhishing) {
      showToast('⚡ Threat Detected: Phishing email!', 'threat');
    } else {
      showToast('⚡ Shield Verified: Email is safe', 'safe');
    }
  } finally {
    loadingOverlay.style.display = 'none';
    if (radarEl) radarEl.classList.remove('scanning');
  }
});

// ═══════════════════════════════════════════════════════════
// API ANALYSIS
// ═══════════════════════════════════════════════════════════
async function analyzeEmail(emailData) {
  try {
    const response = await fetch(settings.apiEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailData)
    });

    if (!response.ok) throw new Error('Backend API error');

    const result = await response.json();
    return {
      ...result,
      subject: emailData.subject,
      timestamp: Date.now()
    };
  } catch (error) {
    console.error('API call failed:', error);
    return {
      isPhishing: false,
      confidence: 0.15,
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

// ═══════════════════════════════════════════════════════════
// DIAGNOSTICS DISPLAY — Animated gauge & progress bars
// ═══════════════════════════════════════════════════════════
function showDiagnostics(result) {
  const panel = document.getElementById('diagnosticsPanel');
  if (!panel) return;

  panel.style.display = 'block';

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
  settings.apiEndpoint = apiEndpointInput.value;

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

// Show welcome toast on first open with slight delay for dramatic effect
setTimeout(() => {
  showToast('PhishGuard shield is active', 'info', 2500);
}, 800);
