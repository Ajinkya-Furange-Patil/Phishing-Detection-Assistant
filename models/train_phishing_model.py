import pandas as pd
import numpy as np
import os
import time
import pickle
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DATASET_PATH = r"..\datasets\combine dataset\simple_dataset.csv"
MODEL_DIR = "saved_models"
RESULTS_DIR = "results"
RANDOM_STATE = 42
TEST_SIZE = 0.2
SAMPLE_SIZE = None  # Set to None to use full dataset, or a number to sample

print("=" * 80)
print("PHISHING DETECTION MODEL TRAINING")
print("=" * 80)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Create directories
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Step 1: Load Data
print("\n[1/7] Loading Dataset...")
start_time = time.time()

try:
    df = pd.read_csv(DATASET_PATH)
    print(f"✓ Loaded {len(df):,} rows")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Loading time: {time.time() - start_time:.2f}s")
except Exception as e:
    print(f"✗ Error loading dataset: {e}")
    exit(1)

# Sample if needed
if SAMPLE_SIZE and SAMPLE_SIZE < len(df):
    print(f"\nSampling {SAMPLE_SIZE:,} rows for faster training...")
    df = df.sample(n=SAMPLE_SIZE, random_state=RANDOM_STATE)

# Step 2: Data Overview
print("\n[2/7] Data Overview...")
print(f"  Total samples: {len(df):,}")
print(f"  Class distribution:")
print(f"    Legitimate (0): {(df['label'] == 0).sum():,} ({(df['label'] == 0).sum()/len(df)*100:.2f}%)")
print(f"    Phishing (1):   {(df['label'] == 1).sum():,} ({(df['label'] == 1).sum()/len(df)*100:.2f}%)")
print(f"  Missing values: {df.isnull().sum().sum()}")
print(f"  Average text length: {df['text'].str.len().mean():.0f} characters")

# Step 3: Train-Test Split
print("\n[3/7] Splitting Data...")
X = df['text'].values
y = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)

print(f"✓ Train set: {len(X_train):,} samples")
print(f"✓ Test set:  {len(X_test):,} samples")
print(f"  Train class distribution: {np.bincount(y_train)}")
print(f"  Test class distribution:  {np.bincount(y_test)}")

# Step 4: Feature Extraction with TF-IDF
print("\n[4/7] Extracting Features (TF-IDF)...")
start_time = time.time()

vectorizer = TfidfVectorizer(
    max_features=5000,
    min_df=2,
    max_df=0.8,
    ngram_range=(1, 2),
    stop_words='english'
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"✓ Feature extraction complete")
print(f"  Vocabulary size: {len(vectorizer.vocabulary_):,}")
print(f"  Train shape: {X_train_tfidf.shape}")
print(f"  Test shape:  {X_test_tfidf.shape}")
print(f"  Time taken: {time.time() - start_time:.2f}s")

# Save vectorizer
vectorizer_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
with open(vectorizer_path, 'wb') as f:
    pickle.dump(vectorizer, f)
print(f"✓ Vectorizer saved to {vectorizer_path}")

# Step 5: Train Models
print("\n[5/7] Training Models...")

models = {
    'Logistic Regression': LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight='balanced'
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=100,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight='balanced'
    )
}

trained_models = {}
results = []

for name, model in models.items():
    print(f"\n  Training {name}...")
    start_time = time.time()
    
    model.fit(X_train_tfidf, y_train)
    training_time = time.time() - start_time
    
    # Predictions
    y_pred = model.predict(X_test_tfidf)
    y_pred_proba = model.predict_proba(X_test_tfidf)[:, 1]
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"  ✓ {name} trained in {training_time:.2f}s")
    print(f"    Accuracy:  {accuracy:.4f}")
    print(f"    Precision: {precision:.4f}")
    print(f"    Recall:    {recall:.4f}")
    print(f"    F1 Score:  {f1:.4f}")
    print(f"    ROC AUC:   {roc_auc:.4f}")
    
    # Save model
    model_path = os.path.join(MODEL_DIR, f"{name.replace(' ', '_').lower()}_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"    Model saved to {model_path}")
    
    trained_models[name] = {
        'model': model,
        'predictions': y_pred,
        'probabilities': y_pred_proba,
        'metrics': {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'roc_auc': roc_auc,
            'training_time': training_time
        }
    }
    
    results.append({
        'Model': name,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1,
        'ROC AUC': roc_auc,
        'Training Time (s)': training_time
    })

# Step 6: Generate Visualizations
print("\n[6/7] Generating Visualizations...")

# 6.1 Model Comparison
results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(RESULTS_DIR, 'model_comparison.csv'), index=False)

