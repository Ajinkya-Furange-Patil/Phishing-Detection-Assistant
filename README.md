# Phishing Detection Assistant

A comprehensive multi-modular stacking ensemble system for advanced phishing detection using machine learning and deep learning techniques.

## 🎯 Overview

This project implements a 5-tier stacking ensemble architecture that analyzes emails through multiple specialized modules:

- **Module 1:** Email Content Analysis (BERT/DistilBERT)
- **Module 2:** URL Analysis (Logistic Regression, Random Forest)
- **Module 3:** Header Authentication Verification (SPF/DKIM/DMARC)
- **Module 4:** Attachment Metadata Analysis (XGBoost)
- **Module 5:** Behavioral & Psychological Profiling (NLP)
- **Meta-Learner:** XGBoost ensemble aggregator

## 🚀 Getting Started

### 1. Clone the Repository

```bash
# Clone this repository
git clone https://github.com/Ajinkya-Furange-Patil/Phishing-Detection-Assistant.git

# Navigate to the project directory
cd Phishing-Detection-Assistant
```

### 2. Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# Core libraries needed:
pip install pandas numpy scikit-learn xgboost
pip install torch transformers
pip install datasets ucimlrepo
```

### 3. Download Datasets

Refer to the comprehensive dataset guide:

- **Detailed Guide:** See [DATASETS.md](DATASETS.md) for complete download instructions
- **Quick Links:** See [DATASET-LINKS.txt](DATASET-LINKS.txt) for direct URLs

**Essential datasets:**
- Enron Email Corpus (legitimate emails)
- Nazario Phishing Dataset (phishing emails)
- PhiUSIIL URL Dataset
- Spam Genuine Mail Contents Dataset

### 4. Project Structure

```
Phishing-Detection-Assistant/
├── README.md                    # This file
├── G-file-formatted.md          # Complete technical documentation
├── DATASETS.md                  # Dataset download guide
├── DATASET-LINKS.txt            # Quick reference links
├── datasets/                    # Downloaded datasets (create this)
│   ├── enron/
│   ├── nazario/
│   ├── phiusiil/
│   └── ...
├── models/                      # Trained models (create this)
│   ├── bert_model/
│   ├── url_model/
│   └── ...
└── src/                         # Source code (to be added)
    ├── module1_content.py
    ├── module2_url.py
    ├── module3_header.py
    ├── module4_attachment.py
    ├── module5_behavioral.py
    └── meta_learner.py
```

## 📚 Documentation

- **[G-file-formatted.md](G-file-formatted.md)** - Complete architectural blueprint and implementation guide
- **[DATASETS.md](DATASETS.md)** - Comprehensive dataset documentation with download instructions
- **[DATASET-LINKS.txt](DATASET-LINKS.txt)** - Quick reference for dataset URLs

## 🛠️ Tech Stack

- **Python 3.8+**
- **PyTorch** - Deep learning framework
- **Transformers (Hugging Face)** - BERT/DistilBERT models
- **Scikit-learn** - Classical ML algorithms
- **XGBoost** - Gradient boosting
- **Pandas & NumPy** - Data manipulation

## 🔍 Features

✅ Multi-vector phishing detection  
✅ Content analysis using transformer models  
✅ URL lexical analysis and obfuscation detection  
✅ Email header authentication verification  
✅ Attachment metadata heuristics  
✅ Psychological trigger detection  
✅ Ensemble learning for high accuracy  

## 📈 Expected Performance

- **Accuracy:** 96-98%
- **Precision:** 95-97%
- **Recall:** 94-96%
- **F1-Score:** 95-97%

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is for educational purposes.

## 👤 Author

**Ajinkya Furange Patil**

- GitHub: [@Ajinkya-Furange-Patil](https://github.com/Ajinkya-Furange-Patil)
- Repository: [Phishing-Detection-Assistant](https://github.com/Ajinkya-Furange-Patil/Phishing-Detection-Assistant)

## 🙏 Acknowledgments

- Enron Email Dataset (FERC)
- Nazario Phishing Corpus
- Canadian Institute for Cybersecurity (ISCX-URL2016)
- UCI Machine Learning Repository (PhiUSIIL)
- Hugging Face for transformer models

---

**Note:** For detailed implementation guide, architecture details, and research documentation, please refer to [G-file-formatted.md](G-file-formatted.md)
