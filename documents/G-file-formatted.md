# Architecting a Modular Stacking Ensemble for Advanced Phishing Detection

## A Comprehensive Dataset and Engineering Blueprint

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Introduction](#introduction)
3. [Architectural Paradigm](#architectural-paradigm)
4. [Module 1: Email Content Analysis](#module-1-email-content-analysis)
5. [Module 2: URL Analysis](#module-2-url-analysis)
6. [Module 3: Header Analysis](#module-3-header-analysis)
7. [Module 4: Attachment Analysis](#module-4-attachment-analysis)
8. [Module 5: Behavioral Profiling](#module-5-behavioral-profiling)
9. [Feature Fusion & Meta-Learner](#feature-fusion-and-meta-learner)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Conclusion](#conclusion)

---

## Executive Summary

The landscape of cyber threat intelligence has undergone a foundational paradigm shift, driven by the escalating complexity of social engineering and technical evasion tactics.

### Current Threat Landscape

**Traditional Approach (Inadequate):**
- Monolithic, heuristic-based filtering algorithms
- Single-algorithm paradigms
- Inadequate for multi-vector attacks

**Modern Threat Tactics:**
- ⚠️ Highly obfuscated payloads
- ⚠️ Algorithmically generated deceptive domains
- ⚠️ Meticulously crafted psychological triggers
- ⚠️ Synthetically generated text powered by **Large Language Models (LLMs)**

### Solution: Multi-Modular Stacking Ensemble

This system employs a **five-tier architecture** that separates detection into specialized modules, each analyzing different attack vectors.

---

## Introduction

### System Architecture Overview

The system classifies electronic communications as **legitimate** or **malicious** using:

**Five Independent Analytical Modules:**
1. 📧 **Content Analysis** - Semantic meaning extraction
2. 🔗 **URL Analysis** - Link obfuscation detection
3. 🔐 **Header Verification** - Authentication & routing analysis
4. 📎 **Attachment Diagnostics** - File metadata heuristics
5. 🧠 **Behavioral Profiling** - Psychological trigger detection

**Final Layer:**
- 🎯 **XGBoost Meta-Learner** - Aggregates all module outputs for final classification


### Key Success Factors

✅ **Quality, structure, and diversity** of training data  
✅ **Progressive implementation** of technology stack  
✅ **Proper feature engineering** for each module  
✅ **Isolated training** to prevent data leakage  

---

## Architectural Paradigm

### Design Philosophy

**Problem with Monolithic Models:**
- Cannot effectively map disparate data types (text, IPs, binary entropy, headers) into a single latent space
- Vulnerable to targeted evasion tactics
- Limited adaptability

**Stacking Ensemble Solution:**
- Deploys **specialized algorithms** for specific data domains
- Forces attackers to evade ALL modules simultaneously
- Provides mathematical robustness through diversity

---

### Email Processing Pipeline

| Tier | Module | Input Type | Algorithm | Output |
|------|--------|------------|-----------|--------|
| 1 | **Content Analysis** | Raw Email Text | BERT/DistilBERT | `bert_score` (0.91) |
| 2 | **URL Analysis** | Embedded Links | Logistic Regression, Random Forest | `url_score` (0.84) |
| 3 | **Header Analysis** | Auth Headers & Routing | Random Forest | `header_score` (0.95) |
| 4 | **Attachment Analysis** | File Metadata | XGBoost | `attachment_score` (0.76) |
| 5 | **Behavioral Features** | Psychological Markers | NLP/Rule-Based | `behavior_score` (0.88) |
| 6 | **Feature Fusion** | 5D Array | Array Construction | `[0.91, 0.84, 0.95, 0.76, 0.88]` |
| 7 | **Meta-Learner** | Fused Array | XGBoost | **Final: 98.2% Phishing** |

### How It Works

1. **Parallel Processing**: Email analyzed by all 5 modules simultaneously
2. **Probability Generation**: Each module outputs a risk score (0.0-1.0)
3. **Feature Fusion**: Scores combined into a single array
4. **Meta-Classification**: XGBoost makes final decision based on pattern of scores

> **Key Insight**: The meta-learner doesn't just average scores—it learns complex patterns. For example, a clean URL + clean attachment but failed headers + urgent language = sophisticated spoofing attack.

---

## Module 1: Email Content Analysis

### 🎯 Objective

Extract **meaning, context, and intent** from unstructured email text.


### 🤖 Models Used

- **BERT** (Bidirectional Encoder Representations from Transformers)
- **DistilBERT** (Lighter, faster variant)

**Why These Models?**
- Process bidirectional context of lexical tokens
- Capture semantic nuances missed by bag-of-words models
- Industry standard for NLP tasks

### 📝 Example Processing

**Input Email:**
> "Your account has been suspended. Click here immediately"

**Processing Steps:**
1. **Tokenization**: Break text into tokens
2. **Semantic Analysis**: Evaluate threat weight of "suspended" + "immediately"
3. **Output**: `phishing_probability = 0.91`

---

### 📊 Required Datasets

#### Dataset 1: **Enron Email Corpus** (Legitimate Baseline)

**📌 Overview:**
- **Size**: ~500,000 emails
- **Source**: Federal Energy Regulatory Commission
- **Contributors**: ~150 Enron senior management employees
- **Class Label**: Legitimate (0)

**✅ Advantages:**

- Authentic workplace communication patterns
- Informal and semi-formal corporate discourse
- Real-world linguistic behavior
- Irreplaceable public corporate dataset

**⚠️ Known Issues & Preprocessing Requirements:**

| Issue | Description | Solution |
|-------|-------------|----------|
| **Data Corruption** | Initial release had severe corruption | Use cleaned versions (CALO Project, SRI, MIT) |
| **Missing Attachments** | All attachments stripped | ❌ Cannot use for Module 4 |
| **Address Normalization** | Invalid addresses converted | Addresses like `user@enron.com`, `no_address@enron.com` |

**🔧 Implementation:**
```python
# Use Hugging Face cleaned distribution
from datasets import load_dataset

dataset = load_dataset("enron_emails")
text_data = dataset['train']['text']
```

---

#### Dataset 2: **Nazario Phishing Dataset** (Historical Phishing)

**📌 Overview:**
- **Source**: monkey.org
- **Format**: `.mbox` files
- **Time Span**: 2005-2025 (over a decade of phishing evolution)

- **Class Label**: Phishing (1)

**✅ Advantages:**
- Historically significant
- Shows evolution of phishing tactics
- Retains full header information (useful for Module 3)

**🔧 Implementation:**
```python
import mailbox

# Parse .mbox format
mbox = mailbox.mbox('nazario_phishing.mbox')
for message in mbox:
    body_text = message.get_payload()
    headers = dict(message.items())
```

**⚠️ Limitation:**
- **Concept Drift Risk**: Historical data may not reflect modern tactics
- **Solution**: Combine with PhishingPot for current threats

---

#### Dataset 3: **PhishingPot** (Live Honeypot Data)

**📌 Overview:**
- **Source**: Live honeypot collection
- **Type**: Real, active phishing samples
- **Updates**: Continuous

**✅ Advantages:**
- Modern threat intelligence
- Counters concept drift

- Reflects contemporary semantic deception
- Keeps model calibrated to current tactics

**⚠️ Security Requirement:**
```python
# MUST anonymize sensitive data
email_text = email_text.replace(honeypot_address, "phishing@pot")
```

---

#### Dataset 4: **MeAJOR Corpus** (Aggregated Dataset)

**📌 Overview:**
- **Created By**: Polytechnic of Porto (GECAD)
- **Size**: 135,894 samples
- **Sources**: TREC-05, TREC-06, TREC-07, Nazario, Nigerian Fraud

**✅ Advantages:**
- Pre-aggregated and cleaned
- Addresses class imbalance
- Ready for deep learning pipelines
- Unified, preprocessed format

**🎯 Use Case**: Ideal for immediate training without extensive preprocessing

---

#### Dataset 5: **LLM-Generated Phishing** (Future-Proofing)

**📌 Overview:**
- **Created By**: FrancescoGreco97
- **Size**: 4,000 emails
- **Categories**:
  - Human-generated (Nazario/Nigerian Fraud)
  - LLM-generated (ChatGPT, WormGPT)


**🚨 Critical Importance:**
- Traditional grammatical errors are vanishing
- AI-generated phishing is grammatically perfect
- Forces model to analyze deeper semantic manipulation

**Training Impact:**
```
Traditional Phishing: "Your acount has ben suspended"  ← Easy to detect
LLM Phishing: "We've noticed unusual activity on your account" ← Requires semantic analysis
```

---

## Module 2: URL Analysis

### 🎯 Objective

Analyze **lexical and structural features** of URLs without visiting them.

### 🤖 Models Used

- **Logistic Regression**
- **Random Forest**
- **XGBoost**

---

### 🔍 Feature Engineering

**Core Features Extracted:**

| Feature | Type | Explanation | Example |
|---------|------|-------------|---------|
| `url_length` | Integer | Phishing URLs padded with excess characters | `34` |
| `num_dots` | Integer | Excessive dots indicate subdomain manipulation | `5` |
| `num_hyphens` | Integer | Used in typosquatting (paypal-login-security.com) | `3` |
| `https_present` | Binary | Absence on financial site = high risk | `0` |
| `domain_age` | Integer | Newly registered domains (days/months) | `2` |
| `num_subdomains` | Integer | Excessive subdomains obfuscate true domain | `4` |
| `ip_address_used` | Binary | Raw IP in URL = major red flag | `1` |

**Example Processing:**
```python
url = "http://paypal-login-security.com"

features = {
    "url_length": 34,
    "num_dots": 2,
    "num_hyphens": 3,
    "https_present": 0,
    "domain_age": 2,
    "ip_address_used": 0
}

# Convert to NumPy array for model
import numpy as np
X = np.array(list(features.values())).reshape(1, -1)
prediction = model.predict_proba(X)[0][1]  # Phishing probability
```

---

### 📊 Required Datasets

#### Dataset 1: **ISCX-URL2016**

**📌 Overview:**
- **Source**: Canadian Institute for Cybersecurity
- **Size**: 57,000 URLs


**Category Breakdown:**
- 35,300 Benign URLs (Alexa top websites)
- 12,000 Spam URLs
- 10,000 Phishing URLs (OpenPhish)
- 11,500 Malware URLs

**✅ Advantages:**
- Multi-class categorization
- Rigorous academic framework
- Focus on lexical obfuscation techniques

---

#### Dataset 2: **PhiUSIIL Phishing URL Dataset**

**📌 Overview:**
- **Source**: UCI Machine Learning Repository (2024)
- **Size**: 235,795 instances
  - 134,850 Legitimate
  - 100,945 Phishing
- **Features**: 54 advanced features

**🚀 Advanced Features:**
- `CharContinuationRate` - Detects algorithmically generated domains
- `TLDLegitimateProb` - Historical reputation of Top-Level Domains
- Goes beyond basic character counts

**✅ Advantages:**
- Massive scale
- Complex derived metrics
- State-of-the-art feature engineering

---

#### Dataset 3: **PILU-90K** (Login URL Specialist)

**📌 Overview:**

- **Size**: 90,000 URLs
  - 60,000 Legitimate (homepages + **login portals**)
  - 30,000 Phishing

**🎯 Critical Problem Solved:**

```
Traditional Training:
Legitimate: www.bank.com ✓
Phishing: www.bank-secure-login.com ✗

Real World:
User receives: www.bank.com/auth/login?session=a8f2k3&redirect=/account
Traditional model: ❌ FLAGS AS SUSPICIOUS (long URL, query strings)
PILU-trained model: ✓ RECOGNIZES LEGITIMATE LOGIN PATTERN
```

**✅ Advantages:**
- Drastically reduces false-positive rates
- Trained on realistic authentication URLs
- Understands complex query strings and tokens

---

## Module 3: Header Analysis and Authentication Verification

### 🎯 Objective

Detect **spoofing, routing anomalies, and failed cryptographic checks**.

### 🤖 Model Used

- **Random Forest Classifier**

---

### 🔐 Authentication Standards Analyzed

#### 1. **SPF** (Sender Policy Framework)


**What it checks:** Is the connecting IP authorized by the domain owner's DNS?

**Feature Extracted:** `spf_pass` (Binary: 1 = Pass, 0 = Fail)

#### 2. **DKIM** (DomainKeys Identified Mail)

**What it checks:** Validates cryptographic signature on email

**Feature Extracted:** `dkim_pass` (Binary: 1 = Pass, 0 = Fail)

#### 3. **DMARC** (Domain-based Message Authentication, Reporting & Conformance)

**What it checks:** Policy enforcement for SPF/DKIM failures + domain alignment

**Feature Extracted:** `sender_match` (Binary: Does authenticated domain match From: field?)

---

### 🚨 Critical Insight

**⚠️ Passing SPF/DKIM alone is NOT sufficient!**

```
Attacker registers: totally-legit-bank.com
SPF: ✓ PASS (their domain, their server)
DKIM: ✓ PASS (signed correctly)
From: support@totally-legit-bank.com
User sees: "support@totally-legit-bank.com" (not their actual bank!)

Solution: DMARC alignment checks if authenticated domain matches displayed From: domain
```

---

### 🔍 Features Extracted


| Feature | Type | Description |
|---------|------|-------------|
| `spf_pass` | Binary | SPF authentication result |
| `dkim_pass` | Binary | DKIM signature validation |
| `dmarc_alignment` | Binary | Domain alignment check |
| `sender_match` | Binary | From: matches authenticated domain |
| `num_received_hops` | Integer | Number of routing hops |
| `return_path_match` | Binary | Return-Path matches From: |
| `reply_to_match` | Binary | Reply-To matches From: |

---

### 📊 Required Datasets

#### Dataset 1: **Nazario Dataset** (Raw Headers Preserved)

**✅ Advantage:**
- `.mbox` format retains complete header structure
- Can parse `Received:` hops
- Extract SPF/DKIM results from headers

**🔧 Implementation:**
```python
import mailbox

mbox = mailbox.mbox('nazario.mbox')
for message in mbox:
    # Extract headers
    headers = {
        'from': message['From'],
        'return_path': message['Return-Path'],
        'received': message.get_all('Received')
    }
```

---

#### Dataset 2: **Spam Genuine Mail Contents Dataset** (by Isuranga)

**📌 Overview:**

- **Size**: 100,000 emails
  - 50,000 Legitimate
  - 50,000 Spam
- **Pre-extracted metadata fields**

**✅ Advantages:**
- SPF, DKIM, DMARC fields already extracted
- Number of `Received:` headers included
- Originating IP metrics
- Ready for immediate Random Forest training

**🎯 Perfect for:** Mapping non-linear decision boundaries between authentication failures and malicious intent

---

## Module 4: Attachment Analysis and Metadata Heuristics

### 🎯 Objective

Flag suspicious attachments using **static analysis** (no sandbox detonation).

### 🤖 Model Used

- **XGBoost Classifier**

---

### 🔍 Features Extracted

| Feature | Type | Description | Red Flag Value |
|---------|------|-------------|----------------|
| `file_extension` | Categorical | File type | `.exe`, `.scr`, `.docm`, `.xlsm` |
| `mime_type_match` | Binary | Extension matches MIME type | `0` (mismatch) |
| `is_executable` | Binary | Has execution permissions | `1` |
| `has_macro` | Binary | Contains VBA macros | `1` |
| `entropy` | Float | File randomness (0-8) | `> 7.5` |

---

### 📈 Understanding Entropy

**Entropy** measures the randomness/unpredictability of file data:

```
Low Entropy (< 5.0):  Plain text, uncompressed files
Medium Entropy (5-7): Normal compressed files
High Entropy (> 7.5): 🚨 Encrypted/obfuscated/packed malware
```

**Example:**
```python
import math
from collections import Counter

def calculate_entropy(data):
    if not data:
        return 0
    entropy = 0
    counter = Counter(data)
    for count in counter.values():
        p = count / len(data)
        entropy -= p * math.log2(p)
    return entropy

# Malware typically has entropy > 7.9
```

---

### 🚨 High-Risk Patterns

**Pattern 1: Macro-Enabled Documents**
```
File: invoice.docm
has_macro: 1
is_executable: 0
entropy: 6.2
Risk: HIGH (macros can execute PowerShell)
```

**Pattern 2: Extension Mismatch**
```
File: document.pdf.exe
Extension: .exe
MIME Type: application/pdf
mime_type_match: 0
Risk: CRITICAL (disguised executable)
```

**Pattern 3: High Entropy + Macros**
```
File: report.xlsm
has_macro: 1
entropy: 7.9
Risk: CRITICAL (packed/obfuscated malware with macro dropper)
```

---

### 📊 Required Dataset

#### **Simulated Email Dataset** (by Vincent Amonde)

**📌 Overview:**
- Simulated attachment metadata
- Reflects realistic malicious patterns
- **No actual malware files** (safe for development)

**✅ Advantages:**
- Includes entropy scores
- Extension mismatch examples
- Macro presence flags
- No security/privacy risks

**🔧 Implementation:**
```python
import pandas as pd

# Load simulated metadata
metadata = {
    'filename': 'invoice.docm',
    'has_macro': 1,
    'is_executable': 0,
    'entropy': 7.9,
    'extension': '.docm'
}

df = pd.DataFrame([metadata])
prediction = xgb_model.predict(df)
```

---

## Module 5: Psychological and Behavioral Profiling


### 🎯 Objective

Detect **psychological manipulation tactics** independent of semantic meaning.

### 🤖 Approach

- **NLP** (TF-IDF from Scikit-learn)
- **Rule-based heuristics**
- **Custom psycholinguistic lexicons**

---

### 🧠 Psycholinguistic Features

| Feature | Description | Example Triggers |
|---------|-------------|------------------|
| `urgency_score` | Temporal pressure (0-10) | "URGENT!", "immediately", "within 24 hours" |
| `threat_score` | Negative consequences (0-10) | "suspended", "terminated", "legal action" |
| `financial_score` | Money-related pressure (0-10) | "refund", "payment failed", "verify payment" |
| `authority_score` | Impersonation attempts (0-10) | "IRS", "CEO", "IT Department" |
| `password_reset_flag` | Binary | Unexpected password reset requests |

---

### 📝 Example Analysis

**Input Email:**
> "URGENT! Your account will be suspended within 24 hours. Click here immediately to verify your payment information or face legal action."

**Feature Extraction:**
```python
features = {
    'urgency_score': 9,   # "URGENT!", "within 24 hours", "immediately"
    'threat_score': 8,    # "suspended", "legal action"
    'financial_score': 7, # "payment information", "verify payment"
    'authority_score': 3, # "account" (implied institutional authority)
    'password_reset': 0   # No password reset request
}

# High urgency + high threat + financial = STRONG phishing signal
```

---

### 📊 Required Datasets

#### Dataset 1: **SpaPhish** (Psychological Framework)

**📌 Overview:**
- **Language**: Spanish (but framework is universal)
- **Annotations**: 5 psychological persuasion dimensions

**5 Persuasion Dimensions (Ana Ferreira Framework):**
1. **Authority** - Impersonation of trusted entities
2. **Social Proof** - "Everyone is doing this"
3. **Liking/Deception** - Mimicking familiar brands
4. **Commitment** - "You already started this process"
5. **Distraction/Urgency** - Time pressure tactics

**✅ Value:**
- Provides mathematical blueprint for any language
- Can adapt annotation schema to English datasets

---

#### Dataset 2: **Custom TF-IDF on Enron + Nazario**

**🔧 Implementation:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Build urgency lexicon
urgency_words = ['urgent', 'immediately', 'now', 'asap', 'within 24']
threat_words = ['suspended', 'terminated', 'legal', 'blocked', 'locked']
financial_words = ['payment', 'refund', 'invoice', 'verify', 'account']

def calculate_urgency_score(text):
    text_lower = text.lower()
    score = sum(text_lower.count(word) for word in urgency_words)
    return min(score * 2, 10)  # Cap at 10
```

---

#### Dataset 3: **Regional Language Datasets**

**🌍 Global Coverage:**
- Gujarati, Hindi, Marathi, Telugu text datasets
- Ensures detection of regionally-targeted phishing
- Prevents attackers from bypassing English-only filters

---

#### Dataset 4: **LLM-Generated Phishing**

**🚨 Critical for Behavioral Analysis:**

Traditional phishing relied on grammar errors as a filter (intentional or not). LLMs eliminate this signal entirely.

**Why Module 5 is Critical:**
```
LLM-Generated Email:
"We've noticed some unusual activity on your account. For your security, 
please verify your identity at your earliest convenience."

✓ Perfect grammar (bypasses Module 1 partially)
✓ Clean URL structure (might bypass Module 2)
✗ High urgency score ("unusual activity", "security")
✗ High threat implication score
```

Module 5 catches AI-generated phishing by analyzing **underlying psychological manipulation**, not surface-level errors.

---

## Feature Fusion and Meta-Learner


### 🎯 Objective

Combine all 5 module outputs into a **unified classification decision**.

---

### 🔄 How Feature Fusion Works

#### Step 1: Freeze Base Models

After training, the 5 modules become **feature extractors**, not classifiers:

```python
# Module 1: BERT
bert_model.eval()  # Freeze weights

# Module 2: URL Model
url_model.fit(X_url_train, y_train)

# Module 3: Header Model
header_model.fit(X_header_train, y_train)

# Module 4: Attachment Model
attachment_model.fit(X_attachment_train, y_train)

# Module 5: Behavioral Model
behavior_model.fit(X_behavior_train, y_train)
```

#### Step 2: Generate Predictions

Pass new email through all 5 modules:

```python
email = load_email("suspicious_email.eml")

# Extract features for each module
bert_score = bert_model.predict_proba(email.text)[0][1]
url_score = url_model.predict_proba(extract_url_features(email.urls))[0][1]
header_score = header_model.predict_proba(extract_header_features(email.headers))[0][1]
attachment_score = attachment_model.predict_proba(extract_attachment_features(email.attachments))[0][1]
behavior_score = behavior_model.predict_proba(extract_behavior_features(email.text))[0][1]


# Fused feature array
fused_features = [bert_score, url_score, header_score, attachment_score, behavior_score]
# Example: [0.91, 0.84, 0.95, 0.76, 0.88]
```

#### Step 3: Create Secondary Dataset

Process a large validation dataset through all 5 modules:

| Email ID | BERT | URL | Header | Attachment | Behavior | **Label** |
|----------|------|-----|--------|------------|----------|-----------|
| Email_001 | 0.91 | 0.84 | 0.95 | 0.76 | 0.88 | **1** (Phishing) |
| Email_002 | 0.12 | 0.05 | 0.10 | 0.01 | 0.05 | **0** (Legitimate) |
| Email_003 | 0.85 | 0.10 | 0.90 | 0.00 | 0.80 | **1** (Spoofed) |
| Email_004 | 0.20 | 0.15 | 0.05 | 0.85 | 0.10 | **0** (IT Email) |

---

### 🤖 XGBoost Meta-Learner

#### Why XGBoost?

**1. Non-Linear Feature Interaction**

XGBoost learns complex patterns:

```
Pattern Recognition:
- High BERT + High URL + High Header = Obvious phishing ✓
- Low URL + Low Attachment + HIGH Header + HIGH BERT = Sophisticated spoofing ✓
- Low all modules EXCEPT High Attachment = Malware delivery ✓
```

Simple averaging would miss these patterns!

**2. Built-in Regularization**

- **L1 (Lasso)** and **L2 (Ridge)** regularization
- Prevents overfitting to dominant module
- Forces balanced consideration of all signals

**3. Optimized for Tabular Data**

- Perfect for continuous probability distributions
- More efficient than deep learning for this task

---

### 🔧 Implementation

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split

# Load secondary dataset (fused predictions + labels)
X_meta = fused_predictions_df[['bert_score', 'url_score', 'header_score', 
                                'attachment_score', 'behavior_score']]
y_meta = fused_predictions_df['label']

X_train, X_test, y_train, y_test = train_test_split(X_meta, y_meta, test_size=0.2)

# Train meta-learner
meta_learner = xgb.XGBClassifier(
    max_depth=5,
    learning_rate=0.1,
    n_estimators=100,
    reg_alpha=0.1,  # L1 regularization
    reg_lambda=1.0  # L2 regularization
)

meta_learner.fit(X_train, y_train)

# Final prediction
final_prediction = meta_learner.predict_proba(fused_features)[0][1]
# Output: 0.982 (98.2% phishing probability)
```

---

## Implementation Roadmap

### 🚀 Progressive Development Strategy

**⚠️ Reality Check:**  
Building all 5 modules + ensemble simultaneously is unrealistic for diploma/B.Tech projects.

---

### 📅 Phase-by-Phase Implementation

#### **Phase 1: Baseline** (Weeks 1-3)

**Goal:** Functional 2-module system

**Implementation:**
- ✅ Module 1: BERT (Content Analysis)
- ✅ Module 2: URL Analysis (Logistic Regression)
- ✅ Simple ensemble (averaging or weighted sum)

**Datasets:**
- Enron + Nazario (Module 1)
- ISCX-URL2016 (Module 2)

**Deliverable:** Basic phishing detector covering text + links

---

#### **Phase 2: Cryptographic Layer** (Weeks 4-5)

**Goal:** Add authentication verification

**Implementation:**
- ✅ Module 3: Header Analysis (Random Forest)
- ✅ Parse `.mbox` files for SPF/DKIM/DMARC

**Datasets:**
- Nazario (headers preserved)
- Spam Genuine Mail Contents

**Deliverable:** Detect spoofed/forged emails

---

#### **Phase 3: Payload Detection** (Weeks 6-7)


**Goal:** Flag malicious attachments

**Implementation:**
- ✅ Module 4: Attachment Metadata (XGBoost)
- ✅ Extract entropy, macros, extension mismatches

**Datasets:**
- Simulated Email Dataset (Vincent Amonde)

**Deliverable:** Identify macro/malware-laden emails

---

#### **Phase 4: Psychological Layer** (Weeks 8-9)

**Goal:** Detect social engineering tactics

**Implementation:**
- ✅ Module 5: Behavioral Profiling (TF-IDF + heuristics)
- ✅ Build custom psycholinguistic lexicons

**Datasets:**
- SpaPhish (framework adaptation)
- LLM-generated phishing dataset

**Deliverable:** Catch AI-generated, grammatically perfect phishing

---

#### **Phase 5: Ensemble Integration** (Weeks 10-12)

**Goal:** Complete stacking ensemble

**Implementation:**
1. Freeze all 5 base models
2. Generate secondary dataset (run validation set through all modules)
3. Train XGBoost meta-learner
4. Hyperparameter tuning
5. Final evaluation

**Deliverable:** Full production-ready system

---

### 🛠️ Technology Stack

```python
# Core Libraries
import pandas as pd              # Data manipulation
import numpy as np               # Array operations


# Module 1: Deep Learning
import torch                     # PyTorch for BERT
from transformers import (       # Hugging Face
    BertTokenizer,
    BertForSequenceClassification,
    DistilBertTokenizer,
    DistilBertForSequenceClassification
)

# Modules 2, 3, 5: Classical ML
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Module 4 + Meta-Learner: Gradient Boosting
import xgboost as xgb

# Parsing & Preprocessing
import mailbox                   # Parse .mbox files
import email                     # Email parsing
from email import policy
from email.parser import BytesParser
```

---

### 🔄 Sequential Training Process

**Critical Rule:** Train each module in isolation to prevent data leakage.

```python
# STEP 1: Train Module 1 (BERT)
bert_model = train_bert(enron_data, nazario_data)

# STEP 2: Train Module 2 (URL)
url_model = train_url_classifier(iscx_data)

# STEP 3: Train Module 3 (Headers)
header_model = train_header_classifier(spam_genuine_data)

# STEP 4: Train Module 4 (Attachments)
attachment_model = train_attachment_classifier(simulated_attachment_data)

# STEP 5: Train Module 5 (Behavioral)
behavior_model = train_behavior_classifier(enron_data, nazario_data)

# STEP 6: Generate Secondary Dataset
validation_emails = load_unseen_validation_set()
fused_predictions = []

for email in validation_emails:
    scores = [
        bert_model.predict(email.text),
        url_model.predict(extract_url_features(email)),
        header_model.predict(extract_header_features(email)),
        attachment_model.predict(extract_attachment_features(email)),
        behavior_model.predict(extract_behavior_features(email))
    ]
    fused_predictions.append(scores + [email.label])

# STEP 7: Train Meta-Learner
meta_df = pd.DataFrame(fused_predictions, 
                       columns=['bert', 'url', 'header', 'attachment', 'behavior', 'label'])
X_meta = meta_df.drop('label', axis=1)
y_meta = meta_df['label']

meta_learner = xgb.XGBClassifier()
meta_learner.fit(X_meta, y_meta)
```

---

## Conclusion

### 🎯 Architectural Superiority

**Why Stacking Ensemble Dominates:**


#### Attack Surface Analysis

**Monolithic Model Vulnerability:**
```
Single BERT model: Attacker crafts grammatically perfect text → BYPASSED
```

**Stacking Ensemble Defense:**
```
To bypass system, attacker must SIMULTANEOUSLY:
✓ Create perfect semantic text (fool Module 1)
✓ Use legitimate-looking URL (fool Module 2)
✓ Pass SPF/DKIM/DMARC (fool Module 3)
✓ Avoid suspicious attachments (fool Module 4)
✓ Remove all psychological triggers (fool Module 5)

Probability of success: STATISTICALLY NEAR ZERO
```

---

### 📊 Dataset Diversity = Robustness

**Training Data Coverage:**

| Attack Vector | Dataset Coverage |
|---------------|------------------|
| Traditional phishing | Nazario (2005-2025) |
| Modern active threats | PhishingPot (honeypot) |
| AI-generated lures | LLM-generated dataset |
| URL obfuscation | ISCX-URL2016, PhiUSIIL, PILU-90K |
| Email spoofing | Nazario headers, Spam Genuine Mail |
| Malicious payloads | Simulated Attachment metadata |
| Psychological manipulation | SpaPhish framework |
| Regional language attacks | Gujarati/Hindi/Marathi/Telugu datasets |

---

### 🚀 Future-Proof Architecture

**Adaptability to Emerging Threats:**

1. **New phishing tactics** → Retrain individual module (not entire system)
2. **Concept drift** → Update PhishingPot data regularly
3. **Advanced LLM threats** → Expand Module 5 lexicons
4. **New file types** → Add features to Module 4
5. **Zero-day exploits** → Meta-learner adapts pattern recognition

---

### 💡 Key Takeaways

1. **Specialization > Generalization**: Domain-specific modules outperform monolithic models
2. **Data Quality = Model Quality**: Diverse, representative datasets are critical
3. **Progressive Implementation**: Build incrementally, validate continuously
4. **Ensemble Power**: XGBoost meta-learner captures non-linear interactions
5. **Defense in Depth**: Multiple layers force attackers to achieve perfect evasion

---

### 📚 Complete Dataset Reference

#### Module 1: Content Analysis
- ✅ Enron Email Corpus (500K emails)
- ✅ Nazario Phishing Dataset (2005-2025)
- ✅ PhishingPot (live honeypot)
- ✅ MeAJOR Corpus (135K aggregated emails)
- ✅ LLM-Generated Phishing (4K emails)

#### Module 2: URL Analysis
- ✅ ISCX-URL2016 (57K URLs, multi-class)
- ✅ PhiUSIIL (236K URLs, 54 features)
- ✅ PILU-90K (90K URLs with login pages)

#### Module 3: Header Analysis
- ✅ Nazario (headers preserved)
- ✅ Spam Genuine Mail Contents (100K emails)

#### Module 4: Attachment Analysis
- ✅ Simulated Email Dataset (Vincent Amonde)

#### Module 5: Behavioral Profiling
- ✅ SpaPhish (psychological framework)
- ✅ Enron + Nazario (custom TF-IDF)
- ✅ Regional language datasets
- ✅ LLM-Generated Phishing

---

### 🎓 Educational Value

**Skills Developed:**
- Deep Learning (PyTorch, Transformers)
- Classical ML (Scikit-learn)
- Gradient Boosting (XGBoost)
- Data Engineering (Pandas, NumPy)
- Email Parsing (mailbox library)
- Feature Engineering
- Ensemble Methods
- Cybersecurity Fundamentals

---

### 🏆 Final Statement

The architecture of a **Stacking Ensemble** reflects the uncompromising reality of modern cybersecurity: 

> **No single feature, heuristic, or algorithm can unilaterally verify the intent of sophisticated digital communication.**

By compartmentalizing the detection process into **isolated semantic, lexical, cryptographic, payload, and psychological evaluations**, the stacking architecture forces an attacker to perfectly spoof **every single operational vector** to achieve a successful system bypass—a **statistically improbable feat**.

The viability of this entire framework is inextricably bound to the rigor of data selection and feature engineering. By structurally fusing these specialized probabilistic assessments through an XGBoost meta-learner within a robust Python ecosystem, engineers can deploy a **highly resilient defense mechanism** capable of adapting to the rapid, asymmetrical evolution of global phishing campaigns.

---

## Appendix A: Quick Start Code Template


```python
"""
Phishing Detection Stacking Ensemble
Complete Implementation Template
"""

import pandas as pd
import numpy as np
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

# ========================================
# STEP 1: Train Individual Modules
# ========================================

def train_content_module(enron_data, nazario_data):
    """Module 1: BERT for content analysis"""
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
    # Training code here...
    return model, tokenizer

def train_url_module(url_dataset):
    """Module 2: Random Forest for URL analysis"""
    X = url_dataset[['url_length', 'num_dots', 'num_hyphens', 
                     'https_present', 'domain_age', 'ip_address_used']]
    y = url_dataset['label']
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model

def train_header_module(header_dataset):
    """Module 3: Random Forest for header analysis"""
    X = header_dataset[['spf_pass', 'dkim_pass', 'dmarc_alignment', 
                        'sender_match', 'num_received_hops']]
    y = header_dataset['label']
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model

def train_attachment_module(attachment_dataset):
    """Module 4: XGBoost for attachment analysis"""
    X = attachment_dataset[['is_executable', 'has_macro', 'entropy', 
                            'mime_type_match']]
    y = attachment_dataset['label']
    
    model = xgb.XGBClassifier(max_depth=5, learning_rate=0.1)
    model.fit(X, y)
    return model

def train_behavior_module(text_dataset):
    """Module 5: TF-IDF + heuristics for behavioral analysis"""
    # Custom implementation with psycholinguistic lexicons
    # Returns urgency_score, threat_score, financial_score
    pass

# ========================================
# STEP 2: Feature Fusion
# ========================================

def predict_all_modules(email, models):
    """Generate predictions from all 5 modules"""
    bert_model, url_model, header_model, attachment_model, behavior_model = models
    
    # Extract features and predict
    bert_score = bert_model.predict_proba(email.text)[0][1]
    url_score = url_model.predict_proba(extract_url_features(email))[0][1]
    header_score = header_model.predict_proba(extract_header_features(email))[0][1]
    attachment_score = attachment_model.predict_proba(extract_attachment_features(email))[0][1]
    behavior_score = behavior_model.predict_proba(extract_behavior_features(email))[0][1]
    
    return [bert_score, url_score, header_score, attachment_score, behavior_score]

# ========================================
# STEP 3: Train Meta-Learner
# ========================================

def train_meta_learner(validation_emails, base_models):
    """Train XGBoost meta-learner on fused predictions"""
    fused_data = []
    
    for email in validation_emails:
        scores = predict_all_modules(email, base_models)
        fused_data.append(scores + [email.label])
    
    df = pd.DataFrame(fused_data, 
                     columns=['bert', 'url', 'header', 'attachment', 'behavior', 'label'])
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    meta_learner = xgb.XGBClassifier(
        max_depth=5,
        learning_rate=0.1,
        n_estimators=100,
        reg_alpha=0.1,
        reg_lambda=1.0
    )
    
    meta_learner.fit(X, y)
    return meta_learner

# ========================================
# STEP 4: Complete Detection Pipeline
# ========================================

def detect_phishing(email, base_models, meta_learner):
    """Complete phishing detection pipeline"""
    
    # Get predictions from all base modules
    fused_features = predict_all_modules(email, base_models)
    
    # Meta-learner final decision
    X_meta = np.array(fused_features).reshape(1, -1)
    final_probability = meta_learner.predict_proba(X_meta)[0][1]
    
    return {
        'is_phishing': final_probability > 0.5,
        'confidence': final_probability,
        'module_scores': {
            'content': fused_features[0],
            'url': fused_features[1],
            'header': fused_features[2],
            'attachment': fused_features[3],
            'behavior': fused_features[4]
        }
    }

# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    # Train all modules
    print("Training Module 1: Content Analysis...")
    bert_model, tokenizer = train_content_module(enron_data, nazario_data)
    
    print("Training Module 2: URL Analysis...")
    url_model = train_url_module(url_dataset)
    
    print("Training Module 3: Header Analysis...")
    header_model = train_header_module(header_dataset)
    
    print("Training Module 4: Attachment Analysis...")
    attachment_model = train_attachment_module(attachment_dataset)
    
    print("Training Module 5: Behavioral Analysis...")
    behavior_model = train_behavior_module(text_dataset)
    
    base_models = (bert_model, url_model, header_model, 
                   attachment_model, behavior_model)
    
    print("Training Meta-Learner...")
    meta_learner = train_meta_learner(validation_emails, base_models)
    
    print("System ready!")
    
    # Test on new email
    test_email = load_email("suspicious_email.eml")
    result = detect_phishing(test_email, base_models, meta_learner)
    
    print(f"\n{'='*50}")
    print(f"Phishing Detection Result")
    print(f"{'='*50}")
    print(f"Classification: {'PHISHING' if result['is_phishing'] else 'LEGITIMATE'}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"\nModule Breakdown:")
    print(f"  Content Analysis:    {result['module_scores']['content']:.3f}")
    print(f"  URL Analysis:        {result['module_scores']['url']:.3f}")
    print(f"  Header Analysis:     {result['module_scores']['header']:.3f}")
    print(f"  Attachment Analysis: {result['module_scores']['attachment']:.3f}")
    print(f"  Behavioral Analysis: {result['module_scores']['behavior']:.3f}")
```

---

## Appendix B: Dataset URLs & Resources

### Module 1: Content Analysis

| Dataset | Source | Link |
|---------|--------|------|
| Enron Corpus | Hugging Face | `datasets.load_dataset("enron_emails")` |
| Nazario Phishing | monkey.org | Various .mbox files available |
| MeAJOR Corpus | GECAD, Porto | Research repository access |
| LLM Phishing | GitHub | FrancescoGreco97 repository |

### Module 2: URL Analysis

| Dataset | Source | Access |
|---------|--------|--------|
| ISCX-URL2016 | Canadian Inst. Cybersecurity | Official website |
| PhiUSIIL | UCI ML Repository | 2024 donation |
| PILU-90K | Academic research | Research paper access |

### Module 3: Header Analysis

| Dataset | Source | Notes |
|---------|--------|-------|
| Nazario | monkey.org | Headers preserved in .mbox |
| Spam Genuine Mail | Kaggle/Isuranga | Pre-extracted metadata |

### Module 4: Attachment Analysis

| Dataset | Creator | Platform |
|---------|---------|----------|
| Simulated Email Dataset | Vincent Amonde | Kaggle |

### Module 5: Behavioral Analysis

| Dataset | Focus | Language |
|---------|-------|----------|
| SpaPhish | Psychological framework | Spanish (adaptable) |
| Regional Datasets | Multi-language | Hindi, Gujarati, etc. |

---

## Appendix C: Performance Metrics

### Expected Results (Post-Training)

| Metric | Individual Module Avg. | Stacking Ensemble |
|--------|----------------------|-------------------|
| **Accuracy** | 85-92% | **96-98%** |
| **Precision** | 83-90% | **95-97%** |
| **Recall** | 80-88% | **94-96%** |
| **F1-Score** | 82-89% | **95-97%** |

### Why Ensemble Outperforms:

1. **Error Diversity**: Individual module errors don't correlate
2. **Non-Linear Patterns**: XGBoost captures complex interactions
3. **Multi-Vector Coverage**: Attackers must bypass ALL modules

---

## Appendix D: Common Pitfalls & Solutions


### Pitfall 1: Data Leakage

**Problem:**
```python
# WRONG: Using same data for base models AND meta-learner
X_train, X_test = train_test_split(all_data)
base_model.fit(X_train)
meta_learner.fit(X_train)  # ❌ LEAKAGE!
```

**Solution:**
```python
# CORRECT: Split data into 3 sets
X_train, X_val, X_test = train_val_test_split(all_data)

# Train base models on train set
base_model.fit(X_train)

# Generate predictions on validation set for meta-learner
val_predictions = base_model.predict(X_val)

# Train meta-learner on validation predictions
meta_learner.fit(val_predictions)

# Test on completely unseen test set
```

---

### Pitfall 2: Ignoring Class Imbalance

**Problem:** Real-world datasets have far more legitimate emails than phishing

**Solution:**
```python
from sklearn.utils import class_weight

# Calculate class weights
class_weights = class_weight.compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)

# Apply to model
model = xgb.XGBClassifier(scale_pos_weight=class_weights[1]/class_weights[0])
```

---

### Pitfall 3: Not Freezing Base Models

**Problem:** Retraining base models during meta-learner training

**Solution:**
```python
# Freeze base models
bert_model.eval()
for param in bert_model.parameters():
    param.requires_grad = False

# Use only for prediction, not training
with torch.no_grad():
    predictions = bert_model(inputs)
```

---

### Pitfall 4: Overfitting Meta-Learner

**Problem:** Meta-learner too complex for small feature space (only 5 features)

**Solution:**
```python
# Use regularization
meta_learner = xgb.XGBClassifier(
    max_depth=3,           # Shallow trees
    min_child_weight=5,    # Minimum samples per leaf
    reg_alpha=0.1,         # L1 regularization
    reg_lambda=1.0,        # L2 regularization
    subsample=0.8          # Row sampling
)
```

---

## Appendix E: Deployment Considerations

### Production Pipeline Architecture

```
Email Received
    ↓
[Preprocessing Layer]
    ├→ Text Extraction
    ├→ URL Extraction
    ├→ Header Parsing
    ├→ Attachment Metadata
    └→ Behavioral Feature Extraction
    ↓
[Parallel Module Processing]
    ├→ Module 1: BERT (GPU)
    ├→ Module 2: URL Classifier (CPU)
    ├→ Module 3: Header Classifier (CPU)
    ├→ Module 4: Attachment Classifier (CPU)
    └→ Module 5: Behavioral Classifier (CPU)
    ↓
[Feature Fusion Layer]
    ↓
[XGBoost Meta-Learner]
    ↓
[Decision: Quarantine/Allow/Flag for Review]
```

### Performance Optimization

**1. Batch Processing:**
```python
# Process multiple emails simultaneously
batch_emails = [email1, email2, email3, ...]
batch_predictions = model.predict(batch_emails)
```

**2. Caching:**
```python
# Cache URL reputation scores
from functools import lru_cache

@lru_cache(maxsize=10000)
def check_url_reputation(url):
    return url_model.predict(extract_url_features(url))
```

**3. GPU Acceleration (Module 1 only):**
```python
# Use GPU for BERT inference
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
bert_model.to(device)
```

### Monitoring & Updates

**Weekly:**
- Update PhishingPot data
- Retrain Module 1 with new samples

**Monthly:**
- Evaluate system performance
- Adjust meta-learner hyperparameters if needed

**Quarterly:**
- Full retraining of all modules
- Dataset expansion with new threat intelligence

---

## Glossary

| Term | Definition |
|------|------------|
| **Stacking Ensemble** | ML technique where multiple models' outputs feed into a meta-learner |
| **Meta-Learner** | Final model that learns from other models' predictions |
| **BERT** | Bidirectional Encoder Representations from Transformers |
| **XGBoost** | Extreme Gradient Boosting algorithm |
| **SPF** | Sender Policy Framework (email authentication) |
| **DKIM** | DomainKeys Identified Mail (cryptographic signature) |
| **DMARC** | Domain-based Message Authentication, Reporting & Conformance |
| **Entropy** | Measure of randomness in data (0-8 scale) |
| **TF-IDF** | Term Frequency-Inverse Document Frequency |
| **Concept Drift** | Model accuracy degradation as threat landscape evolves |
| **Feature Fusion** | Combining outputs from multiple models into single input |
| **Data Leakage** | Using test data during training (invalidates results) |

---

## References & Further Reading

### Academic Papers
1. "Stacking Ensemble Learning for Email Phishing Detection" (Various authors)
2. "BERT: Pre-training of Deep Bidirectional Transformers" (Devlin et al., 2018)
3. "XGBoost: A Scalable Tree Boosting System" (Chen & Guestrin, 2016)
4. "Phishing URL Detection Using Machine Learning" (Canadian Institute for Cybersecurity)

### Datasets
- Enron Email Dataset (FERC)
- Nazario Phishing Dataset (monkey.org)
- UCI Machine Learning Repository (PhiUSIIL)
- Kaggle Phishing Datasets

### Tools & Libraries
- PyTorch: https://pytorch.org
- Hugging Face Transformers: https://huggingface.co/transformers
- Scikit-learn: https://scikit-learn.org
- XGBoost: https://xgboost.readthedocs.io

---

## Document Information

**Version:** 2.0 (Formatted)  
**Last Updated:** 2026  
**Authors:** Research compilation for phishing detection systems  
**Purpose:** Educational blueprint for building advanced phishing detection architectures  

---

**END OF DOCUMENT**

---

*This document provides a comprehensive framework for implementing a production-grade phishing detection system using modern machine learning techniques and diverse threat intelligence datasets.*
