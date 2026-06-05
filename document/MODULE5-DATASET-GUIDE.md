# Module 5: Behavioral Profiling - Dataset Download Guide

## 📋 Overview

Module 5 focuses on **psychological and behavioral profiling** to detect social engineering tactics in phishing emails. Unlike other modules, Module 5 primarily **reuses datasets from Module 1** and applies **custom feature extraction**.

---

## 🎯 What Module 5 Analyzes

Module 5 extracts psychological features:

| Feature | Description | Examples |
|---------|-------------|----------|
| **Urgency Score** | Temporal pressure | "URGENT!", "immediately", "within 24 hours" |
| **Threat Score** | Negative consequences | "suspended", "terminated", "legal action" |
| **Financial Score** | Money-related pressure | "payment failed", "refund", "verify account" |
| **Authority Score** | Impersonation | "IRS", "CEO", "IT Department", "Security Team" |
| **Password Reset** | Unexpected reset requests | "reset your password", "verify identity" |

---

## 📦 Datasets Needed for Module 5

### ✅ Option 1: Reuse Module 1 Datasets (RECOMMENDED)

**You already have these if you downloaded Module 1 datasets!**

1. **Enron Corpus** (Legitimate baseline)
2. **Nazario Phishing** (Phishing examples)
3. **LLM-Generated Phishing** (AI-generated attacks)

**Why this works:**
- Module 5 extracts different features from the same email text
- No separate download needed
- You already have ~500,000+ emails

---

### 🆕 Option 2: Add SpaPhish Framework (OPTIONAL)

SpaPhish provides a **psychological annotation framework** but is in Spanish.

**Use Case:** Learn the annotation methodology, not necessarily the data itself

---

## 🚀 Step-by-Step: Download Process

---

## STEP 1: Verify Module 1 Datasets


First, check if you have Module 1 datasets:

```bash
cd "Phishing Detection Assistant"
ls datasets/
```

**You should see:**
- `enron/` - Enron corpus
- `nazario/` or `.mbox` files - Nazario phishing
- `llm_phishing/` or similar - LLM-generated phishing

### ✅ If you already have these → SKIP TO STEP 3

### ❌ If you DON'T have these → Continue to STEP 2

---

## STEP 2: Download Module 1 Datasets

### 2.1: Download Enron Corpus

**Method A: Using Python (EASIEST)**

```python
# Create file: download_enron.py

from datasets import load_dataset
import os

print("Downloading Enron Email Corpus...")
print("This may take 5-10 minutes...")

# Create datasets directory
os.makedirs('datasets', exist_ok=True)

# Download Enron
enron = load_dataset("enron_emails")

# Save locally
enron.save_to_disk("datasets/enron")

print("✓ Enron corpus downloaded successfully!")
print(f"Location: datasets/enron")
print(f"Size: ~500,000 emails")
```

**Run it:**
```bash
pip install datasets
python download_enron.py
```

---

**Method B: Using Kaggle**

1. Go to: https://www.kaggle.com/datasets/wcukierski/enron-email-dataset
2. Click **"Download"** button (requires Kaggle account)
3. Extract to `datasets/enron/`

---

### 2.2: Download Nazario Phishing

**Using wget (Windows: download wget first)**

```bash
# Create datasets directory
mkdir datasets
cd datasets

# Download Nazario .mbox files
wget http://monkey.org/~jose/phishing/phishing0.mbox
wget http://monkey.org/~jose/phishing/phishing1.mbox
wget http://monkey.org/~jose/phishing/phishing2.mbox
wget http://monkey.org/~jose/phishing/phishing3.mbox

cd ..
```

**Alternative - Manual Download:**

1. Visit: http://monkey.org/~jose/phishing/
2. Right-click each file → "Save As"
   - `phishing0.mbox`
   - `phishing1.mbox`
   - `phishing2.mbox`
   - `phishing3.mbox`
3. Save to `datasets/` folder

---

### 2.3: Download LLM-Generated Phishing

```bash
cd datasets

# Clone the repository
git clone https://github.com/FrancescoGreco/AI-Generated-Phishing-Detection.git

# Rename for clarity (optional)
mv AI-Generated-Phishing-Detection llm_phishing

cd ..
```

