# Phishing Detection Datasets - Download Guide

Complete list of datasets needed for the 5-module stacking ensemble system.

---

## 📋 Quick Reference Table

| Module | Dataset Name | Size | Format | Priority |
|--------|-------------|------|--------|----------|
| 1 | Enron Email Corpus | 500K emails | CSV/JSON | ⭐⭐⭐ HIGH |
| 1 | Nazario Phishing | 10+ years | .mbox | ⭐⭐⭐ HIGH |
| 1 | PhishingPot | Dynamic | Various | ⭐⭐ MEDIUM |
| 1 | MeAJOR Corpus | 135K emails | Preprocessed | ⭐⭐ MEDIUM |
| 1 | LLM-Generated Phishing | 4K emails | CSV | ⭐⭐⭐ HIGH |
| 2 | ISCX-URL2016 | 57K URLs | CSV | ⭐⭐⭐ HIGH |
| 2 | PhiUSIIL | 236K URLs | CSV | ⭐⭐⭐ HIGH |
| 2 | PILU-90K | 90K URLs | CSV | ⭐⭐ MEDIUM |
| 3 | Nazario (headers) | Same as above | .mbox | ⭐⭐⭐ HIGH |
| 3 | Spam Genuine Mail | 100K emails | CSV | ⭐⭐⭐ HIGH |
| 4 | Simulated Email Dataset | Various | CSV | ⭐⭐⭐ HIGH |
| 5 | SpaPhish | Variable | Annotated | ⭐ LOW |

---

## Module 1: Email Content Analysis

### 1️⃣ Enron Email Corpus (ESSENTIAL)

**Description:** Legitimate corporate emails  
**Size:** ~500,000 emails  
**Class:** Legitimate (0)

**Download Options:**

#### Option A: Hugging Face (RECOMMENDED - EASIEST)
```python
# Install library
pip install datasets

# Download directly in Python
from datasets import load_dataset
dataset = load_dataset("enron_emails")
```


**Website:** https://huggingface.co/datasets/enron_emails

#### Option B: Kaggle
**Website:** https://www.kaggle.com/datasets/wcukierski/enron-email-dataset  
**Format:** CSV files  
**Download:** Requires Kaggle account (free)

#### Option C: Direct Download
**Website:** https://www.cs.cmu.edu/~enron/  
**Note:** Raw format, requires extensive preprocessing

---

### 2️⃣ Nazario Phishing Dataset (ESSENTIAL)

**Description:** Historical phishing emails (2005-2025)  
**Size:** 10+ years of phishing campaigns  
**Class:** Phishing (1)

**Download:**

**Primary Source:** http://monkey.org/~jose/phishing/  
**Alternative:** https://github.com/najarianb/phishing-corpus

**Files to Download:**
- `phishing0.mbox` (2005-2010)
- `phishing1.mbox` (2010-2015)
- `phishing2.mbox` (2015-2020)
- `phishing3.mbox` (2020-2025)

**Format:** .mbox (requires Python `mailbox` library to parse)

**Quick Download Script:**
```bash
wget http://monkey.org/~jose/phishing/phishing0.mbox
wget http://monkey.org/~jose/phishing/phishing1.mbox
wget http://monkey.org/~jose/phishing/phishing2.mbox
wget http://monkey.org/~jose/phishing/phishing3.mbox
```

---

### 3️⃣ PhishingPot (OPTIONAL - Live Data)

**Description:** Live honeypot phishing samples  
**Updates:** Continuous

**Access:**
- Not publicly available as a single dataset
- Alternative: Use PhishTank API for current threats


**PhishTank API:**
- Website: https://www.phishtank.com/
- API: https://www.phishtank.com/api_info.php
- Free tier available

**Alternative - OpenPhish:**
- Website: https://openphish.com/
- Feed: https://openphish.com/feed.txt
- Free hourly updates

---

### 4️⃣ MeAJOR Corpus (OPTIONAL - Aggregated)

**Description:** Pre-aggregated corpus (TREC + Nazario + Nigerian Fraud)  
**Size:** 135,894 samples  
**Advantage:** Already cleaned and preprocessed

**Access:**
- Created by: GECAD, Polytechnic of Porto
- **Paper:** Search "MeAJOR email corpus" on Google Scholar
- **Contact:** May require reaching out to GECAD researchers
- **Alternative:** Build your own by combining TREC spam datasets

