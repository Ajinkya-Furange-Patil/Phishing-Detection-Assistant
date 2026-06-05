# Implementation Plan: Email Phishing Detection Pipeline

## Overview

This implementation plan breaks down the Email Phishing Detection Pipeline into discrete coding tasks. The system consists of a browser extension frontend (JavaScript) that extracts email data from Gmail and Outlook, integrates with the Gemini API for content normalization, and communicates with a Flask backend server (Python) that hosts a BERT-based machine learning model for phishing detection. This Phase 1 MVP focuses exclusively on content-based analysis (Module 1), establishing the foundational pipeline architecture.

## Tasks

- [ ] 1. Set up project structure and BERT model training
  - [ ] 1.1 Create backend directory structure and training script
    - Create `backend/` directory with subdirectories: `models/`, `data/`, `utils/`
    - Create `backend/train_bert.py` script for BERT model training
    - Implement data loading from `datasets/combine dataset/final_unique_sample_25.csv`
    - Implement 80-10-10 train-validation-test split with stratification
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 1.2 Write property test for dataset split stratification
    - **Property 6: BERT Output Range Invariant**
    - Test that BERT inference outputs are always in [0.0, 1.0] range
    - **Validates: Requirements 4.5**

  - [ ] 1.3 Implement BERT fine-tuning configuration
    - Load `bert-base-uncased` pretrained checkpoint
    - Configure hyperparameters: learning rate (2e-5), batch size (16), max_length (512), epochs (3)
    - Implement training loop with validation checkpointing
    - Save best model weights to `backend/models/bert_phishing_detector.pth`
    - _Requirements: 9.7, 9.8, 9.9, 9.10, 9.11, 9.12_

  - [ ]* 1.4 Write property test for tokenization length constraint
    - **Property 5: BERT Tokenization Length Constraint**
    - Test that tokenized outputs never exceed 512 tokens
    - **Validates: Requirements 4.3, 4.7**

- [ ] 2. Checkpoint - Train BERT model and verify output
  - Train the BERT model using the training script
  - Verify model achieves minimum 85% validation accuracy
  - Confirm model weights saved to disk
  - Ensure all tests pass, ask the user if questions arise

- [ ] 3. Implement Flask backend server
  - [ ] 3.1 Create Flask application structure
    - Create `backend/app.py` with Flask initialization
    - Configure CORS to accept requests from browser extensions (chrome-extension://* and moz-extension://*)
    - Implement `/api/scan` POST endpoint with request validation
    - Implement `/api/health` GET endpoint
    - _Requirements: 5.2, 5.3, 5.5, 5.12_

  - [ ] 3.2 Implement BERT model loading and inference
    - Create `backend/bert_model.py` with BERTModel class
    - Implement model loading from saved weights in `__init__`
    - Implement `tokenize(text)` method with max_length=512 truncation
    - Implement `predict(tokens)` method returning confidence score in [0.0, 1.0]
    - _Requirements: 4.2, 4.3, 4.4, 4.5_

  - [ ]* 3.3 Write property test for inference response structure
    - **Property 7: Inference Response Structure**
    - Test that all successful inferences return required fields (isPhishing, confidence, module_scores)
    - **Validates: Requirements 4.9**

  - [ ] 3.4 Implement request validation and error handling
    - Validate required fields (subject, body, sender) in POST /api/scan
    - Return HTTP 400 for missing required fields
    - Return HTTP 500 for inference failures
    - Implement request/response logging
    - Set inference timeout to 5 seconds
    - _Requirements: 5.7, 5.8, 5.9, 5.10, 5.11_

  - [ ]* 3.5 Write property test for backend request validation
    - **Property 8: Backend Request Validation**
    - Test that requests missing required fields return HTTP 400
    - **Validates: Requirements 5.7, 5.8**

  - [ ] 3.6 Implement Phase 1 MVP inference logic
    - Extract only subject and body from request payload (exclude URLs, headers, attachments)
    - Concatenate subject and body for BERT input
    - Apply threshold classification: isPhishing = (confidence > 0.5)
    - Return response with only content module score (no module 2-5 scores)
    - Structure response to accommodate future module scores
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10_

  - [ ]* 3.7 Write property test for Phase 1 module exclusivity
    - **Property 10: Phase 1 Module Exclusivity**
    - Test that only subject and body are sent to BERT (no URL, header, attachment data)
    - **Property 11: Phase 1 Response Module Constraint**
    - Test that responses contain only content module score
    - **Validates: Requirements 6.6, 6.7, 6.8**

- [ ] 4. Checkpoint - Backend server functional verification
  - Start Flask backend server on localhost:5000
  - Test /api/health endpoint returns status
  - Test /api/scan endpoint with sample email data
  - Verify BERT inference completes within 3 seconds
  - Ensure all tests pass, ask the user if questions arise

- [ ] 5. Implement Gemini API integration layer
  - [ ] 5.1 Create Gemini API client module
    - Create `backend/gemini_client.py` with GeminiAPIClient class
    - Implement `formatEmail(emailData)` method for HTML removal and normalization
    - Implement retry logic with exponential backoff (3 retries: 1s, 2s, 4s)
    - Implement 2-second timeout for API requests
    - Implement `fallbackClean(emailData)` for basic text cleaning on API failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ] 5.2 Implement Gemini API request formatting
    - Create prompt template for email normalization and suspicious pattern extraction
    - Implement API key retrieval from environment variables
    - Format response into standardized FormattedEmail schema with cleaned_subject, cleaned_body, suspicious_patterns, metadata
    - _Requirements: 3.8, 3.9_

  - [ ]* 5.3 Write property test for Gemini API schema conformance
    - **Property 4: Gemini API Schema Conformance**
    - Test that responses always contain required fields (cleaned_subject, cleaned_body, suspicious_patterns, metadata)
    - **Validates: Requirements 3.3, 3.9**

  - [ ] 5.4 Integrate Gemini formatting into Flask endpoint
    - Add Gemini API call before BERT inference in /api/scan endpoint
    - Use formatted data for inference if Gemini succeeds
    - Fall back to basic cleaning if Gemini fails after retries
    - _Requirements: 3.7_