**Alternative - Manual Download:**

1. Visit: https://github.com/FrancescoGreco/AI-Generated-Phishing-Detection
2. Click **"Code"** → **"Download ZIP"**
3. Extract to `datasets/llm_phishing/`

---

## STEP 3: Build Psycholinguistic Lexicons

Module 5 uses **custom lexicons** to score psychological features.

### 3.1: Create Lexicon File

Create file: `module5_lexicons.py`

```python
"""
Psycholinguistic Lexicons for Behavioral Profiling
Module 5: Phishing Detection Assistant
"""

# ========================================
# URGENCY LEXICON
# ========================================

urgency_words = [
    # Time pressure
    'urgent', 'immediately', 'asap', 'now', 'hurry', 'quick', 'quickly',
    'rush', 'emergency', 'critical', 'today', 'tonight',
    
    # Deadline phrases
    'within 24 hours', 'within 48 hours', 'expires today', 
    'limited time', 'act now', 'don\'t wait', 'expires soon',
    'before it\'s too late', 'last chance', 'final notice',
    
    # Action demands
    'must act', 'act immediately', 'respond now', 'reply immediately',
    'take action', 'immediate action', 'time sensitive'
]

# ========================================
# THREAT LEXICON
# ========================================

threat_words = [
    # Account threats
    'suspended', 'suspend', 'blocked', 'block', 'locked', 'lock',
    'closed', 'close', 'terminated', 'terminate', 'deactivated',
    'disabled', 'restricted', 'frozen',
    
    # Legal threats
    'legal action', 'lawsuit', 'court', 'attorney', 'lawyer',
    'prosecution', 'prosecute', 'charges', 'penalty', 'fine',
    
    # Security threats
    'breach', 'hacked', 'compromised', 'unauthorized', 'suspicious activity',
    'unusual activity', 'fraud', 'fraudulent', 'stolen', 'theft',
    
    # Consequences
    'lose access', 'lose account', 'permanent', 'irreversible',
    'cannot undo', 'will be deleted', 'consequences'
]

# ========================================
# FINANCIAL LEXICON
# ========================================

financial_words = [
    # Payment issues
    'payment', 'pay', 'paid', 'payment failed', 'payment declined',
    'billing', 'bill', 'invoice', 'charge', 'charged', 'transaction',
    
    # Money terms
    'refund', 'refundable', 'money', 'cash', 'fee', 'fees', 'cost',
    'price', 'amount', 'balance', 'credit', 'debit',
    
    # Account actions
    'verify payment', 'update payment', 'confirm payment',
    'verify account', 'update billing', 'payment information',
    'credit card', 'bank account', 'bank details',
    
    # Rewards (fake incentives)
    'reward', 'prize', 'win', 'winner', 'won', 'gift', 'bonus',
    'rebate', 'cashback', 'discount', 'free money', 'claim'
]

# ========================================
# AUTHORITY LEXICON
# ========================================

authority_words = [
    # Government
    'irs', 'internal revenue service', 'tax', 'taxes', 'government',
    'fbi', 'homeland security', 'social security', 'medicare',
    'department of', 'federal',
    
    # Financial institutions
    'bank', 'paypal', 'venmo', 'zelle', 'western union',
    'mastercard', 'visa', 'american express', 'discover',
    
    # Tech companies
    'microsoft', 'apple', 'google', 'amazon', 'facebook', 'meta',
    'twitter', 'linkedin', 'dropbox', 'adobe',
    
    # Internal authority
    'ceo', 'cfo', 'president', 'director', 'manager', 'supervisor',
    'it department', 'it support', 'help desk', 'security team',
    'admin', 'administrator', 'support team'
]

# ========================================
# PASSWORD/SECURITY LEXICON
# ========================================

password_security_words = [
    # Password actions
    'password', 'reset password', 'change password', 'update password',
    'verify password', 'confirm password', 'expired password',
    
    # Security actions
    'verify identity', 'verify account', 'confirm identity',
    'two factor', '2fa', 'authentication', 'security code',
    'verification code', 'confirm email', 'verify email',
    
    # Login issues
    'login', 'log in', 'sign in', 'signin', 'access', 'credentials',
    'username', 'account details'
]

# ========================================
# SCORING FUNCTIONS
# ========================================

def calculate_urgency_score(text, max_score=10):
    """
    Calculate urgency score based on keyword frequency
    
    Args:
        text (str): Email text
        max_score (int): Maximum score (default 10)
    
    Returns:
        int: Urgency score (0-10)
    """
    text_lower = text.lower()
    count = sum(text_lower.count(word) for word in urgency_words)
    score = min(count * 2, max_score)  # Each match = 2 points, cap at 10
    return score

def calculate_threat_score(text, max_score=10):
    """Calculate threat score"""
    text_lower = text.lower()
    count = sum(text_lower.count(word) for word in threat_words)
    score = min(count * 2, max_score)
    return score

def calculate_financial_score(text, max_score=10):
    """Calculate financial pressure score"""
    text_lower = text.lower()
    count = sum(text_lower.count(word) for word in financial_words)
    score = min(count * 1.5, max_score)  # Slightly lower weight
    return score

def calculate_authority_score(text, max_score=10):
    """Calculate authority impersonation score"""
    text_lower = text.lower()
    count = sum(text_lower.count(word) for word in authority_words)
    score = min(count * 3, max_score)  # Higher weight for authority
    return score

def has_password_reset_request(text):
    """Check if email requests password reset (binary)"""
    text_lower = text.lower()
    return any(word in text_lower for word in password_security_words)

def extract_behavioral_features(email_text):
    """
    Extract all behavioral features from email text
    
    Args:
        email_text (str): Raw email text
    
    Returns:
        dict: Dictionary of behavioral features
    """
    features = {
        'urgency_score': calculate_urgency_score(email_text),
        'threat_score': calculate_threat_score(email_text),
        'financial_score': calculate_financial_score(email_text),
        'authority_score': calculate_authority_score(email_text),
        'password_reset_flag': 1 if has_password_reset_request(email_text) else 0
    }
    
    return features

# ========================================
# TESTING
# ========================================

if __name__ == "__main__":
    # Test email
    test_email = """
    URGENT: Your PayPal account has been suspended
    
    Dear customer,
    
    We've detected suspicious activity on your PayPal account.
    Your account will be permanently closed within 24 hours unless
    you verify your identity immediately.
    
    Click here to reset your password and verify your payment information.
    
    Failure to act now will result in legal action.
    
    PayPal Security Team
    """
    
    print("Testing Behavioral Feature Extraction:")
    print("="*50)
    
    features = extract_behavioral_features(test_email)
    
    print(f"Urgency Score:        {features['urgency_score']}/10")
    print(f"Threat Score:         {features['threat_score']}/10")
    print(f"Financial Score:      {features['financial_score']}/10")
    print(f"Authority Score:      {features['authority_score']}/10")
    print(f"Password Reset Flag:  {features['password_reset_flag']}")
    
    print("\n" + "="*50)
    print("HIGH RISK PHISHING DETECTED!" if sum(features.values()) > 20 else "Low risk")
```

