"""
Dataset Preparation Script for BERT Phishing Detection Pipeline

This script processes the combined dataset (final_unique_sample_25.csv or final_combined_dataset.csv)
and extracts only the columns needed for BERT training that match the inference pipeline format:
- subject
- body_plain
- label

The script also simulates Gemini API normalization (HTML stripping, text cleaning) to ensure
training data matches the format that will be received during inference.

Output: bert_training_data.csv
"""

import pandas as pd
import numpy as np
import re
import os
from html import unescape

def clean_html_and_normalize(text):
    """
    Simulates Gemini API text normalization:
    - Remove HTML tags
    - Unescape HTML entities
    - Remove extra whitespace
    - Strip leading/trailing whitespace
    """
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Unescape HTML entities (&nbsp; -> space, &lt; -> <, etc.)
    text = unescape(text)
    
    # Remove URLs (optional - depends on your Gemini API behavior)
    # Uncomment if you want to strip URLs during training
    # text = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+', '[URL]', text)
    
    # Remove email addresses from body (optional)
    # text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)
    
    # Remove multiple whitespace/newlines
    text = ' '.join(text.split())
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def prepare_bert_dataset(input_csv_path, output_csv_path, sample_size=None):
    """
    Prepares dataset for BERT training from combined dataset.
    
    Args:
        input_csv_path: Path to final_unique_sample_25.csv or final_combined_dataset.csv
        output_csv_path: Path to save the prepared dataset
        sample_size: Optional - number of rows to sample (for testing)
    """
    print("=" * 70)
    print("BERT TRAINING DATA PREPARATION")
    print("=" * 70)
    print(f"Input: {input_csv_path}")
    print(f"Output: {output_csv_path}")
    
    # Check if input file exists
    if not os.path.exists(input_csv_path):
        print(f"ERROR: Input file not found: {input_csv_path}")
        return
    
    print("\n[1/5] Loading dataset...")
    # Load only needed columns to save memory
    try:
        if sample_size:
            df = pd.read_csv(input_csv_path, usecols=['subject', 'body_plain', 'body_html', 'label'], nrows=sample_size)
            print(f"Loaded {len(df)} rows (sample mode)")
        else:
            df = pd.read_csv(input_csv_path, usecols=['subject', 'body_plain', 'body_html', 'label'])
            print(f"Loaded {len(df)} rows")
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
        return
    
    print(f"Initial dataset shape: {df.shape}")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    
    print("\n[2/5] Filling missing values...")
    df['subject'] = df['subject'].fillna('')
    df['body_plain'] = df['body_plain'].fillna('')
    df['body_html'] = df['body_html'].fillna('')
    
    # Use body_html if body_plain is empty, otherwise use body_plain
    df['body'] = df.apply(
        lambda row: row['body_html'] if row['body_plain'] == '' else row['body_plain'],
        axis=1
    )
    
    # Drop rows with empty subject AND body
    initial_len = len(df)
    df = df[(df['subject'] != '') | (df['body'] != '')]
    dropped = initial_len - len(df)
    print(f"Dropped {dropped} rows with empty subject and body")
    
    print("\n[3/5] Normalizing text (simulating Gemini API)...")
    # Apply Gemini-like cleaning
    df['subject_clean'] = df['subject'].apply(clean_html_and_normalize)
    df['body_clean'] = df['body'].apply(clean_html_and_normalize)
    
    print("\n[4/5] Creating combined text for BERT input...")
    # Create combined text: subject + body (matches inference format)
    df['text'] = df['subject_clean'] + ' ' + df['body_clean']
    
    # Remove extra spaces
    df['text'] = df['text'].apply(lambda x: ' '.join(x.split()))
    
    # Drop rows with empty text after cleaning
    initial_len = len(df)
    df = df[df['text'].str.strip() != '']
    dropped = initial_len - len(df)
    print(f"Dropped {dropped} rows with empty text after cleaning")
    
    print("\n[5/5] Saving prepared dataset...")
    # Keep only necessary columns for training
    df_final = df[['text', 'label']].copy()
    
    # Ensure label is binary (0 or 1)
    df_final['label'] = df_final['label'].astype(int)
    
    # Save to CSV
    df_final.to_csv(output_csv_path, index=False)
    
    print("\n" + "=" * 70)
    print("PREPARATION COMPLETE!")
    print("=" * 70)
    print(f"Output file: {output_csv_path}")
    print(f"Final dataset shape: {df_final.shape}")
    print(f"Final label distribution:\n{df_final['label'].value_counts()}")
    
    # Calculate and display statistics
    print("\n--- Text Length Statistics ---")
    df_final['text_length'] = df_final['text'].str.len()
    print(f"Mean text length: {df_final['text_length'].mean():.2f} characters")
    print(f"Median text length: {df_final['text_length'].median():.2f} characters")
    print(f"Max text length: {df_final['text_length'].max()} characters")
    print(f"Min text length: {df_final['text_length'].min()} characters")
    
    # Estimate token counts (rough approximation: 1 token ≈ 4 characters for English)
    df_final['approx_tokens'] = df_final['text_length'] / 4
    print(f"\n--- Approximate Token Counts ---")
    print(f"Mean tokens: {df_final['approx_tokens'].mean():.2f}")
    print(f"Median tokens: {df_final['approx_tokens'].median():.2f}")
    print(f"% exceeding 512 tokens: {(df_final['approx_tokens'] > 512).sum() / len(df_final) * 100:.2f}%")
    
    # Show sample rows
    print("\n--- Sample Rows ---")
    print(df_final.head(3))
    
    print("\n" + "=" * 70)
    print("Ready for BERT training!")
    print("=" * 70)

def main():
    # Configuration
    base_path = r"c:\Users\Ajinkya Patil\OneDrive\Desktop\Internship\Phishing Detection Assistant\datasets\combine dataset"
    
    # Try to find the input file (check both possible names)
    input_candidates = [
        os.path.join(base_path, "final_unique_sample_25.csv"),
        os.path.join(base_path, "final_combined_dataset.csv")
    ]
    
    input_file = None
    for candidate in input_candidates:
        if os.path.exists(candidate):
            input_file = candidate
            break
    
    if input_file is None:
        print("ERROR: Could not find input dataset!")
        print("Expected one of:")
        for candidate in input_candidates:
            print(f"  - {candidate}")
        return
    
    output_file = os.path.join(base_path, "bert_training_data.csv")
    
    # For testing with small sample, uncomment the line below:
    # prepare_bert_dataset(input_file, output_file, sample_size=10000)
    
    # Full dataset processing:
    prepare_bert_dataset(input_file, output_file)

if __name__ == "__main__":
    main()