- [ ] 6. Implement browser extension email extraction
  - [ ] 6.1 Implement Gmail email extraction
    - Create or update `frontend/content-gmail.js` with extractGmailEmailData() function
    - Implement DOM selectors for Gmail: subject (h2.hP), sender (span.gD[email]), body (div.a3s.aiL), links, attachments
    - Extract all required fields: subject, sender, body, headers, links, attachments
    - Return structured ExtractedEmail JSON object with platform="gmail"
    - Implement error handling: return null and log error on extraction failure
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.13, 1.14_

  - [ ]* 6.2 Write property test for Gmail extraction structure validity
    - **Property 1: Email Extraction Structure Validity**
    - Test that successful extraction returns valid JSON with all required fields
    - **Property 2: Extraction Error Handling**
    - Test that extraction failures return null without throwing exceptions
    - **Validates: Requirements 1.1-1.14**

  - [ ] 6.3 Implement Outlook email extraction
    - Create or update `frontend/content-outlook.js` with extractOutlookEmailData() function
    - Implement DOM selectors for Outlook: subject ([role="heading"]), sender ([aria-label*="From"]), body ([role="document"]), links, attachments
    - Extract all required fields: subject, sender, body, headers, links, attachments
    - Return structured ExtractedEmail JSON object with platform="outlook"
    - Implement error handling: return null and log error on extraction failure
    - _Requirements: 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14_

  - [ ]* 6.4 Write unit tests for Outlook extraction
    - Test extraction with mock Outlook DOM structures
    - Test error handling when required elements are missing
    - _Requirements: 1.7-1.14_

- [ ] 7. Implement banner display and result rendering
  - [ ] 7.1 Create banner display functions in content scripts
    - Implement `displayBanner(result)` function in both content-gmail.js and content-outlook.js
    - Create red warning banner for isPhishing=true with confidence percentage
    - Create green safe banner for isPhishing=false with confidence percentage
    - Add dismiss button to banners
    - Apply styles from `frontend/styles/content.css`
    - _Requirements: 7.8, 7.9, 7.10, 7.11_

  - [ ]* 7.2 Write property tests for banner display rules
    - **Property 13: Phishing Banner Display Rule**
    - Test that isPhishing=true always displays red warning banner
    - **Property 14: Safe Banner Display Rule**
    - Test that isPhishing=false always displays green safe banner
    - **Property 15: Confidence Score Display Format**
    - Test that confidence scores are displayed as percentages
    - **Validates: Requirements 7.8, 7.9, 7.10**

  - [ ] 7.3 Implement banner removal function
    - Implement `clearBanner()` function to remove existing banners
    - Call clearBanner() before displaying new banner to prevent duplicates
    - _Requirements: 7.11_

