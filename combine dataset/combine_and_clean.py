import pandas as pd
import numpy as np
import re
import os
import time
import datetime
from email import message_from_string
from email.utils import parsedate_to_datetime

# File paths
folder = r"c:\Users\ADMIN\OneDrive\Desktop\phsisng detector\Phishing-Detection-Assistant\combine dataset"
output_path = os.path.join(folder, "final_combined_dataset.csv")

# Unified columns schema
unified_columns = [
    # General & Text Columns
    'raw_text', 'subject', 'body_plain', 'body_html', 'from_address', 'from_domain', 
    'reply_to', 'to_addresses', 'cc_addresses', 'date', 'hour_of_day', 'message_id', 
    'in_reply_to', 'language', 'label', 'source',
    
    # Header & Security Features
    'num_received_headers', 'received_origin_ip', 'spf_result', 'dkim_result', 
    'dmarc_result', 'x_spam_score', 'user_agent', 'list_unsubscribe',
    
    # Content Indicators
    'has_html', 'num_urls', 'num_emails_in_body', 'num_phone_numbers', 'contains_tracking_token',
    
    # Attachment Features
    'has_attachments', 'attachment_types', 'attachment_name', 'attachment_extension', 
    'attachment_size', 'attachment_entropy', 'compression_ratio', 'sender_frequency', 
    'attachment_count', 'attachment_mime_type', 'attachment_is_archive', 'attachment_is_executable', 
    'attachment_entropy_bin', 'domain_reputation_score'
]

# Regex patterns
url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
phone_pattern = re.compile(r'\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')

def extract_domain(email_str):
    if not email_str or pd.isna(email_str):
        return ''
    email_str = str(email_str).strip()
    match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', email_str)
    return match.group(1).lower() if match else ''

def parse_rfc2822_date(date_str):
    if not date_str or pd.isna(date_str):
        return '', -1
    try:
        dt = parsedate_to_datetime(str(date_str).strip())
        iso_date = dt.strftime('%Y-%m-%dT%H:%M:%S')
        return iso_date, dt.hour
    except Exception:
        return str(date_str), -1

def parse_iso_date(date_str):
    if not date_str or pd.isna(date_str):
        return '', -1
    try:
        date_str = str(date_str).strip()
        if 'T' in date_str:
            dt = datetime.datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
            dt = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%dT%H:%M:%S'), dt.hour
    except Exception:
        return str(date_str), -1

def parse_raw_message(msg_str):
    try:
        msg = message_from_string(msg_str)
        
        # Headers
        subject = msg.get('Subject', '')
        from_address = msg.get('From', '')
        to_addresses = msg.get('To', '')
        cc_addresses = msg.get('Cc', '')
        reply_to = msg.get('Reply-To', '')
        in_reply_to = msg.get('In-Reply-To', '')
        date_header = msg.get('Date', '')
        message_id = msg.get('Message-ID', '')
        
        iso_date, hour_of_day = parse_rfc2822_date(date_header)
        from_domain = extract_domain(from_address)
        num_received_headers = len(msg.get_all('Received') or [])
        
        # Body
        body_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_parts.append(payload.decode('utf-8', errors='ignore'))
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body_parts.append(payload.decode('utf-8', errors='ignore'))
        
        body_plain = "\n".join(body_parts).strip()
        num_urls = len(url_pattern.findall(body_plain))
        num_emails_in_body = len(email_pattern.findall(body_plain))
        num_phone_numbers = len(phone_pattern.findall(body_plain))
        raw_text = f"Subject: {subject}\n{body_plain}"
        
        return {
            'raw_text': raw_text,
            'subject': subject,
            'body_plain': body_plain,
            'body_html': '',
            'from_address': from_address,
            'from_domain': from_domain,
            'reply_to': reply_to,
            'to_addresses': to_addresses,
            'cc_addresses': cc_addresses,
            'date': iso_date,
            'hour_of_day': hour_of_day,
            'message_id': message_id,
            'in_reply_to': in_reply_to,
            'language': 'en',
            'label': 0,
            'source': 'enron_emails',
            'num_received_headers': num_received_headers,
            'received_origin_ip': '',
            'spf_result': 'none',
            'dkim_result': 'none',
            'dmarc_result': 'none',
            'x_spam_score': np.nan,
            'user_agent': msg.get('X-Mailer', ''),
            'list_unsubscribe': '',
            'has_html': 0,
            'num_urls': num_urls,
            'num_emails_in_body': num_emails_in_body,
            'num_phone_numbers': num_phone_numbers,
            'contains_tracking_token': 0,
            'has_attachments': 0,
            'attachment_types': '',
            'attachment_name': '',
            'attachment_extension': '',
            'attachment_size': np.nan,
            'attachment_entropy': np.nan,
            'compression_ratio': np.nan,
            'sender_frequency': np.nan,
            'attachment_count': 0,
            'attachment_mime_type': '',
            'attachment_is_archive': 0,
            'attachment_is_executable': 0,
            'attachment_entropy_bin': '',
            'domain_reputation_score': np.nan
        }
    except Exception as e:
        return None

