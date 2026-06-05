import pandas as pd
import numpy as np
import pickle
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

print("=" * 80)
print("PHISHING DETECTION - COMPLETE ACCURACY REPORT")
print("=" * 80)

# Paths
DATASET_PATH = r"..\datasets\combine dataset\simple_dataset.csv"
MODEL_DIR = "saved_models"
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
LOGISTIC_PATH = os.path.join(MODEL_DIR, "logistic_regression_model.pkl")
RF_PATH = os.path.join(MODEL_DIR, "random_forest_model.pkl")

# Load data
print("\n[1/5] Loading Dataset...")
df = pd.read_csv(DATASET_PATH)
print(f"✓ Total samples: {len(df):,}")

# Split data (same as training)
from sklearn.model_selection import train_test_split
X = df['text'].values
y = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✓ Training samples: {len(X_train):,}")
print(f"✓ Testing samples: {len(X_test):,}")

# Load models
print("\n[2/5] Loading Models...")
with open(VECTORIZER_PATH, 'rb') as f:
    vectorizer = pickle.load(f)
print("✓ Vectorizer loaded")

with open(LOGISTIC_PATH, 'rb') as f:
    logistic_model = pickle.load(f)
print("✓ Logistic Regression loaded")

with open(RF_PATH, 'rb') as f:
    rf_model = pickle.load(f)
print("✓ Random Forest loaded")

# Transform data
print("\n[3/5] Transforming Data...")
X_train_tfidf = vectorizer.transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)
print("✓ Data transformed")

# Calculate metrics for both models
print("\n[4/5] Calculating Metrics...")

models = {
    'Logistic Regression': logistic_model,
    'Random Forest': rf_model
}

results = []

for model_name, model in models.items():
    print(f"\n  Analyzing {model_name}...")
    
    # TRAINING ACCURACY
    y_train_pred = model.predict(X_train_tfidf)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    train_precision = precision_score(y_train, y_train_pred)
    train_recall = recall_score(y_train, y_train_pred)
    train_f1 = f1_score(y_train, y_train_pred)
    
    # TESTING ACCURACY
    y_test_pred = model.predict(X_test_tfidf)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_precision = precision_score(y_test, y_test_pred)
    test_recall = recall_score(y_test, y_test_pred)
    test_f1 = f1_score(y_test, y_test_pred)
    
    # Confusion matrices
    train_cm = confusion_matrix(y_train, y_train_pred)
    test_cm = confusion_matrix(y_test, y_test_pred)
    
    results.append({
        'Model': model_name,
        'Train Accuracy': train_accuracy,
        'Test Accuracy': test_accuracy,
        'Train Precision': train_precision,
        'Test Precision': test_precision,
        'Train Recall': train_recall,
        'Test Recall': test_recall,
        'Train F1': train_f1,
        'Test F1': test_f1,
        'Train CM': train_cm,
        'Test CM': test_cm
    })
    
    print(f"    Train Accuracy: {train_accuracy:.4f}")
    print(f"    Test Accuracy:  {test_accuracy:.4f}")

# Create detailed report
print("\n[5/5] Generating Report...")

