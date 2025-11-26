from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer as AutoTokenizerGen
import re

# --- Load routing model ---
clf_tok = AutoTokenizer.from_pretrained("./department_classifier", use_fast=False)
clf_model = AutoModelForSequenceClassification.from_pretrained("./department_classifier")

# --- Load response model ---
gen_name = "google/flan-t5-small"
gen_tok = AutoTokenizerGen.from_pretrained(gen_name, use_fast=False)
gen_model = AutoModelForSeq2SeqLM.from_pretrained(gen_name)

# --- Department mapping ---
DEPARTMENT_MAP = {
    0: "Sales",
    1: "Billing",
    2: "HR",
    3: "Support"
}

# --- Utility: sanitize and quality-check replies ---
FORBIDDEN_PHRASES = [
    r"\bi'?m sorry\b",
    r"\bsorry\b",
    r"\bi apologize\b",
    r"\bapologize\b",
]

def clean_reply(text: str) -> str:
    # Normalize whitespace
    reply = re.sub(r"\s+", " ", text).strip()

    # Remove overly repetitive segments (naive dedupe of 3+ repeats)
    reply = re.sub(r"(?:\b(\w+)\b(?:\s+|,|\.)*){3,}", lambda m: " ".join(dict.fromkeys(m.group(0).split())), reply)

    # Trim generic signatures or hallucinated meta
    reply = re.sub(r"(?:best regards|sincerely|assistant|ai model).*", "", reply, flags=re.IGNORECASE).strip()

    return reply

def is_low_quality(text: str) -> bool:
    if not text or len(text) < 12:
        return True
    lower = text.lower()
    if any(re.search(p, lower) for p in FORBIDDEN_PHRASES):
        return True
    # Excessive repetition heuristic
    if re.search(r"\b(\w+)\b(?:.*\1){4,}", lower):
        return True
    return False

# --- Core functions ---
def classify_email(email_text: str) -> str:
    inputs = clf_tok(email_text, return_tensors="pt", truncation=True, padding=True)
    outputs = clf_model(**inputs)
    predicted_class = outputs.logits.argmax(-1).item()
    return DEPARTMENT_MAP.get(predicted_class, "Support")

def generate_reply(email_text: str, department_name: str) -> str:
    """
    Generate a dynamic, concise, professional reply.
    - Avoid apologies or repetitive filler.
    - Provide a helpful next step.
    - If uncertain, defer gracefully to the relevant department.
    """
    department_guidance = {
        "Sales": "Focus on product details, availability, quotes, and next steps to collect order info.",
        "Billing": "Focus on invoices, payments, references, and steps to resolve billing questions.",
        "HR": "Focus on roles, applications, next steps, and how to proceed professionally.",
        "Support": "Focus on troubleshooting steps, clarity, and escalation if needed.",
    }.get(department_name, "Provide concise, helpful guidance and next steps.")

    prompt = (
        f"You are a {department_name} representative writing directly to a client.\n"
        f"Client message: \"{email_text}\"\n\n"
        "Compose a short, warm, and professional reply that\n"
        " Thanks them for reaching out,\n"
        " Mentions the {department_name} team will assist further,\n"
        " and Offers a clear next step or reassurance.\n"
        "Keep it under 1000 words, natural and friendly."
    )

    inputs = gen_tok(prompt, return_tensors="pt")
    outputs = gen_model.generate(
        **inputs,
        max_length=160,
        num_beams=4,
        no_repeat_ngram_size=3
    )
    raw = gen_tok.decode(outputs[0], skip_special_tokens=True)
    reply = clean_reply(raw)

    if is_low_quality(reply):
        # Graceful, dynamic fallback
        reply = (
            f"Thank you for reaching out. Based on your request, our {department_name} team "
            f"will assist you shortly. To move faster, please share any specific details "
            f"(e.g., quantities, references, timeline)."
        )

    return reply
