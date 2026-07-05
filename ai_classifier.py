"""
ai_classifier.py
Sends the email content to Google Gemini (free tier) and gets back:
  - category (Pricing / Demo Request / Support / Spam / Other)
  - urgency (Low / Medium / High)
  - a suggested reply draft

Uses the official Google Gen AI Python SDK (google-genai).
Get a FREE API key at: https://aistudio.google.com/apikey  (no credit card needed)
"""

import json
from google import genai
import config

client = genai.Client(api_key=config.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are an assistant that triages business emails for a company called ScaleOn.
For every email you receive, respond ONLY with valid JSON (no markdown, no extra text) in this exact shape:

{
  "category": "Pricing" | "Demo Request" | "Support" | "Partnership" | "Spam" | "Other",
  "urgency": "Low" | "Medium" | "High",
  "summary": "one-line summary of what the sender wants",
  "suggested_reply": "a short, polite, professional reply draft (3-5 sentences) addressing the sender's request"
}

Keep the suggested_reply friendly, concise, and specific to what was asked. Do not invent facts,
prices, or promises you don't have information about — keep it general if unsure (e.g. 'our team will share pricing details shortly').
"""


def classify_email(subject: str, body: str, sender: str) -> dict:
    """Returns a dict with category, urgency, summary, suggested_reply."""

    user_prompt = f"""Sender: {sender}
Subject: {subject}
Body:
{body}
"""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
    )

    raw_text = response.text.strip()

    # Gemini sometimes wraps JSON in ```json ... ``` — strip that if present
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        # fallback so the pipeline never crashes on a bad response
        result = {
            "category": "Other",
            "urgency": "Low",
            "summary": "Could not parse AI response",
            "suggested_reply": "Thank you for your email. Our team will get back to you shortly.",
        }

    return result


if __name__ == "__main__":
    # quick manual test: python ai_classifier.py
    test = classify_email(
        subject="Pricing for your automation tool",
        body="Hi, can you tell me how much your AI automation service costs for a small team of 5?",
        sender="test@example.com",
    )
    print(json.dumps(test, indent=2))
