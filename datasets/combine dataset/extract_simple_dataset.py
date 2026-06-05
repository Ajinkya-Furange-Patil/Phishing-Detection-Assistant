import pandas as pd
import numpy as np
import os
import time

# Configuration
INPUT_FILE = "final_unique_sample_25.csv"  # Can also use "final_combined_dataset.csv" when available
OUTPUT_FILE = "simple_dataset.csv"
CHUNK_SIZE = 200000

def clean_text(text):
    """Clean and prepare text data."""
    if pd.isna(text) or text == '':
        return ''
    text = str(text).strip()
    # Remove excessive whitespace
    text = ' '.join(text.split())
    return text

def combine_subject_body(subject, body):
    """Combine subject and body into a single text field."""
    subject = clean_text(subject)
    body = clean_text(body)
    
    if subject and body:
        return f"{subject} {body}"
    elif subject:
        return subject
    elif body:
        return body
    else:
        return ''

def process_chunk(chunk):
    """Process a chunk of data to extract subject, body, and label."""
    # Extract relevant columns
    result = pd.DataFrame()
    
    # Combine subject and body_plain into a single text field
    result['text'] = chunk.apply(
        lambda row: combine_subject_body(row.get('subject', ''), row.get('body_plain', '')),
        axis=1
    )
    
    # Extract label (ensure it's 0 or 1)
    result['label'] = chunk['label'].fillna(0).astype(int)
    
    # Filter out empty texts
    result = result[result['text'].str.len() > 0]
    
    return result

def main():
    print("=" * 60)
    print("EXTRACTING SIMPLE DATASET (subject + body + label)")
    print("=" * 60)
    start_time = time.time()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_FILE)
    output_path = os.path.join(script_dir, OUTPUT_FILE)
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        print("Please run combine_and_clean.py first to generate the combined dataset.")
        return
    
    # Remove old output file if exists
    if os.path.exists(output_path):
        print(f"Removing existing output file: {OUTPUT_FILE}")
        os.remove(output_path)
    
    print(f"\nInput: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Chunk size: {CHUNK_SIZE:,} rows\n")
    
    # Process in chunks
    chunk_idx = 0
    total_rows_processed = 0
    total_rows_kept = 0
    first_chunk = True
    
    try:
        for chunk in pd.read_csv(input_path, chunksize=CHUNK_SIZE, low_memory=False):
            chunk_idx += 1
            print(f"Processing chunk {chunk_idx}... ", end='', flush=True)
            
            # Process the chunk
            processed = process_chunk(chunk)
            
            # Write to output
            if first_chunk:
                processed.to_csv(output_path, index=False, mode='w')
                first_chunk = False
            else:
                processed.to_csv(output_path, index=False, mode='a', header=False)
            
            total_rows_processed += len(chunk)
            total_rows_kept += len(processed)
            
            print(f"kept {len(processed):,} / {len(chunk):,} rows")
            
    except Exception as e:
        print(f"\nError processing file: {e}")
        return
    
    # Final statistics
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"Time Taken: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"Total Rows Processed: {total_rows_processed:,}")
    print(f"Total Rows Kept: {total_rows_kept:,}")
    print(f"Rows Filtered Out: {total_rows_processed - total_rows_kept:,}")
    
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Output File Size: {size_mb:.2f} MB")
        
        # Verify and show class distribution
        print("\nVerifying output dataset...")
        label_counts = pd.Series(dtype=int)
        for chunk in pd.read_csv(output_path, chunksize=CHUNK_SIZE):
            label_counts = label_counts.add(chunk['label'].value_counts(), fill_value=0)
        
        print(f"\nClass Distribution:")
        print(f"  Legitimate (0): {int(label_counts.get(0, 0)):,} ({int(label_counts.get(0, 0))/total_rows_kept*100:.2f}%)")
        print(f"  Phishing (1):   {int(label_counts.get(1, 0)):,} ({int(label_counts.get(1, 0))/total_rows_kept*100:.2f}%)")
        
        # Show sample
        print("\nSample rows:")
        sample_df = pd.read_csv(output_path, nrows=3)
        for idx, row in sample_df.iterrows():
            print(f"\n[Row {idx+1}]")
            print(f"  Label: {row['label']}")
            print(f"  Text: {row['text'][:150]}...")
    
    print("\n" + "=" * 60)
    print(f"Output saved to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