**TREC Spam Datasets (Public):**
- TREC 2005: https://plg.uwaterloo.ca/~gvcormac/treccorpus/
- TREC 2006: https://plg.uwaterloo.ca/~gvcormac/treccorpus06/
- TREC 2007: https://plg.uwaterloo.ca/~gvcormac/treccorpus07/

---

### 5️⃣ LLM-Generated Phishing (ESSENTIAL)

**Description:** AI-generated phishing vs human-generated  
**Size:** 4,000 emails  
**Classes:** Human phishing, ChatGPT phishing, WormGPT phishing

**Download:**

**GitHub:** https://github.com/FrancescoGreco/AI-Generated-Phishing-Detection

```bash
git clone https://github.com/FrancescoGreco/AI-Generated-Phishing-Detection.git
```

**Alternative Kaggle Search:** "LLM generated phishing" or "AI phishing detection"

---

## Module 2: URL Analysis

### 1️⃣ ISCX-URL2016 (ESSENTIAL)

**Description:** Multi-class URL dataset  
**Size:** 57,000 URLs


**Categories:**
- 35,300 Benign URLs
- 12,000 Spam URLs
- 10,000 Phishing URLs
- 11,500 Malware URLs

**Download:**

**Official Source:** https://www.unb.ca/cic/datasets/url-2016.html  
**Canadian Institute for Cybersecurity**

**Direct Download Link:**
```
https://www.unb.ca/cic/datasets/url-2016.html
```

**Alternative (Kaggle):**
```
https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset
```

---

### 2️⃣ PhiUSIIL Phishing URL Dataset (ESSENTIAL)

**Description:** Massive URL dataset with 54 features  
**Size:** 235,795 URLs (134,850 legitimate + 100,945 phishing)

**Download:**

**UCI ML Repository:** https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset

**Direct Download:**
```
https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip
```

**Alternative Name:** Search "PhiUSIIL UCI" on Google

**Python Download:**
```python
from ucimlrepo import fetch_ucirepo

# Fetch dataset
phiusiil = fetch_ucirepo(id=967)

# Data
X = phiusiil.data.features
y = phiusiil.data.targets
```

---

### 3️⃣ PILU-90K (OPTIONAL - Login URLs)

**Description:** Specialized for login page URLs  
**Size:** 90,000 URLs (60K legitimate + 30K phishing)

**Access:**
- **Research Paper:** "Phishing Index Login URL Dataset" (Search on Google Scholar)
- May require academic access


**Alternative - Build Your Own:**
- Collect legitimate login URLs from top 1000 websites
- Combine with phishing URLs from PhishTank

**PhishTank Download:**
```bash
# Get current phishing URLs
wget https://data.phishtank.com/data/online-valid.csv
```

---

## Module 3: Header Analysis

### 1️⃣ Nazario Dataset (REUSE from Module 1)

**Why:** .mbox format preserves email headers  
**Contains:** SPF, DKIM, Received headers, routing information

**Already downloaded if you got Module 1 Nazario files**

---

### 2️⃣ Spam Genuine Mail Contents Dataset (ESSENTIAL)

**Description:** Pre-extracted email metadata with authentication results  
**Size:** 100,000 emails (50K legitimate + 50K spam)

**Download:**

**Kaggle (Primary):**
```
https://www.kaggle.com/datasets/isuranga/spam-genuine-mail-contents-dataset
```

**Creator:** Isuranga on Kaggle

**Features Included:**
- SPF results
- DKIM results
- DMARC alignment
- Number of Received headers
- Originating IP
- Return-Path, Reply-To fields

**Download Command:**
```bash
kaggle datasets download -d isuranga/spam-genuine-mail-contents-dataset
```
*(Requires Kaggle CLI: `pip install kaggle`)*

---

## Module 4: Attachment Analysis

### 1️⃣ Simulated Email Dataset (ESSENTIAL)

**Description:** Simulated attachment metadata (safe, no actual malware)  
**Contains:** Entropy scores, macro flags, extension data

**Download:**

**Kaggle (Primary):**
```
https://www.kaggle.com/datasets/vincentamonde/simulated-email-dataset
```

**Creator:** Vincent Amonde

**Alternative Search Terms:**
- "email attachment metadata dataset"
- "malware attachment simulation"

**Note:** If not available, you can create simulated data:

