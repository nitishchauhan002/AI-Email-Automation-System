"""
fix_existing_log.py
One-time cleanup for rows already sitting in email_log.csv.

Re-runs the same HTML-stripping + soft-line-unwrapping used for new emails
against every existing row, so old rows (fetched before the fix) display
cleanly too. Safe to run multiple times.

Usage:
    python fix_existing_log.py
"""

import csv
import shutil

import config
from email_reader import _unflow, _html_to_text

LOOKS_LIKE_HTML = ("<html", "<div", "<table", "<span", "<style", "<!DOCTYPE", "<br")


def clean_body(body: str) -> str:
    if any(marker in body for marker in LOOKS_LIKE_HTML):
        return _html_to_text(body)
    return _unflow(body)


def main():
    backup_path = config.CSV_LOG_PATH + ".bak"
    shutil.copy(config.CSV_LOG_PATH, backup_path)
    print(f"Backup saved to {backup_path}")

    with open(config.CSV_LOG_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    changed = 0
    for row in rows:
        original = row.get("body", "")
        cleaned = clean_body(original)
        if cleaned != original:
            row["body"] = cleaned
            changed += 1

    with open(config.CSV_LOG_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Cleaned {changed} of {len(rows)} row(s).")


if __name__ == "__main__":
    main()