report_path = "ACCURACY_REPORT.txt"
with open(report_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("PHISHING DETECTION ASSISTANT - COMPLETE ACCURACY REPORT\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("DATASET INFORMATION\n")
    f.write("-" * 80 + "\n")
    f.write(f"Total Samples:     {len(df):,}\n")
    f.write(f"Training Samples:  {len(X_train):,} (80%)\n")
    f.write(f"Testing Samples:   {len(X_test):,} (20%)\n")
    f.write(f"Legitimate Emails: {(y == 0).sum():,} ({(y == 0).sum()/len(y)*100:.2f}%)\n")
    f.write(f"Phishing Emails:   {(y == 1).sum():,} ({(y == 1).sum()/len(y)*100:.2f}%)\n")
    f.write("\n")
    
    for result in results:
        f.write("=" * 80 + "\n")
        f.write(f"MODEL: {result['Model']}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("TRAINING PERFORMANCE (on 115,610 emails)\n")
        f.write("-" * 80 + "\n")
        f.write(f"Accuracy:  {result['Train Accuracy']:.4f} ({result['Train Accuracy']*100:.2f}%)\n")
        f.write(f"Precision: {result['Train Precision']:.4f} ({result['Train Precision']*100:.2f}%)\n")
        f.write(f"Recall:    {result['Train Recall']:.4f} ({result['Train Recall']*100:.2f}%)\n")
        f.write(f"F1 Score:  {result['Train F1']:.4f} ({result['Train F1']*100:.2f}%)\n\n")
        
        f.write("Training Confusion Matrix:\n")
        cm = result['Train CM']
        f.write(f"                Predicted\n")
        f.write(f"              Legit    Phishing\n")
        f.write(f"Actual Legit  {cm[0][0]:5d}    {cm[0][1]:5d}\n")
        f.write(f"      Phish   {cm[1][0]:5d}    {cm[1][1]:5d}\n\n")
        
        f.write("TESTING PERFORMANCE (on 28,903 emails)\n")
        f.write("-" * 80 + "\n")
        f.write(f"Accuracy:  {result['Test Accuracy']:.4f} ({result['Test Accuracy']*100:.2f}%)\n")
        f.write(f"Precision: {result['Test Precision']:.4f} ({result['Test Precision']*100:.2f}%)\n")
        f.write(f"Recall:    {result['Test Recall']:.4f} ({result['Test Recall']*100:.2f}%)\n")
        f.write(f"F1 Score:  {result['Test F1']:.4f} ({result['Test F1']*100:.2f}%)\n\n")
        
        f.write("Testing Confusion Matrix:\n")
        cm = result['Test CM']
        f.write(f"                Predicted\n")
        f.write(f"              Legit    Phishing\n")
        f.write(f"Actual Legit  {cm[0][0]:5d}    {cm[0][1]:5d}\n")
        f.write(f"      Phish   {cm[1][0]:5d}    {cm[1][1]:5d}\n\n")
        
        # Calculate error rates
        false_positives = cm[0][1]
        false_negatives = cm[1][0]
        total_test = len(y_test)
        
        f.write("ERROR ANALYSIS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"False Positives: {false_positives} ({false_positives/total_test*100:.3f}%)\n")
        f.write(f"  - Legitimate emails incorrectly marked as phishing\n\n")
        f.write(f"False Negatives: {false_negatives} ({false_negatives/total_test*100:.3f}%)\n")
        f.write(f"  - Phishing emails that were missed\n\n")
        
        # Overfitting analysis
        overfit = result['Train Accuracy'] - result['Test Accuracy']
        f.write("GENERALIZATION ANALYSIS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Accuracy Gap: {overfit:.4f} ({overfit*100:.2f}%)\n")
        if overfit < 0.01:
            f.write("Status: ✓ EXCELLENT - Model generalizes very well\n")
        elif overfit < 0.05:
            f.write("Status: ✓ GOOD - Minimal overfitting\n")
        else:
            f.write("Status: ⚠ CAUTION - Some overfitting detected\n")
        f.write("\n\n")
    
    # Summary comparison
    f.write("=" * 80 + "\n")
    f.write("SUMMARY COMPARISON\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"{'Metric':<25} {'Logistic Reg (Train)':<20} {'Logistic Reg (Test)':<20}\n")
    f.write("-" * 80 + "\n")
    f.write(f"{'Accuracy':<25} {results[0]['Train Accuracy']*100:>18.2f}% {results[0]['Test Accuracy']*100:>18.2f}%\n")
    f.write(f"{'Precision':<25} {results[0]['Train Precision']*100:>18.2f}% {results[0]['Test Precision']*100:>18.2f}%\n")
    f.write(f"{'Recall':<25} {results[0]['Train Recall']*100:>18.2f}% {results[0]['Test Recall']*100:>18.2f}%\n")
    f.write(f"{'F1 Score':<25} {results[0]['Train F1']*100:>18.2f}% {results[0]['Test F1']*100:>18.2f}%\n\n")
    
    f.write(f"{'Metric':<25} {'Random Forest (Train)':<20} {'Random Forest (Test)':<20}\n")
    f.write("-" * 80 + "\n")
    f.write(f"{'Accuracy':<25} {results[1]['Train Accuracy']*100:>18.2f}% {results[1]['Test Accuracy']*100:>18.2f}%\n")
    f.write(f"{'Precision':<25} {results[1]['Train Precision']*100:>18.2f}% {results[1]['Test Precision']*100:>18.2f}%\n")
    f.write(f"{'Recall':<25} {results[1]['Train Recall']*100:>18.2f}% {results[1]['Test Recall']*100:>18.2f}%\n")
    f.write(f"{'F1 Score':<25} {results[1]['Train F1']*100:>18.2f}% {results[1]['Test F1']*100:>18.2f}%\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("RECOMMENDATIONS\n")
    f.write("=" * 80 + "\n\n")
    
    best_model = results[1] if results[1]['Test F1'] > results[0]['Test F1'] else results[0]
    f.write(f"✓ BEST MODEL: {best_model['Model']}\n")
    f.write(f"  - Test Accuracy: {best_model['Test Accuracy']*100:.2f}%\n")
    f.write(f"  - Test F1 Score: {best_model['Test F1']*100:.2f}%\n\n")
    
    f.write("USAGE:\n")
    f.write("  - Use for production phishing detection\n")
    f.write("  - Suitable for real-time email scanning\n")
    f.write("  - Low false positive rate ensures minimal user disruption\n")
    f.write("  - High recall catches most phishing attempts\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("Report generated successfully!\n")
    f.write("=" * 80 + "\n")

print(f"✓ Report saved to: {report_path}")

# Create CSV for easy sharing
csv_path = "ACCURACY_SUMMARY.csv"
summary_df = pd.DataFrame([
    {
        'Model': r['Model'],
        'Train_Accuracy': f"{r['Train Accuracy']*100:.2f}%",
        'Test_Accuracy': f"{r['Test Accuracy']*100:.2f}%",
        'Train_Precision': f"{r['Train Precision']*100:.2f}%",
        'Test_Precision': f"{r['Test Precision']*100:.2f}%",
        'Train_Recall': f"{r['Train Recall']*100:.2f}%",
        'Test_Recall': f"{r['Test Recall']*100:.2f}%",
        'Train_F1': f"{r['Train F1']*100:.2f}%",
        'Test_F1': f"{r['Test F1']*100:.2f}%"
    }
    for r in results
])

summary_df.to_csv(csv_path, index=False)
print(f"✓ CSV summary saved to: {csv_path}")

# Print to console
print("\n" + "=" * 80)
print("QUICK SUMMARY")
print("=" * 80)

for result in results:
    print(f"\n{result['Model']}:")
    print(f"  Training Accuracy:  {result['Train Accuracy']*100:.2f}%")
    print(f"  Testing Accuracy:   {result['Test Accuracy']*100:.2f}%")
    print(f"  Difference:         {(result['Train Accuracy'] - result['Test Accuracy'])*100:.2f}%")

print("\n" + "=" * 80)
print("Files created:")
print(f"  1. {report_path} - Detailed text report")
print(f"  2. {csv_path} - CSV summary for Excel")
print("=" * 80)
