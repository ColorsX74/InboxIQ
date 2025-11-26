InboxIQ 
AI-Powered Email Workflow 
Automation 
Prepared by: ColorsX74 
Role: IT Consultant & Senior Software Developer 
Date: November 2025 
Location: Abu Dhabi, UAE
==========================================================================

Introduction 
This application turns a messy inbox into a reliable, semi-automated workflow: it reads 
incoming emails, classifies them by department, generates a polite, context-aware reply, 
and forwards the conversation to the right team. It combines a simple desktop GUI 
(Tkinter), a FastAPI backend, and an AI pipeline (classification + response generation) to 
create a practical bridge between customer inquiries and internal handling.
==========================================================================

Architecture Overview 
    The application is built around three main layers — GUI, Backend API, and AI Pipeline — 
    supported by training scripts and datasets. This modular design ensures clarity, scalability, 
    and ease of maintenance. 

Architecture Diagram (Textual Representation) 
Code 
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
Supporting Files: - ai_model.py (training script for classifier) - train.csv / test.csv (datasets) - requirements.txt (dependencies) - results/ (training outputs) 

Narrative Flow 
    1. GUI Layer (gui.py) 
        a. Provides a Tester Panel for experimenting with sample emails. 
        b. Provides an Admin Panel for configuring department emails, AI inbox 
        credentials, and server settings. 
        c. Handles inbox monitoring via IMAP and sends replies/forwards via SMTP. 
        d. Communicates with the backend using REST API calls. 
    2. Backend Layer (app.py) 
        a. Implements a FastAPI server with a single endpoint: /process_email/. 
        b. Receives email text from the GUI. 
        c. Calls the AI pipeline to classify and generate a reply. 
        d. Returns JSON with department and reply. 
    3. AI Pipeline (ai_pipeline.py) 
        a. Loads the fine‑tuned department classifier (xlm-roberta-base). 
        b. Loads the reply generator (flan-t5-small). 
        c. Provides two core functions: 
            i. classify_email() → determines department. 
            ii. generate_reply() → produces a professional, client‑friendly 
            response. 
        d. Cleans and validates replies, with fallback logic for low‑quality outputs. 
    4. Models & Training 
        a. ai_model.py trains the department classifier using train.csv and 
        test.csv. 
        b. Saves fine‑tuned model to ./department_classifier. 
        c. Hugging Face cache stores flan-t5-small for reply generation. 
        d. Training outputs and logs are stored in results/.   

Key Design Principles 
    • Separation of Concerns: GUI, backend, and AI pipeline are independent modules. 
    • Extensibility: Developers can swap models, adjust prompts, or integrate with 
    CRMs/ERPs. 
    • Reliability: Fallback logic ensures professional replies even if AI output is low 
    quality. 
    • Security: Uses Gmail App Passwords, TLS for SMTP, and isolated .venv for 
    dependencies. 
==========================================================================

Installation & Setup 
1. Prerequisites 
    • Python: Version 3.9 or higher 
    • Git: For cloning and version control 
    • Gmail Account: With App Passwords enabled (required for IMAP/SMTP access) 
    • Internet Access: To download Hugging Face models (xlm-roberta-base, flan
    t5-small)
2. Clone the Repository 
    bash 
    git clone https://github.com/your-org/InboxIQ.git 
    cd InboxIQ 
3. Create Virtual Environment 
    bash 
    python -m venv .venv 
    Activate it: 
    bash 
    # Linux/macOS 
    source .venv/bin/activate 
    # Windows 
    .venv\Scripts\activate 
4. Install Dependencies 
    bash 
    pip install -r requirements.txt 
    This installs: 
        • Machine Learning: torch, transformers, datasets, scikit-learn 
        • Web Framework: fastapi, uvicorn 
        • Tokenization Utilities: sentencepiece, protobuf, tiktoken 
        • Email Handling: imaplib2, smtplib 
        • Hugging Face Hub: huggingface_hub 