def main():
    print("=" * 60)
    print("STARTING DATASET COMBINATION AND CLEANING")
    print("=" * 60)
    start_time = time.time()
    
    # Check if files exist
    files_to_check = {
        "email_dataset_100k.csv": os.path.join(folder, "email_dataset_100k.csv"),
        "email-data.csv": os.path.join(folder, "email-data.csv"),
        "emails.csv": os.path.join(folder, "emails.csv")
    }
    
    for name, path in files_to_check.items():
        if not os.path.exists(path):
            print(f"Error: Required file {name} not found at {path}!")
            return
            
    # Remove old combined file if exists
    if os.path.exists(output_path):
        print("Removing existing combined file...")
        os.remove(output_path)

    # 1. PROCESS email_dataset_100k.csv
    print("\n--- [1/3] Processing email_dataset_100k.csv ---")
    df1 = pd.read_csv(files_to_check["email_dataset_100k.csv"])
    print(f"Loaded {len(df1)} rows.")
    
    # Cleaning df1
    df1 = df1.drop_duplicates(subset=['raw_text', 'message_id'], keep='first')
    df1['source'] = 'email_dataset_100k'
    
    # Ensure all target columns exist and are typed
    df1['label'] = df1['label'].fillna(0).astype(int)
    df1['hour_of_day'] = df1['hour_of_day'].fillna(-1).astype(int)
    df1['num_received_headers'] = df1['num_received_headers'].fillna(0).astype(int)
    df1['num_urls'] = df1['num_urls'].fillna(0).astype(int)
    df1['num_emails_in_body'] = df1['num_emails_in_body'].fillna(0).astype(int)
    df1['num_phone_numbers'] = df1['num_phone_numbers'].fillna(0).astype(int)
    df1['has_attachments'] = df1['has_attachments'].astype(int)
    df1['has_html'] = df1['has_html'].astype(int)
    df1['contains_tracking_token'] = df1['contains_tracking_token'].astype(int)
    
    # Standardize dates
    dates_parsed = [parse_iso_date(d) for d in df1['date']]
    df1['date'] = [d[0] for d in dates_parsed]
    df1['hour_of_day'] = [d[1] for d in dates_parsed]
    
    # Add empty columns for attachment features
    for col in unified_columns:
        if col not in df1.columns:
            df1[col] = np.nan
            
    # Write df1 with headers to start the combined file
    df1.to_csv(output_path, index=False, columns=unified_columns)
    print(f"Cleaned and wrote {len(df1)} rows from email_dataset_100k.csv")
    del df1 # Free memory

    # 2. PROCESS email-data.csv (Attachment Metadata) in chunks
    print("\n--- [2/3] Processing email-data.csv in chunks ---")
    chunk_size = 200000
    chunk_idx = 0
    total_attachment_rows = 0
    
    for chunk in pd.read_csv(files_to_check["email-data.csv"], chunksize=chunk_size):
        chunk_idx += 1
        print(f"Processing attachment data chunk {chunk_idx}...")
        
        # Deduplicate chunk
        chunk = chunk.drop_duplicates(subset=['email_id'], keep='first')
        
        # Mapping
        chunk['from_address'] = chunk['sender_email']
        chunk['from_domain'] = chunk['sender_domain']
        chunk['to_addresses'] = chunk['recipient_email']
        chunk['label'] = chunk['is_malicious'].fillna(0).astype(int)
        chunk['source'] = 'email_attachment_data'
        chunk['has_attachments'] = np.where(chunk['attachment_count'] > 0, 1, 0)
        chunk['attachment_types'] = chunk['attachment_extension']
        
        # Standardize date and hour
        dates_parsed = [parse_iso_date(d) for d in chunk['time_received']]
        chunk['date'] = [d[0] for d in dates_parsed]
        chunk['hour_of_day'] = [d[1] for d in dates_parsed]
        
        # Fill missing unified columns with NaNs/defaults
        for col in unified_columns:
            if col not in chunk.columns:
                chunk[col] = np.nan
        
        # Clean numeric attachment columns
        chunk['attachment_size'] = chunk['attachment_size'].fillna(0).astype(int)
        chunk['attachment_entropy'] = chunk['attachment_entropy'].fillna(0.0).astype(float)
        chunk['compression_ratio'] = chunk['compression_ratio'].fillna(0.0).astype(float)
        chunk['sender_frequency'] = chunk['sender_frequency'].fillna(0).astype(int)
        chunk['attachment_count'] = chunk['attachment_count'].fillna(0).astype(int)
        chunk['attachment_is_archive'] = chunk['attachment_is_archive'].fillna(0).astype(int)
        chunk['attachment_is_executable'] = chunk['attachment_is_executable'].fillna(0).astype(int)
        chunk['domain_reputation_score'] = chunk['domain_reputation_score'].fillna(0.0).astype(float)
        
        # Append chunk
        chunk.to_csv(output_path, mode='a', header=False, index=False, columns=unified_columns)
        total_attachment_rows += len(chunk)
        
    print(f"Finished email-data.csv: processed {total_attachment_rows} rows.")

    # 3. PROCESS emails.csv (Enron) in chunks
    print("\n--- [3/3] Processing emails.csv (Enron) in chunks ---")
    enron_chunk_size = 50000
    enron_chunk_idx = 0
    total_enron_rows = 0
    seen_message_ids = set()
    
    for chunk in pd.read_csv(files_to_check["emails.csv"], chunksize=enron_chunk_size):
        enron_chunk_idx += 1
        print(f"Processing Enron chunk {enron_chunk_idx}...")
        
        parsed_chunk_data = []
        for msg in chunk['message']:
            parsed = parse_raw_message(msg)
            if parsed:
                # Memory efficient deduplication of Message-ID
                msg_id = parsed['message_id']
                if msg_id:
                    if msg_id in seen_message_ids:
                        continue
                    seen_message_ids.add(msg_id)
                parsed_chunk_data.append(parsed)
                
        if parsed_chunk_data:
            df_parsed_chunk = pd.DataFrame(parsed_chunk_data)
            
            # Fill missing columns
            for col in unified_columns:
                if col not in df_parsed_chunk.columns:
                    df_parsed_chunk[col] = np.nan
                    
            # Append chunk
            df_parsed_chunk.to_csv(output_path, mode='a', header=False, index=False, columns=unified_columns)
            total_enron_rows += len(df_parsed_chunk)
            
    print(f"Finished emails.csv: processed {total_enron_rows} rows.")

    # Verification
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("DATASET COMBINATION AND CLEANING COMPLETE!")
    print("=" * 60)
    print(f"Time Taken: {elapsed_time/60:.2f} minutes")
    print(f"Combined File Path: {output_path}")
    if os.path.exists(output_path):
        size_gb = os.path.getsize(output_path) / (1024 * 1024 * 1024)
        print(f"Output File Size: {size_gb:.2f} GB")
        
        # Print a small overview of counts
        print("\nVerifying combined dataset row count...")
        total_rows = 0
        for chk in pd.read_csv(output_path, usecols=['source'], chunksize=200000):
            total_rows += len(chk)
        print(f"Verified Total Rows: {total_rows}")
    print("=" * 60)

if __name__ == "__main__":
    main()
