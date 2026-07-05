"""
config.py
Loads all secrets/settings from a .env file (local) or Streamlit Secrets
(when deployed on Streamlit Community Cloud) so nothing sensitive is hardcoded.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly point to the .env file next to this script, so it loads
# correctly no matter which folder you run the command from.
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


def _get(key, default=None):
    """
    Reads a setting from, in order:
      1. Streamlit secrets (st.secrets) -- used when deployed on Streamlit Cloud
      2. Environment variables / .env file -- used for local runs
    """
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass  # not running inside Streamlit, or no secrets.toml configured
    return os.getenv(key, default)


# ---- Email account (Gmail example) ----
EMAIL_ADDRESS = _get("EMAIL_ADDRESS")
EMAIL_PASSWORD = _get("EMAIL_PASSWORD")  # use a Gmail "App Password", not your real password

IMAP_SERVER = _get("IMAP_SERVER", "imap.gmail.com")
SMTP_SERVER = _get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(_get("SMTP_PORT", "587"))

# ---- Gemini API (free tier) ----
GEMINI_API_KEY = _get("GEMINI_API_KEY")
GEMINI_MODEL = _get("GEMINI_MODEL", "gemini-2.5-flash")  # fast + free-tier friendly

# ---- Behaviour settings ----
# "draft"  -> saves the AI reply to your Drafts folder (SAFE, recommended for demo)
# "send"   -> sends the reply immediately to the client (use with caution)
REPLY_MODE = _get("REPLY_MODE", "draft")

# How many unread emails to process in one run
MAX_EMAILS_PER_RUN = int(_get("MAX_EMAILS_PER_RUN", "10"))

CSV_LOG_PATH = _get("CSV_LOG_PATH", "email_log.csv")