```python
import pandas as pd
import numpy as np

# Create simulated attachment metadata
data = {
    'filename': ['doc.pdf', 'invoice.docm', 'report.exe'],
    'extension': ['.pdf', '.docm', '.exe'],
    'has_macro': [0, 1, 0],
    'is_executable': [0, 0, 1],
    'entropy': [5.2, 7.9, 7.8],
    'mime_type': ['application/pdf', 'application/vnd.ms-word', 'application/x-exe'],
    'label': [0, 1, 1]  # 0=benign, 1=malicious
}

df = pd.DataFrame(data)
df.to_csv('simulated_attachments.csv', index=False)
```

---

## Module 5: Behavioral Profiling

### 1️⃣ SpaPhish Dataset (OPTIONAL - Framework Reference)

**Description:** Spanish phishing with psychological annotations  
**Purpose:** Use framework, adapt to English

**Access:**
- **Research Paper:** "SpaPhish: A Spanish Email Phishing Dataset" (Google Scholar)
- May require academic access
- **Alternative:** Use the framework methodology to annotate Enron + Nazario

---

### 2️⃣ Custom Behavioral Dataset (BUILD YOUR OWN)

**Method:** Use Enron + Nazario with custom annotation

**No separate download needed** - reuse Module 1 datasets and extract behavioral features using:

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Define psychological lexicons
urgency_words = ['urgent', 'immediately', 'asap', 'now', 'hurry']
threat_words = ['suspended', 'terminated', 'blocked', 'legal action']
financial_words = ['payment', 'refund', 'invoice', 'verify account']

def extract_behavioral_features(text):
    text_lower = text.lower()
    return {
        'urgency_score': sum(text_lower.count(w) for w in urgency_words),
        'threat_score': sum(text_lower.count(w) for w in threat_words),
        'financial_score': sum(text_lower.count(w) for w in financial_words)
    }
```

---

## 🚀 Quick Download Script

Save this as `download_datasets.py`:

```python
"""
Automated Dataset Downloader
Downloads all publicly available datasets
"""

import os
import subprocess

def download_datasets():
    print("="*60)
    print("PHISHING DETECTION DATASETS - AUTOMATED DOWNLOAD")
    print("="*60)
    
    # Create datasets directory
    os.makedirs('datasets', exist_ok=True)
    os.chdir('datasets')
    
    # 1. Enron (Hugging Face)
    print("\n[1/7] Downloading Enron Email Corpus...")
    try:
        from datasets import load_dataset
        dataset = load_dataset("enron_emails")
        dataset.save_to_disk("enron_corpus")
        print("✓ Enron downloaded successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Manual download: https://huggingface.co/datasets/enron_emails")
    
    # 2. Nazario Phishing
    print("\n[2/7] Downloading Nazario Phishing...")
    nazario_urls = [
        "http://monkey.org/~jose/phishing/phishing0.mbox",
        "http://monkey.org/~jose/phishing/phishing1.mbox",
        "http://monkey.org/~jose/phishing/phishing2.mbox",
        "http://monkey.org/~jose/phishing/phishing3.mbox"
    ]
    
    for url in nazario_urls:
        try:
            subprocess.run(['wget', url], check=True)
            print(f"✓ Downloaded {url.split('/')[-1]}")
        except:
            print(f"✗ Failed to download {url}")
            print("  Manual download: http://monkey.org/~jose/phishing/")
    
    # 3. LLM-Generated Phishing
    print("\n[3/7] Downloading LLM-Generated Phishing...")
    try:
        subprocess.run([
            'git', 'clone',
            'https://github.com/FrancescoGreco/AI-Generated-Phishing-Detection.git'
        ], check=True)
        print("✓ LLM phishing dataset cloned")
    except:
        print("✗ Git clone failed")
        print("  Manual: https://github.com/FrancescoGreco/AI-Generated-Phishing-Detection")
    
    # 4. PhishTank (Current URLs)
    print("\n[4/7] Downloading PhishTank URLs...")
    try:
        subprocess.run([
            'wget',
            'https://data.phishtank.com/data/online-valid.csv',
            '-O', 'phishtank_current.csv'
        ], check=True)
        print("✓ PhishTank downloaded")
    except:
        print("✗ PhishTank download failed")
        print("  Manual: https://www.phishtank.com/")
    
    # 5. UCI PhiUSIIL
    print("\n[5/7] Downloading PhiUSIIL from UCI...")
    try:
        from ucimlrepo import fetch_ucirepo
        phiusiil = fetch_ucirepo(id=967)
        phiusiil.data.features.to_csv('phiusiil_features.csv', index=False)
        phiusiil.data.targets.to_csv('phiusiil_targets.csv', index=False)
        print("✓ PhiUSIIL downloaded")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Manual: https://archive.ics.uci.edu/dataset/967/")
    
    # 6 & 7. Kaggle datasets (requires authentication)
    print("\n[6/7] Kaggle datasets require manual download:")
    print("  → ISCX-URL2016: https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset")
    print("  → Spam Genuine Mail: https://www.kaggle.com/datasets/isuranga/spam-genuine-mail-contents-dataset")
    print("  → Simulated Attachments: https://www.kaggle.com/datasets/vincentamonde/simulated-email-dataset")
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("Check 'datasets/' folder for downloaded files")
    print("="*60)

