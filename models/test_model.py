import pickle
import os

# Load the trained model and vectorizer
MODEL_DIR = "saved_models"

print("=" * 80)
print("PHISHING DETECTION - MODEL TESTING")
print("=" * 80)

# Load vectorizer
vectorizer_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
with open(vectorizer_path, 'rb') as f:
    vectorizer = pickle.load(f)
print("✓ Vectorizer loaded")

# Load model
model_path = os.path.join(MODEL_DIR, "logistic_regression_model.pkl")
with open(model_path, 'rb') as f:
    model = pickle.load(f)
print("✓ Logistic Regression model loaded\n")

# Test samples
test_samples = [
    {
        "text": "Dear valued customer, your account has been suspended. Click here immediately to restore access: http://suspicious-link.com/restore",
        "expected": "Phishing"
    },
    {
        "text": "Hi team, please review the quarterly report attached. Let's discuss in tomorrow's meeting. Thanks, Sarah",
        "expected": "Legitimate"
    },
    {
        "text": "WINNER! You have won $1,000,000! Claim your prize now by providing your bank details at: http://fake-lottery.com",
        "expected": "Phishing"
    },
    {
        "text": "Meeting scheduled for 3pm on Friday in Conference Room B. Agenda: Q4 budget review and strategic planning.",
        "expected": "Legitimate"
    },
    {
        "text": "Your payment has failed. Update your billing information within 24 hours or your account will be deleted: http://phishing-site.com/billing",
        "expected": "Phishing"
    }
]

print("Testing model on sample emails:\n")
print("=" * 80)

for idx, sample in enumerate(test_samples, 1):
    # Transform text
    text_vector = vectorizer.transform([sample['text']])
    
    # Predict
    prediction = model.predict(text_vector)[0]
    probability = model.predict_proba(text_vector)[0]
    
    predicted_label = "Phishing" if prediction == 1 else "Legitimate"
    confidence = probability[prediction] * 100
    
    # Display results
    print(f"\n[Test {idx}]")
    print(f"Text: {sample['text'][:100]}...")
    print(f"Expected:  {sample['expected']}")
    print(f"Predicted: {predicted_label}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Probabilities: Legitimate={probability[0]:.4f}, Phishing={probability[1]:.4f}")
    
    # Check if correct
    is_correct = predicted_label == sample['expected']
    print(f"Result: {'✓ CORRECT' if is_correct else '✗ INCORRECT'}")
    print("-" * 80)

print("\n" + "=" * 80)
print("Testing complete!")
print("=" * 80)
