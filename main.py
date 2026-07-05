"""
main.py
The entry point. Run this file (or click "Run automation now" in the dashboard)
to process unread emails end-to-end:

  1. Fetch unread emails (email_reader.py)
  2. Classify + generate a suggested reply using Gemini (ai_classifier.py)
  3. Log everything to CSV (logger.py)

Note: this step does NOT create the Gmail draft automatically anymore.
The dashboard (app.py) is the single place that creates drafts — you review
the AI-suggested reply there and click "Save as Draft" yourself. This avoids
ending up with duplicate drafts for the same email.

Run:  python main.py
"""

import re

from email_reader import fetch_unread_emails
from ai_classifier import classify_email
from logger import log_email
import config


def extract_email_address(from_field: str) -> str:
    """Pulls the raw email address out of a 'Name <email@x.com>' string."""
    match = re.search(r"<(.+?)>", from_field)
    return match.group(1) if match else from_field


def run():
    print("Checking for unread emails...")
    emails = fetch_unread_emails()

    if not emails:
        print("No new emails found.")
        return

    print(f"Found {len(emails)} unread email(s). Processing...\n")

    for e in emails:
        sender_address = extract_email_address(e["from"])
        print(f"Processing email from {sender_address} | Subject: {e['subject']}")

        result = classify_email(
            subject=e["subject"],
            body=e["body"],
            sender=sender_address,
        )

        print(f"  -> Category: {result['category']} | Urgency: {result['urgency']}")
        print(f"  -> Summary: {result['summary']}")

        # Log to CSV (includes the AI-suggested reply, but does NOT send/draft it yet)
        log_email(
            sender=sender_address,
            subject=e["subject"],
            category=result["category"],
            urgency=result["urgency"],
            summary=result["summary"],
            reply_mode=config.REPLY_MODE,
            body=e["body"],
            suggested_reply=result["suggested_reply"],
        )
        print("  -> Logged. Review and save/send the reply from the dashboard.\n")

    print("Done. Open the dashboard (streamlit run app.py) to review and act on these emails.")


if __name__ == "__main__":
    run()