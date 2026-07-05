"""
logger.py
Logs every processed email + AI result into a CSV file so you have
a simple "mini CRM" record you can open in Excel/Sheets, or in the dashboard.

Each row gets a short unique `id` so the dashboard can reliably
reference / delete a specific row (instead of relying on row position,
which shifts whenever a row is deleted).
"""

import csv
import os
import uuid
from datetime import datetime

import config

FIELDNAMES = ["id", "timestamp", "from", "subject", "category", "urgency", "summary",
              "body", "suggested_reply", "reply_mode"]


def log_email(sender, subject, category, urgency, summary, reply_mode, body="", suggested_reply=""):
    """Appends one row to the CSV log. Returns the generated id."""
    file_exists = os.path.isfile(config.CSV_LOG_PATH)
    row_id = uuid.uuid4().hex[:8]

    with open(config.CSV_LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "id": row_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": sender,
            "subject": subject,
            "category": category,
            "urgency": urgency,
            "summary": summary,
            "body": body,
            "suggested_reply": suggested_reply,
            "reply_mode": reply_mode,
        })

    return row_id


def delete_email(row_id: str):
    """Removes a single row (by id) from the CSV log, like moving an email to Trash."""
    if not os.path.isfile(config.CSV_LOG_PATH):
        return

    with open(config.CSV_LOG_PATH, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = [row for row in reader if row.get("id") != row_id]

    with open(config.CSV_LOG_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)