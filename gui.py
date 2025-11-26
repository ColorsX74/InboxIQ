import tkinter as tk
import requests
import imaplib, smtplib, email
from email.mime.text import MIMEText
from email.utils import parseaddr

# --- Global Config (defaults, can be overridden in GUI) ---
AI_EMAIL = "ai.tester.140@gmail.com"
AI_PASSWORD = "shlh etwh fcte vtmt"  # <-- your Gmail App Password here
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

department_emails = {
    "Sales": "",
    "Billing": "",
    "HR": "",
    "Support": ""
}

# --- Functions ---
def process_email():
    """Tester section: send text to FastAPI and display result."""
    email_text = text_input.get("1.0", tk.END).strip()
    response = requests.post("http://127.0.0.1:8000/process_email/", json={"email": email_text})
    data = response.json()
    if "department" in data and "reply" in data:
        result_label.config(text=f"Department: {data['department']}\nReply: {data['reply']}")
    else:
        result_label.config(text=f"Error: {data}")

def save_settings():
    """Admin section: save department + AI inbox + server settings from entry fields."""
    global AI_EMAIL, AI_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT
    department_emails["Sales"] = sales_entry.get()
    department_emails["Billing"] = billing_entry.get()
    department_emails["HR"] = hr_entry.get()
    department_emails["Support"] = support_entry.get()
    AI_EMAIL = ai_email_entry.get()
    AI_PASSWORD = ai_password_entry.get()
    IMAP_SERVER = imap_entry.get()
    SMTP_SERVER = smtp_entry.get()
    try:
        SMTP_PORT = int(smtp_port_entry.get())
    except ValueError:
        SMTP_PORT = 587
    set_status("Settings saved. Ready to check inbox.")

def check_inbox():
    """Admin section: fetch unread emails, classify, reply, and forward only if subject contains 'test'."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(AI_EMAIL, AI_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()

        processed_count = 0

        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            sender_name, sender_email = parseaddr(msg["From"])
            subject = msg["Subject"] or "(no subject)"
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            # ✅ Only process if subject contains 'test'
            if "test" not in subject.lower():
                continue

            # Classify via FastAPI
            response = requests.post("http://127.0.0.1:8000/process_email/", json={"email": body})
            data = response.json()
            department = data.get("department", "Support")
            reply_text = data.get("reply", "Thank you for your inquiry.")

            # Send reply to client
            smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            smtp.starttls()
            smtp.login(AI_EMAIL, AI_PASSWORD)

            reply_msg = MIMEText(reply_text, "plain", "utf-8")
            reply_msg["Subject"] = f"Re: {subject}"
            reply_msg["From"] = AI_EMAIL
            reply_msg["To"] = sender_email
            smtp.sendmail(AI_EMAIL, [sender_email], reply_msg.as_string())

            # Forward to department
            forward_body = (
                f"Client Email: {sender_email}\n"
                f"Subject: {subject}\n\n"
                f"Original inquiry:\n{body}\n\n"
                f"AI reply:\n{reply_text}"
            )

            forward_msg = MIMEText(forward_body, "plain", "utf-8")
            forward_msg["Subject"] = f"FWD: {subject}"
            forward_msg["From"] = AI_EMAIL
            forward_msg["To"] = department_emails.get(department, AI_EMAIL)

            smtp.sendmail(AI_EMAIL, [department_emails.get(department, AI_EMAIL)], forward_msg.as_string())

            smtp.quit()
            processed_count += 1

        mail.logout()
        set_status(f"Processed {processed_count} 'test' emails.")

    except Exception as e:
        set_status(f"Error: {e}")

# --- GUI Layout ---
root = tk.Tk()
root.title("Email Classifier & Admin Panel")

tester_frame = tk.LabelFrame(root, text="Tester", padx=10, pady=10)
admin_frame = tk.LabelFrame(root, text="Admin", padx=10, pady=10)

# Tester section
text_input = tk.Text(tester_frame, height=10, width=50)
text_input.pack()
submit_btn = tk.Button(tester_frame, text="Submit", command=process_email)
submit_btn.pack()
result_label = tk.Label(tester_frame, text="", justify="left")
result_label.pack()
tester_frame.pack(side="left", padx=20, pady=20)

# Admin section
tk.Label(admin_frame, text="Sales Email").pack()
sales_entry = tk.Entry(admin_frame); sales_entry.pack()
tk.Label(admin_frame, text="Billing Email").pack()
billing_entry = tk.Entry(admin_frame); billing_entry.pack()
tk.Label(admin_frame, text="HR Email").pack()
hr_entry = tk.Entry(admin_frame); hr_entry.pack()
tk.Label(admin_frame, text="Support Email").pack()
support_entry = tk.Entry(admin_frame); support_entry.pack()

tk.Label(admin_frame, text="AI Inbox Email").pack()
ai_email_entry = tk.Entry(admin_frame); ai_email_entry.insert(0, AI_EMAIL); ai_email_entry.pack()
tk.Label(admin_frame, text="AI Password").pack()
ai_password_entry = tk.Entry(admin_frame, show="*"); ai_password_entry.insert(0, AI_PASSWORD); ai_password_entry.pack()

tk.Label(admin_frame, text="IMAP Server").pack()
imap_entry = tk.Entry(admin_frame); imap_entry.insert(0, IMAP_SERVER); imap_entry.pack()
tk.Label(admin_frame, text="SMTP Server").pack()
smtp_entry = tk.Entry(admin_frame); smtp_entry.insert(0, SMTP_SERVER); smtp_entry.pack()
tk.Label(admin_frame, text="SMTP Port").pack()
smtp_port_entry = tk.Entry(admin_frame); smtp_port_entry.insert(0, str(SMTP_PORT)); smtp_port_entry.pack()

save_btn = tk.Button(admin_frame, text="Save Settings", command=save_settings)
save_btn.pack(pady=5)
check_btn = tk.Button(admin_frame, text="Check Inbox", command=check_inbox)
check_btn.pack(pady=5)

status_label = tk.Text(admin_frame, height=4, width=50, wrap="word")
status_label.config(state="disabled")  # start as read-only
status_label.pack()

def set_status(msg):
    status_label.config(state="normal")   # temporarily make editable
    status_label.delete("1.0", tk.END)    # clear old text
    status_label.insert(tk.END, msg)      # insert new message
    status_label.config(state="disabled") # back to read-only

admin_frame.pack(side="right", padx=20, pady=20)

root.mainloop()
