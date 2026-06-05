# Requirements Document

## Introduction

The Email Phishing Detection Pipeline is a browser extension system that integrates a BERT-based machine learning model to analyze and detect phishing attempts in email content. The system extracts email data from webmail platforms (Gmail and Outlook), processes it through a formatting layer using the Gemini API, and performs inference using a trained BERT model. The system provides real-time phishing detection results to users through a visual interface integrated with their email client.

## Glossary

- **Extension**: The browser extension component that runs in Chrome and Firefox browsers
- **Email_Scraper**: The content script module that extracts email data from webmail DOM structures
- **Gemini_API**: Google's Gemini API service used for content extraction and formatting
- **BERT_Model**: Bidirectional Encoder Representations from Transformers model trained on final_unique_sample_25.csv dataset
- **Inference_Pipeline**: The complete data flow from email extraction to phishing prediction
- **Backend_Server**: The local Flask development server that hosts the BERT model inference endpoint
- **Detection_Result**: The output containing phishing classification and confidence score
- **Frontend_Structure**: The existing popup.html, popup.js, and content script architecture
- **Cross_Browser**: Support for both Chrome and Firefox browser environments

## Requirements

### Requirement 1: Email Content Extraction

**User Story:** As a user, I want the extension to automatically extract complete email information when I open an email, so that the system can analyze it for phishing threats.

#### Acceptance Criteria

1. WHEN a user opens an email in Gmail, THE Email_Scraper SHALL extract the email subject line
2. WHEN a user opens an email in Gmail, THE Email_Scraper SHALL extract the sender email address
3. WHEN a user opens an email in Gmail, THE Email_Scraper SHALL extract the complete email body text
4. WHEN a user opens an email in Gmail, THE Email_Scraper SHALL extract all email headers available in the DOM
5. WHEN a user opens an email in Gmail, THE Email_Scraper SHALL extract all URLs present in the email body
6. WHEN a user opens an email in Gmail, THE Email_Scraper SHALL extract attachment metadata including filename and size
7. WHEN a user opens an email in Outlook, THE Email_Scraper SHALL extract the email subject line
8. WHEN a user opens an email in Outlook, THE Email_Scraper SHALL extract the sender email address
9. WHEN a user opens an email in Outlook, THE Email_Scraper SHALL extract the complete email body text
10. WHEN a user opens an email in Outlook, THE Email_Scraper SHALL extract all email headers available in the DOM
11. WHEN a user opens an email in Outlook, THE Email_Scraper SHALL extract all URLs present in the email body
12. WHEN a user opens an email in Outlook, THE Email_Scraper SHALL extract attachment metadata including filename and size
13. IF the email body cannot be extracted, THEN THE Email_Scraper SHALL log an error message and return null
14. WHEN extraction completes successfully, THE Email_Scraper SHALL return a structured JSON object containing all extracted fields

### Requirement 2: Cross-Browser Compatibility

**User Story:** As a user, I want to use the phishing detection extension in my preferred browser, so that I can maintain my existing workflow regardless of browser choice.

#### Acceptance Criteria

1. THE Extension SHALL run on Chrome browser version 88 or higher
2. THE Extension SHALL run on Firefox browser version 78 or higher
3. WHEN installed in Chrome, THE Extension SHALL use Manifest V3 format
4. WHEN installed in Firefox, THE Extension SHALL use Manifest V2 compatibility mode
5. THE Extension SHALL maintain identical functionality across Chrome and Firefox
6. WHEN the extension is activated in either browser, THE Extension SHALL display the same user interface
7. THE Extension SHALL use browser-agnostic APIs for storage and messaging
8. IF a browser-specific API is required, THEN THE Extension SHALL implement a compatibility layer to normalize behavior

### Requirement 3: Gemini API Integration

**User Story:** As a developer, I want the extracted email data to be formatted and structured through the Gemini API, so that the BERT model receives consistent and well-formatted input regardless of email platform variations.

#### Acceptance Criteria