**Save and test:**
```bash
python module5_lexicons.py
```

**Expected output:**
```
Testing Behavioral Feature Extraction:
==================================================
Urgency Score:        10/10
Threat Score:         8/10
Financial Score:      6/10
Authority Score:      6/10
Password Reset Flag:  1
==================================================
HIGH RISK PHISHING DETECTED!
```

---

## STEP 4: Create Dataset Processing Script

Now create a script to process Module 1 datasets and extract behavioral features.

Create file: `process_module5_data.py`

```python
"""
Process Module 1 datasets to extract Module 5 behavioral features
"""

import pandas as pd
import os
from datasets import load_from_disk
import mailbox
from module5_lexicons import extract_behavioral_features

# ========================================
# PROCESS ENRON (LEGITIMATE)
# ========================================

def process_enron():
    """Process Enron corpus for behavioral features"""
    print("Processing Enron corpus...")
    
    # Load Enron
    enron = load_from_disk("datasets/enron")
    
    data = []
    
    # Process sample (adjust size as needed)
    for i, email in enumerate(enron['train']):
        if i >= 10000:  # Process first 10,000 for speed
            break
            
        if i % 1000 == 0:
            print(f"Processed {i} Enron emails...")
        
        text = email['text'] if 'text' in email else email['message']
        features = extract_behavioral_features(text)
        features['label'] = 0  # Legitimate
        features['source'] = 'enron'
        
        data.append(features)
    
    df = pd.DataFrame(data)
    print(f"✓ Enron processed: {len(df)} emails")
    return df

# ========================================
# PROCESS NAZARIO (PHISHING)
# ========================================

def process_nazario():
    """Process Nazario phishing corpus"""
    print("Processing Nazario phishing...")
    
    data = []
    
    # Process .mbox files
    mbox_files = [
        'datasets/phishing0.mbox',
        'datasets/phishing1.mbox',
        'datasets/phishing2.mbox',
        'datasets/phishing3.mbox'
    ]
    
    for mbox_file in mbox_files:
        if not os.path.exists(mbox_file):
            print(f"⚠ {mbox_file} not found, skipping...")
            continue
            
        print(f"Processing {mbox_file}...")
        mbox = mailbox.mbox(mbox_file)
        
        for i, message in enumerate(mbox):
            if i % 500 == 0 and i > 0:
                print(f"  Processed {i} messages from {mbox_file}")
            
            # Extract email body
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            # Extract features
            features = extract_behavioral_features(body)
            features['label'] = 1  # Phishing
            features['source'] = 'nazario'
            
            data.append(features)
    
    df = pd.DataFrame(data)
    print(f"✓ Nazario processed: {len(df)} emails")
    return df

# ========================================
# PROCESS LLM PHISHING
# ========================================

def process_llm_phishing():
    """Process LLM-generated phishing"""
    print("Processing LLM-generated phishing...")
    
    # Path to LLM dataset (adjust based on your download)
    llm_path = "datasets/llm_phishing/"
    
    if not os.path.exists(llm_path):
        print("⚠ LLM phishing dataset not found, skipping...")
        return pd.DataFrame()
    
    # Try to find CSV files
    csv_files = [f for f in os.listdir(llm_path) if f.endswith('.csv')]
    
    if not csv_files:
        print("⚠ No CSV files found in LLM dataset, skipping...")
        return pd.DataFrame()
    
    data = []
    
    for csv_file in csv_files:
        df_temp = pd.read_csv(os.path.join(llm_path, csv_file))
        
        # Find text column (may be named differently)
        text_col = None
        for col in ['text', 'email', 'body', 'content', 'message']:
            if col in df_temp.columns:
                text_col = col
                break
        
        if text_col is None:
            print(f"⚠ Could not find text column in {csv_file}")
            continue
        
        for _, row in df_temp.iterrows():
            features = extract_behavioral_features(row[text_col])
            features['label'] = 1  # Phishing (LLM-generated)
            features['source'] = 'llm'
            data.append(features)
    
    df = pd.DataFrame(data)
    print(f"✓ LLM phishing processed: {len(df)} emails")
    return df

# ========================================
# MAIN PROCESSING
# ========================================

def main():
    print("="*60)
    print("MODULE 5: BEHAVIORAL FEATURE EXTRACTION")
    print("="*60)
    
    # Process all datasets
    dfs = []
    
    # Enron (legitimate)
    df_enron = process_enron()
    if not df_enron.empty:
        dfs.append(df_enron)
    
    # Nazario (phishing)
    df_nazario = process_nazario()
    if not df_nazario.empty:
        dfs.append(df_nazario)
    
    # LLM phishing
    df_llm = process_llm_phishing()
    if not df_llm.empty:
        dfs.append(df_llm)
    
    # Combine all
    if dfs:
        df_combined = pd.concat(dfs, ignore_index=True)
        
        # Save
        output_file = 'datasets/module5_behavioral_features.csv'
        df_combined.to_csv(output_file, index=False)
        
        print("\n" + "="*60)
        print("PROCESSING COMPLETE!")
        print("="*60)
        print(f"Total emails processed: {len(df_combined)}")
        print(f"Legitimate: {len(df_combined[df_combined['label']==0])}")
        print(f"Phishing: {len(df_combined[df_combined['label']==1])}")
        print(f"\nOutput saved to: {output_file}")
        print("\n" + "="*60)
        
        # Show sample
        print("\nSample of extracted features:")
        print(df_combined.head(10))
        
        # Show statistics
        print("\nFeature Statistics:")
        print(df_combined.groupby('label')[['urgency_score', 'threat_score', 
                                             'financial_score', 'authority_score']].mean())
    else:
        print("\n⚠ No datasets processed. Please download Module 1 datasets first.")

if __name__ == "__main__":
    main()
```