plt.figure(figsize=(12, 6))
metrics_to_plot = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC']
x = np.arange(len(results_df))
width = 0.15

for i, metric in enumerate(metrics_to_plot):
    plt.bar(x + i*width, results_df[metric], width, label=metric)

plt.xlabel('Model')
plt.ylabel('Score')
plt.title('Model Performance Comparison')
plt.xticks(x + width*2, results_df['Model'], rotation=15)
plt.legend()
plt.ylim(0, 1.1)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'model_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✓ Model comparison chart saved")

# 6.2 Confusion Matrices
fig, axes = plt.subplots(1, len(trained_models), figsize=(12, 5))
if len(trained_models) == 1:
    axes = [axes]

for idx, (name, data) in enumerate(trained_models.items()):
    cm = confusion_matrix(y_test, data['predictions'])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx], 
                xticklabels=['Legitimate', 'Phishing'],
                yticklabels=['Legitimate', 'Phishing'])
    axes[idx].set_title(f'{name}\nConfusion Matrix')
    axes[idx].set_ylabel('True Label')
    axes[idx].set_xlabel('Predicted Label')

plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrices.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✓ Confusion matrices saved")

# 6.3 ROC Curves
plt.figure(figsize=(10, 8))
for name, data in trained_models.items():
    fpr, tpr, _ = roc_curve(y_test, data['probabilities'])
    auc = data['metrics']['roc_auc']
    plt.plot(fpr, tpr, label=f'{name} (AUC = {auc:.4f})', linewidth=2)

plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves - Phishing Detection Models')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'roc_curves.png'), dpi=300, bbox_inches='tight')
plt.close()
print("✓ ROC curves saved")

# Step 7: Save Detailed Reports
print("\n[7/7] Generating Detailed Reports...")

# Classification reports
for name, data in trained_models.items():
    report = classification_report(y_test, data['predictions'], 
                                   target_names=['Legitimate', 'Phishing'])
    report_path = os.path.join(RESULTS_DIR, f'{name.replace(" ", "_").lower()}_report.txt')
    with open(report_path, 'w') as f:
        f.write(f"Classification Report: {name}\n")
        f.write("=" * 80 + "\n\n")
        f.write(report)
        f.write("\n\nConfusion Matrix:\n")
        f.write(str(confusion_matrix(y_test, data['predictions'])))
    print(f"✓ {name} report saved")

# Summary report
summary_path = os.path.join(RESULTS_DIR, 'training_summary.txt')
with open(summary_path, 'w') as f:
    f.write("PHISHING DETECTION MODEL TRAINING SUMMARY\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Dataset: {DATASET_PATH}\n")
    f.write(f"Total Samples: {len(df):,}\n")
    f.write(f"Train Samples: {len(X_train):,}\n")
    f.write(f"Test Samples: {len(X_test):,}\n")
    f.write(f"Test Size: {TEST_SIZE*100}%\n")
    f.write(f"Random State: {RANDOM_STATE}\n\n")
    f.write("Class Distribution:\n")
    f.write(f"  Legitimate (0): {(df['label'] == 0).sum():,} ({(df['label'] == 0).sum()/len(df)*100:.2f}%)\n")
    f.write(f"  Phishing (1):   {(df['label'] == 1).sum():,} ({(df['label'] == 1).sum()/len(df)*100:.2f}%)\n\n")
    f.write("Feature Extraction:\n")
    f.write(f"  Method: TF-IDF\n")
    f.write(f"  Max Features: 5000\n")
    f.write(f"  N-gram Range: (1, 2)\n")
    f.write(f"  Vocabulary Size: {len(vectorizer.vocabulary_):,}\n\n")
    f.write("Model Performance:\n")
    f.write(results_df.to_string(index=False))
    f.write("\n\n")
    f.write("Saved Models:\n")
    for name in trained_models.keys():
        model_file = f"{name.replace(' ', '_').lower()}_model.pkl"
        f.write(f"  - {model_file}\n")
    f.write(f"\nVectorizer: tfidf_vectorizer.pkl\n")

print(f"✓ Training summary saved to {summary_path}")

# Final Summary
print("\n" + "=" * 80)
print("TRAINING COMPLETE!")
print("=" * 80)
print(f"\nBest Model: {results_df.loc[results_df['F1 Score'].idxmax(), 'Model']}")
print(f"Best F1 Score: {results_df['F1 Score'].max():.4f}")
print(f"\nAll models and results saved to:")
print(f"  - Models: {MODEL_DIR}/")
print(f"  - Results: {RESULTS_DIR}/")
print("\n" + "=" * 80)
print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