5. Configure Gmail App Password 
    1. Enable 2-Step Verification in your Google account. 
    2. Generate an App Password for “Mail”. 
    3. Copy the 16-character password. 
    4. Update gui.py → AI_PASSWORD with this value. 
    Note: Never use your real Gmail password. Always use an App Password. 
6. Train Department Classifier (Optional) 
    If you want to retrain the classifier: 
    bash 
    python ai_model.py 
    • Uses train.csv and test.csv datasets. 
    • Saves fine-tuned model to ./department_classifier. 
    If already trained, skip this step — the app will load the existing model. 
7. Run FastAPI Backend 
    bash 
    uvicorn app:app --reload 
    • Starts the API at http://127.0.0.1:8000 
    • Exposes /process_email/ endpoint 
8. Launch GUI 
    bash 
    python gui.py 
    • Opens the Tkinter interface. 
    • Tester Panel: Try sample emails. 
    • Admin Panel: Configure department emails, AI inbox, and servers. 
    • Use Check Inbox to process unread emails. 
9. Verify Setup 
    • Send a test email to the AI inbox with subject containing "test". 
    • The GUI should classify, reply, and forward the message. 
    • Status box will show: 
    Processed 1 'test' email. 
10. Deployment Notes 
    • For production, run FastAPI with a robust server (e.g., Gunicorn + Uvicorn workers). 
    • Secure environment variables for credentials instead of hardcoding. 
    • Consider Dockerizing for portability. 
==========================================================================


Usage Guide 
The application provides two main modes of operation: Tester Mode (for experimenting 
with sample emails) and Admin Mode (for real inbox monitoring, replies, and forwarding). 
Both are accessible through the Tkinter GUI. 
1. Launching the Application 
    • Ensure the FastAPI backend is running: 
    bash 
    uvicorn app:app --reload 
    • Start the GUI: 
    bash 
    python gui.py 
    • The interface opens with two panels: 
        o Tester Panel (left) 
        o Admin Panel (right) 
2. Tester Panel 
    This mode is designed for quick experiments and demonstrations. 
    • Text Input Box: Enter any sample email text. 
    • Submit Button: Sends the text to the FastAPI backend (/process_email/). 
    • Result Display: Shows: 
        o Department classification (Sales, Billing, HR, Support) 
        o AI-generated reply 
    Example: 
    Input: "I need help with my invoice." 
    Output: 
    Department: Billing 
    Reply: Thank you for reaching out. Our Billing team will assist 
    you shortly with your invoice. 
3. Admin Panel 
    This mode is for configuring and running the real email workflow. 
    Configuration 
    • Department Emails: Enter forwarding addresses for Sales, Billing, HR, and 
    Support. 
    • AI Inbox Email: Enter the Gmail address used by the AI. 
    • AI Password: Enter the Gmail App Password (not the real password). 
    • IMAP/SMTP Settings: Configure mail servers (imap.gmail.com, 
    smtp.gmail.com) and port (587). 
    • Save Settings Button: Saves all configuration values. 
    Inbox Monitoring 
    • Check Inbox Button: 
        o Connects to the AI inbox via IMAP. 
        o Fetches unread emails. 
        o Filters only those with "test" in the subject. 
        o Sends email body to FastAPI for classification and reply. 
        o Replies to the client via SMTP. 
        o Forwards the inquiry + AI reply to the relevant department. 
        o Updates the status box with results. 
    Example Status: 
    Processed 3 'test' emails. 
4. Workflow Summary 
    1. Client sends an email to the AI inbox. 
    2. Admin clicks Check Inbox. 
    3. Email is classified by department. 
    4. AI generates a reply. 
    5. Reply is sent back to the client. 
    6. Email + AI reply are forwarded to the department team. 
    7. Status updates show progress or errors. 
5. Best Practices 
    • Always use Gmail App Passwords for security. 
    • Test with subjects containing "test" before enabling full automation. 
    • Regularly update department email addresses in the Admin Panel. 
    • Monitor the status box for errors (e.g., authentication issues, SMTP failures). 