1. WHEN email data is extracted, THE Inference_Pipeline SHALL send the raw data to the Gemini_API
2. THE Gemini_API SHALL normalize the email text formatting by removing HTML tags
3. THE Gemini_API SHALL structure the email data into a standardized JSON schema
4. THE Gemini_API SHALL extract and highlight suspicious text patterns
5. THE Gemini_API SHALL return the formatted data within 2 seconds
6. IF the Gemini_API request fails, THEN THE Inference_Pipeline SHALL retry up to 3 times with exponential backoff
7. IF all Gemini_API retries fail, THEN THE Inference_Pipeline SHALL fall back to basic text cleaning and proceed with inference
8. THE Gemini_API SHALL authenticate using an API key stored in secure browser storage
9. WHEN formatting is complete, THE Gemini_API SHALL return a response containing cleaned subject, body, and metadata

### Requirement 4: BERT Model Inference

**User Story:** As a user, I want my emails to be analyzed by a trained machine learning model, so that I can receive accurate phishing detection results based on learned patterns.

#### Acceptance Criteria

1. THE BERT_Model SHALL be trained on the final_unique_sample_25.csv dataset
2. WHEN formatted email data is received, THE Backend_Server SHALL load the trained BERT_Model from disk
3. THE BERT_Model SHALL tokenize the input text using BERT tokenizer with max length 512 tokens
4. THE BERT_Model SHALL perform forward pass inference on the tokenized input
5. THE BERT_Model SHALL output a phishing probability score between 0.0 and 1.0
6. THE Backend_Server SHALL return inference results within 3 seconds for inputs under 512 tokens
7. IF the input exceeds 512 tokens, THEN THE BERT_Model SHALL truncate the input to 512 tokens
8. THE BERT_Model SHALL achieve minimum 85% accuracy on validation data
9. WHEN inference completes, THE Backend_Server SHALL return a JSON response with isPhishing boolean and confidence score

### Requirement 5: Local Development Server

**User Story:** As a developer, I want to run the inference backend on my local machine, so that I can develop and test the system without requiring cloud infrastructure.

#### Acceptance Criteria

1. THE Backend_Server SHALL run on localhost at port 5000
2. THE Backend_Server SHALL implement a Flask web server
3. THE Backend_Server SHALL expose a POST endpoint at /api/scan
4. WHEN the server starts, THE Backend_Server SHALL load the BERT_Model into memory
5. THE Backend_Server SHALL enable CORS to accept requests from browser extensions
6. THE Backend_Server SHALL accept JSON payloads containing email data
7. THE Backend_Server SHALL validate incoming requests contain required fields
8. IF a required field is missing, THEN THE Backend_Server SHALL return HTTP 400 with error message
9. WHEN inference completes successfully, THE Backend_Server SHALL return HTTP 200 with detection results
10. IF inference fails, THEN THE Backend_Server SHALL return HTTP 500 with error details
11. THE Backend_Server SHALL log all requests and responses for debugging
12. THE Backend_Server SHALL implement a /api/health endpoint that returns server status

### Requirement 6: Single-Module MVP Pipeline

**User Story:** As a developer implementing Phase 1, I want to build a simplified pipeline using only the BERT content analysis module, so that I can validate the end-to-end workflow before adding additional detection modules.

#### Acceptance Criteria

1. THE Inference_Pipeline SHALL implement only Module 1 content analysis in Phase 1
2. THE Inference_Pipeline SHALL exclude URL analysis (Module 2) in Phase 1
3. THE Inference_Pipeline SHALL exclude header analysis (Module 3) in Phase 1
4. THE Inference_Pipeline SHALL exclude attachment analysis (Module 4) in Phase 1
5. THE Inference_Pipeline SHALL exclude behavioral analysis (Module 5) in Phase 1
6. WHEN email data is received, THE Inference_Pipeline SHALL send only subject and body text to the BERT_Model
7. THE Detection_Result SHALL contain only the BERT_Model confidence score
8. THE Detection_Result SHALL not include module-specific scores for modules 2-5
9. THE Inference_Pipeline SHALL use a simple threshold of 0.5 to determine isPhishing classification
10. WHERE future expansion is planned, THE Backend_Server SHALL structure the API response to accommodate additional module scores

### Requirement 7: Frontend Integration

**User Story:** As a user, I want to see phishing detection results displayed within my email interface, so that I can make informed decisions about email safety without leaving my mailbox.

#### Acceptance Criteria