- [ ] 8. Implement extension communication layer
  - [ ] 8.1 Update background service worker message handling
    - Update `frontend/background.js` to handle 'analyzeEmail' messages
    - Implement `analyzeEmailBackground(emailData)` function to call Gemini API then Flask backend
    - Retrieve API endpoint from chrome.storage.sync (default: http://localhost:5000/api/scan)
    - Send formatted data to /api/scan endpoint
    - Return detection result to sender
    - _Requirements: 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ] 8.2 Implement popup interface scan functionality
    - Update `frontend/popup.js` to handle "Scan Email" button click
    - Send 'extractEmail' message to active tab content script
    - Display loading indicator while processing
    - Send extracted data to background worker for analysis
    - Display result by sending 'showWarning' message to content script
    - Hide loading indicator on response
    - _Requirements: 7.3, 7.4, 7.5, 7.6, 7.7_

  - [ ] 8.3 Implement error handling in extension
    - Display "Backend server unavailable" message when backend is offline
    - Display "Unable to extract email data" when extraction fails
    - Allow manual retry on errors
    - Ensure errors don't block user's ability to read emails
    - Log all errors to console without exposing internal details in UI
    - _Requirements: 10.1, 10.3, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10_

  - [ ]* 8.4 Write property test for error message privacy
    - **Property 16: Error Message Privacy**
    - Test that user-facing error messages never contain stack traces or internal details
    - **Validates: Requirements 10.9**

- [ ] 9. Checkpoint - End-to-end pipeline verification
  - Ensure all tests pass, ask the user if questions arise
  - Verify complete workflow: extension activation → extraction → Gemini formatting → backend inference → banner display
  - Test with sample phishing and legitimate emails
  - Confirm detection results displayed correctly in both Gmail and Outlook

- [ ] 10. Implement statistics tracking and storage
  - [ ] 10.1 Implement statistics update in background worker
    - Update chrome.storage.local stats (safe, threats counters) after each scan
    - Store recent scan results with timestamp in recentScans array
    - Update extension badge with threat count
    - _Requirements: 7.13_

  - [ ] 10.2 Implement popup statistics display
    - Update `frontend/popup.js` to retrieve and display stats from chrome.storage.local
    - Show total safe and threat counts in popup interface
    - _Requirements: 7.2_

  - [ ]* 10.3 Write integration tests for statistics tracking
    - Test that statistics increment correctly after scans
    - Test that badge updates reflect threat count
    - _Requirements: 7.2, 7.13_

- [ ] 11. Implement cross-browser compatibility
  - [ ] 11.1 Create browser API compatibility layer
    - Create `frontend/browser-compat.js` to normalize chrome.* and browser.* APIs
    - Normalize storage APIs (sync, local)
    - Normalize messaging APIs (sendMessage, sendTabMessage)
    - _Requirements: 2.7_

  - [ ] 11.2 Test manifest compatibility
    - Verify Manifest V3 format works in Chrome 88+
    - Verify Manifest V2 compatibility works in Firefox 78+
    - Test that extension loads and functions identically in both browsers
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 12. Final integration and end-to-end testing
  - [ ] 12.1 Wire all components together
    - Verify data flow from popup → content script → background worker → Gemini API → backend → content script
    - Ensure all message passing works correctly
    - Verify error handling at each layer
    - Confirm workflow completes within 10 seconds
    - _Requirements: 8.1, 8.2, 8.8, 8.9, 8.10_

  - [ ]* 12.2 Write integration tests for full pipeline
    - Test end-to-end workflow with mock email data
    - Test error scenarios: extraction failure, Gemini unavailability, backend offline
    - Test timeout handling for slow inferences
    - _Requirements: 8.1-8.10, 10.1-10.10_

- [ ] 13. Final checkpoint - Production readiness verification
  - Run all unit tests and property tests
  - Verify BERT model accuracy meets 85% threshold
  - Test extension in both Gmail and Outlook across Chrome and Firefox
  - Confirm all error handling works gracefully
  - Verify backend logs requests correctly
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation of the pipeline
- Property tests validate universal correctness properties from the design document
- Unit and integration tests validate specific examples and edge cases
- The implementation uses Python for backend (Flask + BERT) and JavaScript for frontend (browser extension)
- Phase 1 focuses exclusively on BERT content analysis; modules 2-5 are reserved for future phases

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3"] },
    { "id": 2, "tasks": ["1.4", "3.1"] },
    { "id": 3, "tasks": ["3.2", "5.1"] },
    { "id": 4, "tasks": ["3.3", "3.4", "5.2"] },
    { "id": 5, "tasks": ["3.5", "3.6", "5.3", "6.1"] },
    { "id": 6, "tasks": ["3.7", "5.4", "6.2", "6.3"] },
    { "id": 7, "tasks": ["6.4", "7.1"] },
    { "id": 8, "tasks": ["7.2", "7.3", "8.1"] },
    { "id": 9, "tasks": ["8.2", "8.3", "10.1"] },
    { "id": 10, "tasks": ["8.4", "10.2", "11.1"] },
    { "id": 11, "tasks": ["10.3", "11.2"] },
    { "id": 12, "tasks": ["12.1"] },
    { "id": 13, "tasks": ["12.2"] }
  ]
}
```