if __name__ == "__main__":
    download_datasets()
```

---

## 📦 Installation Requirements

Before running the download script:

```bash
# Python libraries
pip install datasets
pip install ucimlrepo
pip install kaggle
pip install wget

# System tools (if not installed)
# Windows: Install wget from https://eternallybored.org/misc/wget/
# Linux/Mac: Usually pre-installed
```

---

## 🔐 Kaggle Setup

For Kaggle datasets, you need API credentials:

1. Go to https://www.kaggle.com/
2. Click your profile → Account → API → "Create New API Token"
3. Download `kaggle.json`
4. Place it in:
   - **Windows:** `C:\Users\<username>\.kaggle\kaggle.json`
   - **Linux/Mac:** `~/.kaggle/kaggle.json`

```bash
# Set permissions (Linux/Mac)
chmod 600 ~/.kaggle/kaggle.json

# Download dataset
kaggle datasets download -d isuranga/spam-genuine-mail-contents-dataset
```

---

## 📊 Dataset Size Summary

| Dataset | Download Size | Extracted Size | Download Time (est.) |
|---------|--------------|----------------|---------------------|
| Enron | ~500 MB | ~1.5 GB | 5-10 min |
| Nazario | ~200 MB | ~500 MB | 3-5 min |
| LLM Phishing | ~10 MB | ~20 MB | < 1 min |
| PhiUSIIL | ~50 MB | ~100 MB | 1-2 min |
| ISCX-URL | ~20 MB | ~40 MB | < 1 min |
| Spam Genuine | ~100 MB | ~200 MB | 2-3 min |
| **TOTAL** | **~880 MB** | **~2.3 GB** | **15-25 min** |

---

## ✅ Verification Checklist

After downloading, verify you have:

### Module 1: Content Analysis
- [ ] Enron corpus (legitimate emails)
- [ ] Nazario .mbox files (phishing emails)
- [ ] LLM-generated phishing dataset

### Module 2: URL Analysis
- [ ] PhiUSIIL dataset (236K URLs)
- [ ] ISCX-URL2016 or similar URL dataset

### Module 3: Header Analysis
- [ ] Nazario .mbox (reuse from Module 1)
- [ ] Spam Genuine Mail Contents dataset

### Module 4: Attachment Analysis
- [ ] Simulated Email Dataset OR create your own

### Module 5: Behavioral
- [ ] Enron + Nazario (reuse from Module 1)
- [ ] Custom lexicons (build yourself)

---

## 🆘 Troubleshooting

### Problem: Dataset link is broken
**Solution:** Search dataset name + "download" on Google, Kaggle, or GitHub

### Problem: Download is too slow
**Solution:** Use torrent if available, or download during off-peak hours

### Problem: File is corrupted
**Solution:** Verify checksum if provided, re-download

### Problem: Can't access academic datasets
**Solution:** Use alternative datasets or contact dataset authors via email

---

## 📞 Alternative Sources

If primary sources fail:

1. **Papers with Code:** https://paperswithcode.com/datasets
2. **Google Dataset Search:** https://datasetsearch.research.google.com/
3. **GitHub:** Search "phishing dataset", "email spam dataset"
4. **UCI ML Repository:** https://archive.ics.uci.edu/
5. **Kaggle:** https://www.kaggle.com/datasets

---

## 📝 Notes

- ⚠️ Some datasets may require citations in your research
- 🔒 Always check dataset licenses before commercial use
- 🔄 Update PhishTank data regularly for current threats
- 💾 Keep backups of downloaded datasets

---

**Last Updated:** June 2026  
**Document Version:** 1.0

For issues or questions, refer to dataset documentation or contact dataset maintainers.