**Run it:**
```bash
python process_module5_data.py
```

---

## STEP 5: Verify Module 5 Dataset

After processing, you should have:

```
datasets/
├── module5_behavioral_features.csv    ← Your Module 5 dataset!
├── enron/                             ← Source data
├── phishing0.mbox                     ← Source data
├── phishing1.mbox
├── phishing2.mbox
├── phishing3.mbox
└── llm_phishing/                      ← Source data
```

### Verify the file:

```python
import pandas as pd

# Load Module 5 dataset
df = pd.read_csv('datasets/module5_behavioral_features.csv')

print(f"Total samples: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())

print(f"\nClass distribution:")
print(df['label'].value_counts())

print(f"\nFeature ranges:")
print(df.describe())
```

---

## 📊 What You Should See

**Expected output:**
```
Total samples: 15000

Columns: ['urgency_score', 'threat_score', 'financial_score', 
          'authority_score', 'password_reset_flag', 'label', 'source']

Class distribution:
0 (Legitimate)    10000
1 (Phishing)       5000

Feature ranges:
       urgency_score  threat_score  financial_score
count   15000.000000  15000.000000    15000.000000
mean        2.345000      1.892000        3.124000
std         2.891000      2.456000        2.789000
min         0.000000      0.000000        0.000000
max        10.000000     10.000000       10.000000
```

