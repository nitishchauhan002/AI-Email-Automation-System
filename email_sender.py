"""
email_sender.py
Either SAVES the AI-generated reply as a Gmail draft (safe, recommended)
or SENDS it immediately via SMTP, depending on config.REPLY_MODE.
"""

import smtplib
import imaplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

import config


def _build_message(to_address, subject, body):
    msg = MIMEMultipart()
    msg["From"] = config.EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = f"Re: {subject}"
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(body, "plain"))
    return msg


def send_reply(to_address, subject, body):
    """Sends the reply immediately via SMTP."""
    msg = _build_message(to_address, subject, body)

    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_ADDRESS, to_address, msg.as_string())

    print(f"[SENT] Reply sent to {to_address}")


def save_as_draft(to_address, subject, body):
    """Saves the reply into the Gmail 'Drafts' folder instead of sending it."""
    msg = _build_message(to_address, subject, body)

    imap = imaplib.IMAP4_SSL(config.IMAP_SERVER)
    imap.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

    # "[Gmail]/Drafts" is the standard Gmail draft folder name
    imap.append(
        '"[Gmail]/Drafts"',
        "",
        imaplib.Time2Internaldate(time.time()),
        msg.as_bytes(),
    )
    imap.logout()

    print(f"[DRAFTED] Reply draft saved for {to_address}")


def handle_reply(to_address, subject, body):
    """Routes to send or draft based on config.REPLY_MODE."""
    if config.REPLY_MODE == "send":
        send_reply(to_address, subject, body)
    else:
        save_as_draft(to_address, subject, body)
