# 🚀 Quick Start Guide

Get up and running with the Phishing Detection Assistant in 10 minutes!

---

## Step 1: Clone the Repository (2 minutes)

```bash
git clone https://github.com/Ajinkya-Furange-Patil/Phishing-Detection-Assistant.git
cd Phishing-Detection-Assistant
```

---

## Step 2: Set Up Python Environment (3 minutes)

### Option A: Using virtual environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option B: Direct installation
```bash
pip install -r requirements.txt
```

---

## Step 3: Download Essential Datasets (5 minutes)

### Quick Download (Minimum Viable Dataset)

```python
# Create a file: download_minimal.py
"""
Minimal dataset downloader - gets you started quickly
"""

from datasets import load_dataset
from ucimlrepo import fetch_ucirepo
import os

# Create datasets directory
os.makedirs('datasets', exist_ok=True)

print("Downloading Enron Corpus (legitimate emails)...")
enron = load_dataset("enron_emails")
enron.save_to_disk("datasets/enron")
print("✓ Enron downloaded")

print("\nDownloading PhiUSIIL URL Dataset...")
phiusiil = fetch_ucirepo(id=967)
phiusiil.data.features.to_csv('datasets/phiusiil_features.csv', index=False)
phiusiil.data.targets.to_csv('datasets/phiusiil_labels.csv', index=False)
print("✓ PhiUSIIL downloaded")

print("\n✓ Minimal dataset setup complete!")
print("For full datasets, see DATASETS.md")
```

Run it:
```bash
python download_minimal.py
```

---

## Step 4: Verify Installation

```python
# Create: test_setup.py
"""
Test if everything is installed correctly
"""

print("Testing imports...")

try:
    import pandas as pd
    print("✓ pandas")
except:
    print("✗ pandas - run: pip install pandas")

try:
    import numpy as np
    print("✓ numpy")
except:
    print("✗ numpy - run: pip install numpy")

try:
    import sklearn
    print("✓ scikit-learn")
except:
    print("✗ scikit-learn - run: pip install scikit-learn")

try:
    import torch
    print("✓ pytorch")
except:
    print("✗ pytorch - run: pip install torch")

try:
    import transformers
    print("✓ transformers")
except:
    print("✗ transformers - run: pip install transformers")

try:
    import xgboost
    print("✓ xgboost")
except:
    print("✗ xgboost - run: pip install xgboost")

print("\n✓ Setup verification complete!")
```

Run it:
```bash
python test_setup.py
```

---

## Next Steps

### 1. Read the Documentation
- **Architecture:** See [G-file-formatted.md](G-file-formatted.md)
- **Datasets:** See [DATASETS.md](DATASETS.md)
- **Quick Links:** See [DATASET-LINKS.txt](DATASET-LINKS.txt)

### 2. Download Full Datasets
See [DATASETS.md](DATASETS.md) for complete dataset list

Essential datasets:
- ✅ Enron Corpus (already downloaded)
- ✅ PhiUSIIL URLs (already downloaded)
- ⏳ Nazario Phishing (.mbox files)
- ⏳ Spam Genuine Mail Contents
- ⏳ LLM-Generated Phishing

### 3. Build the System
Follow the implementation roadmap in [G-file-formatted.md](G-file-formatted.md):
- Phase 1: Content Analysis + URL Analysis (Baseline)
- Phase 2: Add Header Analysis
- Phase 3: Add Attachment Analysis
- Phase 4: Add Behavioral Profiling
- Phase 5: Build Stacking Ensemble

---

## Common Issues & Solutions

### Issue: `pip install torch` is slow
**Solution:** Use conda or download pre-built wheel from pytorch.org

### Issue: Can't download from Kaggle
**Solution:** Set up Kaggle API credentials
1. Go to kaggle.com → Account → API → Create Token
2. Place kaggle.json in `~/.kaggle/` (Linux/Mac) or `C:\Users\<user>\.kaggle\` (Windows)

### Issue: Out of memory when loading datasets
**Solution:** Load datasets in chunks or use streaming mode
```python
dataset = load_dataset("enron_emails", streaming=True)
```

### Issue: CUDA/GPU not detected for PyTorch
**Solution:** 
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
# If False, PyTorch will use CPU (slower but works)
```

---

## Project Structure After Setup

```
Phishing-Detection-Assistant/
├── README.md
├── QUICKSTART.md         ← You are here
├── DATASETS.md
├── G-file-formatted.md
├── requirements.txt
├── .gitignore
├── datasets/            ← Your downloaded datasets
│   ├── enron/
│   ├── phiusiil_features.csv
│   └── phiusiil_labels.csv
├── models/              ← Create this for trained models
├── notebooks/           ← Create this for Jupyter notebooks
└── src/                 ← Create this for source code
```

---

## Getting Help

- **Documentation Issues:** Open an issue on GitHub
- **Dataset Problems:** See [DATASETS.md](DATASETS.md) troubleshooting section
- **Code Questions:** Check [G-file-formatted.md](G-file-formatted.md) for implementation details

---

## Ready to Build!

You're all set! Start with:
1. Read [G-file-formatted.md](G-file-formatted.md) Module 1
2. Build your first BERT content analyzer
3. Test with Enron + Nazario data

**Good luck with your phishing detection system! 🎯**
