# InboxIQ

**AI-Powered Email Workflow Automation**  
**Prepared by:** ColorsX74  
**Role:** IT Consultant & Senior Software Developer  
**Date:** November 2025  
**Location:** Abu Dhabi, UAE  

---

## Introduction

This application turns a messy inbox into a reliable, semi-automated workflow: it reads incoming emails, classifies them by department, generates a polite, context-aware reply, and forwards the conversation to the right team. It combines a simple desktop GUI (Tkinter), a FastAPI backend, and an AI pipeline (classification + response generation) to create a practical bridge between customer inquiries and internal handling.

---

## Architecture Overview

The application is built around three main layers — GUI, Backend API, and AI Pipeline — supported by training scripts and datasets. This modular design ensures clarity, scalability, and ease of maintenance.

### Architecture Diagram (Textual Representation)
```
+-------------------+ 
|   GUI (Tkinter)   | 
|  - gui.py         | 
|  - Admin Panel    | 
|  - Tester Panel   | 
+---------+---------+ 
          | 
          | REST API call (POST /process_email/) 
          v 
+-------------------+ 
| Backend (FastAPI) | 
|  - app.py         | 
|  - Endpoint       | 
+---------+---------+ 
          | 
          | Calls AI pipeline 
          v 
+-------------------+ 
|   AI Pipeline     | 
|  - ai_pipeline.py | 
|  - classify_email | 
|  - generate_reply | 
+---------+---------+ 
          | 
          | Uses models 
          v 
+-------------------+ 
|   Models          | 
|  - department_classifier (fine-tuned XLM-R) | 
|  - flan-t5-small (reply generation)         | 
+-------------------+
```

### Supporting Files

- `ai_model.py` (training script for classifier)
- `train.csv` / `test.csv` (datasets)
- `requirements.txt` (dependencies)
- `results/` (training outputs)

---

## Narrative Flow

### 1. GUI Layer (`gui.py`)
- Provides a **Tester Panel** for experimenting with sample emails.
- Provides an **Admin Panel** for configuring department emails, AI inbox credentials, and server settings.
- Handles inbox monitoring via IMAP and sends replies/forwards via SMTP.
- Communicates with the backend using REST API calls.

### 2. Backend Layer (`app.py`)
- Implements a FastAPI server with a single endpoint: `/process_email/`.
- Receives email text from the GUI.
- Calls the AI pipeline to classify and generate a reply.
- Returns JSON with department and reply.

### 3. AI Pipeline (`ai_pipeline.py`)
- Loads the fine‑tuned department classifier (`xlm-roberta-base`).
- Loads the reply generator (`flan-t5-small`).
- Provides two core functions:
  - `classify_email()` → determines department.
  - `generate_reply()` → produces a professional, client‑friendly response.
- Cleans and validates replies, with fallback logic for low‑quality outputs.

### 4. Models & Training
- `ai_model.py` trains the department classifier using `train.csv` and `test.csv`.
- Saves fine-tuned model to `./department_classifier`.
- Hugging Face cache stores `flan-t5-small` for reply generation.
- Training outputs and logs are stored in `results/`.

---

## Key Design Principles

- **Separation of Concerns:** GUI, backend, and AI pipeline are independent modules.
- **Extensibility:** Developers can swap models, adjust prompts, or integrate with CRMs/ERPs.
- **Reliability:** Fallback logic ensures professional replies even if AI output is low quality.
- **Security:** Uses Gmail App Passwords, TLS for SMTP, and isolated `.venv` for dependencies.

---

## Installation & Setup

### 1. Prerequisites
- **Python:** Version 3.9 or higher
- **Git:** For cloning and version control
- **Gmail Account:** With App Passwords enabled (required for IMAP/SMTP access)
- **Internet Access:** To download Hugging Face models (`xlm-roberta-base`, `flan-t5-small`)

### 2. Clone the Repository
```bash
git clone https://github.com/your-org/InboxIQ.git
cd InboxIQ
```
### 3. Create Virtual Environment
```
python -m venv .venv
```
Activate it
```
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```
### 4. Install Dependencies
```
pip install -r requirements.txt
```
This installs: 
- Machine Learning: torch, transformers, datasets, scikit-learn 
- Web Framework: fastapi, uvicorn 
- Tokenization Utilities: sentencepiece, protobuf, tiktoken 
- Email Handling: imaplib2, smtplib 
- Hugging Face Hub: huggingface_hub

### 5. Configure Gmail App Password
1. Enable 2-Step Verification in your Google account. 
2. Generate an App Password for “Mail”. 
3. Copy the 16-character password. 
4. Update gui.py → AI_PASSWORD with this value.
   
Note: Never use your real Gmail password. Always use an App Password.

### 6. Train Department Classifier (Optional) 
If you want to retrain the classifier:
```
python ai_model.py 
```
- Uses train.csv and test.csv datasets. 
- Saves fine-tuned model to ./department_classifier.
  
If already trained, skip this step — the app will load the existing model. 

### 7. Run FastAPI Backend 
``` 
uvicorn app:app --reload
```
- Starts the API at http://127.0.0.1:8000 
- Exposes /process_email/ endpoint

### 8. Launch GUI 
``` 
python gui.py
```
- Opens the Tkinter interface. 
- Tester Panel: Try sample emails. 
- Admin Panel: Configure department emails, AI inbox, and servers. 
- Use Check Inbox to process unread emails.

### 9. Verify Setup 
- Send a test email to the AI inbox with subject containing "test". 
- The GUI should classify, reply, and forward the message. 
- Status box will show: 
Processed 1 'test' email. 
### 10. Deployment Notes 
- For production, run FastAPI with a robust server (e.g., Gunicorn + Uvicorn workers). 
- Secure environment variables for credentials instead of hardcoding. 
- Consider Dockerizing for portability.