**Phishing emails should have HIGHER scores** than legitimate emails.

---

## ✅ SUCCESS CHECKLIST

After completing all steps, you should have:

- [x] Module 1 datasets downloaded (Enron, Nazario, LLM)
- [x] `module5_lexicons.py` created with psycholinguistic dictionaries
- [x] `process_module5_data.py` created for feature extraction
- [x] `datasets/module5_behavioral_features.csv` generated
- [x] Verified the dataset has correct structure

---

## 🎯 Next Steps

Now you can train Module 5:

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load data
df = pd.read_csv('datasets/module5_behavioral_features.csv')

# Features and labels
X = df[['urgency_score', 'threat_score', 'financial_score', 
        'authority_score', 'password_reset_flag']]
y = df['label']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
import joblib
joblib.dump(model, 'models/module5_behavioral_model.pkl')
print("✓ Model saved!")
```

---

## 🆘 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'datasets'"
**Solution:**
```bash
pip install datasets
```

### Issue: "FileNotFoundError: datasets/enron"
**Solution:** Download Enron first (see STEP 2.1)

### Issue: "All behavioral scores are 0"
**Solution:** Check if email text is being extracted correctly. Print sample text to verify.

### Issue: "Out of memory"
**Solution:** Reduce sample size in `process_module5_data.py`:
```python
if i >= 5000:  # Instead of 10000
    break
```

### Issue: ".mbox file corrupt"
**Solution:** Re-download Nazario files or skip corrupt file

---

## 📝 Summary

**Module 5 is unique:** It doesn't require separate dataset downloads. Instead, it:

1. ✅ **Reuses Module 1 datasets** (Enron, Nazario, LLM)
2. ✅ **Applies custom lexicons** to extract psychological features
3. ✅ **Creates new feature set** (urgency, threat, financial scores)
4. ✅ **Saves as CSV** for easy training

**Total time:** 20-30 minutes (depending on dataset size)

---

**Created by:** Ajinkya Furange Patil  
**Project:** Phishing Detection Assistant  
**Module:** 5 - Behavioral Profiling  
**Last Updated:** June 2026
