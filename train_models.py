"""
Quick Model Training Script for PhishGuard Backend
Uses the email_dataset_100k.csv to train TF-IDF + Logistic Regression + Random Forest
Saves models to backend/models/saved_models/
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import os
import time
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

print("=" * 70)
print("  PHISHGUARD - Model Training Pipeline")
print("=" * 70)

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "combine dataset", "email_dataset_100k.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models", "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ── Step 1: Load Dataset ──
print("\n[1/5] Loading dataset...")
start = time.time()
df = pd.read_csv(DATASET_PATH)
print(f"  ✓ Loaded {len(df):,} rows in {time.time()-start:.1f}s")
print(f"  Columns: {list(df.columns)[:8]}...")

# Use 'raw_text' or 'text' column and 'label'
text_col = 'raw_text' if 'raw_text' in df.columns else 'text'
print(f"  Using text column: '{text_col}'")
print(f"  Label distribution:")
print(f"    Legitimate (0): {(df['label']==0).sum():,}")
print(f"    Phishing   (1): {(df['label']==1).sum():,}")

# Drop NaN
df = df.dropna(subset=[text_col, 'label'])
df['label'] = df['label'].astype(int)
df[text_col] = df[text_col].fillna('').astype(str)

# ── Step 2: Sample for speed (use 50k max for faster training) ──
MAX_SAMPLES = 50000
if len(df) > MAX_SAMPLES:
    print(f"\n[2/5] Sampling {MAX_SAMPLES:,} rows for faster training...")
    df = df.sample(n=MAX_SAMPLES, random_state=42)
else:
    print(f"\n[2/5] Using full dataset ({len(df):,} rows)")

X = list(df[text_col])
y = list(df['label'])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  Train: {len(X_train):,} | Test: {len(X_test):,}")

# ── Step 3: TF-IDF Vectorization ──
print("\n[3/5] Building TF-IDF features...")
start = time.time()
vectorizer = TfidfVectorizer(
    max_features=5000,
    min_df=2,
    max_df=0.8,
    ngram_range=(1, 2),
    stop_words='english'
)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)
print(f"  ✓ Vocabulary size: {len(vectorizer.vocabulary_):,} ({time.time()-start:.1f}s)")

# Save vectorizer
vec_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
with open(vec_path, 'wb') as f:
    pickle.dump(vectorizer, f)
print(f"  ✓ Saved: {vec_path}")

# ── Step 4: Train Models ──
print("\n[4/5] Training models...")

models = {
    'logistic_regression': LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1, class_weight='balanced'),
    'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
}

for name, model in models.items():
    start = time.time()
    print(f"\n  Training {name}...")
    model.fit(X_train_tfidf, y_train)
    
    y_pred = model.predict(X_test_tfidf)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"  ✓ Accuracy: {acc:.4f} | F1: {f1:.4f} ({time.time()-start:.1f}s)")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))
    
    model_path = os.path.join(MODEL_DIR, f"{name}_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"  ✓ Saved: {model_path}")

# ── Step 5: Verify ──
print("\n[5/5] Verifying saved models...")
for fname in os.listdir(MODEL_DIR):
    fpath = os.path.join(MODEL_DIR, fname)
    size_mb = os.path.getsize(fpath) / (1024*1024)
    print(f"  ✓ {fname} ({size_mb:.1f} MB)")

print("\n" + "=" * 70)
print("  ✅ Training complete! Models ready for backend.")
print("=" * 70)