1. THE Extension SHALL integrate with the existing popup.html interface
2. WHEN the user clicks the extension icon, THE Extension SHALL display the popup interface
3. THE Extension SHALL include a "Scan Email" button in the popup
4. WHEN the "Scan Email" button is clicked, THE Extension SHALL extract email data from the active tab
5. THE Extension SHALL send the extracted data to the Backend_Server endpoint
6. WHILE the request is processing, THE Extension SHALL display a loading indicator
7. WHEN the response is received, THE Extension SHALL hide the loading indicator
8. IF isPhishing is true, THEN THE Extension SHALL display a red warning banner in the email interface
9. IF isPhishing is false, THEN THE Extension SHALL display a green safe banner in the email interface
10. THE Extension SHALL display the confidence score as a percentage in the banner
11. THE Extension SHALL provide a dismiss button to remove the banner
12. IF the Backend_Server is not reachable, THEN THE Extension SHALL display an error message "Backend server unavailable"
13. THE Extension SHALL maintain visual consistency with the existing styles in popup.css and content.css

### Requirement 8: Data Flow Architecture

**User Story:** As a system architect, I want a clear and maintainable data flow from extension activation to result display, so that the system can be debugged, tested, and extended efficiently.

#### Acceptance Criteria

1. WHEN the extension is activated, THE Extension SHALL trigger the Email_Scraper
2. WHEN email data is extracted, THE Email_Scraper SHALL pass the data to the background service worker
3. WHEN the background worker receives data, THE Extension SHALL send the data to the Gemini_API for formatting
4. WHEN Gemini_API formatting completes, THE Extension SHALL send the formatted data to the Backend_Server
5. WHEN the Backend_Server receives data, THE BERT_Model SHALL perform inference
6. WHEN inference completes, THE Backend_Server SHALL return the Detection_Result to the Extension
7. WHEN the Extension receives the result, THE Extension SHALL display the result in the content script UI
8. THE Inference_Pipeline SHALL log each step completion with timestamp for debugging
9. IF any step fails, THEN THE Inference_Pipeline SHALL log the error and terminate gracefully
10. THE Inference_Pipeline SHALL complete the full workflow within 10 seconds from activation to display

### Requirement 9: Model Training Data

**User Story:** As a machine learning engineer, I want to train the BERT model on the specified dataset, so that the model learns to distinguish phishing patterns from legitimate email patterns.

#### Acceptance Criteria

1. THE BERT_Model SHALL be trained using the final_unique_sample_25.csv dataset
2. THE final_unique_sample_25.csv dataset SHALL contain labeled examples of phishing and legitimate emails
3. THE BERT_Model SHALL use 80% of the dataset for training
4. THE BERT_Model SHALL use 10% of the dataset for validation
5. THE BERT_Model SHALL use 10% of the dataset for testing
6. THE BERT_Model SHALL implement data stratification to maintain class balance in splits
7. THE BERT_Model SHALL be fine-tuned from the bert-base-uncased pretrained checkpoint
8. THE BERT_Model training SHALL use a learning rate between 1e-5 and 5e-5
9. THE BERT_Model training SHALL use batch size of 16 or 32 depending on available GPU memory
10. THE BERT_Model training SHALL run for minimum 3 epochs
11. THE BERT_Model SHALL save the best checkpoint based on validation accuracy
12. WHEN training completes, THE BERT_Model SHALL save the final weights to disk in the models directory

### Requirement 10: Error Handling and Resilience

**User Story:** As a user, I want the system to handle errors gracefully, so that temporary failures do not prevent me from reading my emails or cause the extension to crash.

#### Acceptance Criteria

1. IF email extraction fails, THEN THE Extension SHALL display "Unable to extract email data" message
2. IF the Gemini_API is unavailable, THEN THE Inference_Pipeline SHALL use fallback text cleaning
3. IF the Backend_Server is offline, THEN THE Extension SHALL display "Phishing detection unavailable - please start the backend server"
4. IF the BERT_Model inference times out, THEN THE Backend_Server SHALL return an error after 5 seconds
5. IF network requests fail, THEN THE Extension SHALL retry once before displaying error
6. THE Extension SHALL not block the user's ability to read emails even if detection fails
7. THE Extension SHALL log all errors to the browser console for debugging
8. IF an unexpected error occurs, THEN THE Extension SHALL display "An unexpected error occurred" message
9. THE Extension SHALL not expose internal error details or stack traces to the user interface
10. WHEN an error occurs, THE Extension SHALL allow the user to manually retry the scan
