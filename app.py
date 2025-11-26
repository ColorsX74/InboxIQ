from fastapi import FastAPI
from pydantic import BaseModel
from ai_pipeline import classify_email, generate_reply

app = FastAPI()

class EmailRequest(BaseModel):
    email: str

@app.post("/process_email/")
def process_email(request: EmailRequest):
    email_text = request.email.strip()
    department = classify_email(email_text)
    reply = generate_reply(email_text, department)
    return {"department": department, "reply": reply}
