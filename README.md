<div align="center">

# 📧 AI Email Automation System

### ScaleOn Internship Program 2026 — Assignment 01 (AI Agent Developer Track)
**Option Selected: AI Automation Challenge → Email Automation**

An AI-powered agent that reads your Gmail inbox, classifies every email (category, priority, intent, sentiment), drafts a context-aware reply using Google Gemini, and lets you review, edit, save-as-draft, or send it — all from a Gmail-styled dashboard.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Google_Gemini-AI_Engine-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)]()

[🎥 Demo Video](https://colab.research.google.com/drive/1BaZlow1SPpu4tUo1LoeL7LycyDhh5tR8?usp=sharing) · [🐛 Report Bug](https://github.com/nitishchauhan002/AI-Email-Automation-System/issues) · [💡 Request Feature](https://github.com/nitishchauhan002/AI-Email-Automation-System/issues)

</div>

---

## 📌 Problem Statement

Businesses receive a constant stream of repetitive inbound emails — pricing questions, demo requests, support tickets, HR queries, promotional spam — and manually reading, categorizing, and replying to each one wastes hours every week.

This project automates that entire first-response workflow using AI, so a human only needs to **review and approve** rather than read-and-write everything from scratch.

## ✨ Features

| Feature | Description |
|---|---|
| 📥 **Full Inbox Fetch** | Pulls **every email** in the inbox (read + unread), not just unread ones |
| ⚡ **Unread-Only Mode** | Faster option to just check new mail |
| 🧠 **AI Classification** | Category (Sales / Support / HR / Finance / Marketing / Meeting / Orders / Spam), Priority, Intent, Sentiment |
| ✍️ **AI-Drafted Replies** | Gemini writes a professional reply tailored to each email's intent |
| 📤 **Send Reply** | Edit the AI draft and send it for real, directly from the dashboard |
| 💾 **Save as Draft** | Push the reply into your real Gmail Drafts folder instead of sending |
| 🔍 **Live Search** | Filter by sender, subject, intent, category, or body content |
| ⭐ **Star / 🗑️ Delete** | Organize and clean up processed emails |
| 📊 **Analytics Dashboard** | Category breakdown, priority distribution, spam-filtered count |
| 🚫 **Duplicate-safe** | Tracks `message_id` so re-running never reprocesses the same email twice |
| 🎨 **Gmail-style UI** | Familiar inbox layout — avatars, labels, priority dots, hamburger menu |

## 🖼️ Screenshots

> _Replace these placeholders with your own screenshots — drop the image files into a `screenshots/` folder in the repo and update the paths below._

| Inbox View | AI Reply + Draft/Send | Analytics |
|---|---|---|
| ![Inbox](screenshots/inbox.png) | ![Reply](screenshots/reply.png) | ![Analytics](screenshots/analytics.png) |

## 🧭 How It Works

```mermaid
flowchart TD
    A[📬 Gmail Inbox] -->|IMAP fetch: unread or ALL mail| B[email_reader.py]
    B --> C{Already processed?<br/>check message_id}
    C -->|Yes, skip| Z[Done]
    C -->|No, new email| D[ai_classifier.py<br/>Google Gemini]
    D --> E[Category · Priority<br/>Intent · Sentiment<br/>Suggested Action · Draft Reply]
    E --> F[(logger.py<br/>email_log.csv)]
    F --> G[app.py — Streamlit Dashboard]
    G --> H{User reviews<br/>AI reply}
    H -->|Edit + Save as Draft| I[email_sender.py<br/>IMAP → Gmail Drafts folder]
    H -->|Edit + Send| J[email_sender.py<br/>SMTP → Sent for real]
    H -->|Star / Delete| K[Update CSV log]
```

## 🏗️ Tech Stack

- **Frontend/Dashboard:** Streamlit + Plotly (Gmail-inspired custom CSS)
- **AI Engine:** Google Gemini API (`gemini-2.5-flash`, free tier — no card required)
- **Email Protocols:** IMAP (fetch + draft) / SMTP (send) via Python's `imaplib` / `smtplib`
- **Storage:** CSV-based lightweight log (`email_log.csv`) — easy to inspect in Excel/Sheets
- **Language:** Python 3.10+

## 📂 Project Structure