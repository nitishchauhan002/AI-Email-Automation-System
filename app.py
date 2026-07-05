"""
app.py
Gmail-styled dashboard for the AI Email Automation project.

Run locally:   streamlit run app.py
Deploy free:   push to GitHub -> https://share.streamlit.io -> deploy this file
"""

import os

import pandas as pd
import streamlit as st
import plotly.express as px

import config
from main import run as run_automation
from email_sender import handle_reply
from logger import delete_email

st.set_page_config(page_title="Chauhan Mail", page_icon="📧", layout="wide")

# ---------------------------------------------------------------------------
# Gmail-inspired styling
# ---------------------------------------------------------------------------
GMAIL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Roboto', 'Google Sans', Arial, sans-serif;
}

#MainMenu, footer, header {visibility: hidden;}

.st-key-topbar button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #5f6368 !important;
    font-size: 18px !important;
    padding: 4px 8px !important;
    white-space: nowrap !important;
    width: auto !important;
}
.st-key-topbar button:hover {
    background: #f1f3f4 !important;
    border-radius: 50% !important;
}
.st-key-topbar div[data-testid="stPopover"] {
    width: auto !important;
}

.gmail-logo {
    font-size: 22px;
    font-weight: 500;
    color: #5f6368;
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
    padding-top: 6px;
}
.gmail-logo span.mail-icon { color: #ea4335; font-size: 26px; }

.gmail-avatar-round {
    width: 32px; height: 32px; border-radius: 50%;
    background: #d93025; color: white; font-weight: 700;
    display: flex; align-items: center; justify-content: center; font-size: 14px;
    margin-top: 2px;
}

div[data-testid="stTextInput"] input {
    background: #eaf1fb !important;
    color: #202124 !important;
    border-radius: 24px !important;
    border: 1px solid transparent !important;
    padding: 10px 18px !important;
    font-size: 14px !important;
    caret-color: #202124 !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #5f6368 !important;
    opacity: 1 !important;
}
div[data-testid="stTextInput"] input:focus {
    background: #ffffff !important;
    color: #202124 !important;
    border: 1px solid #1a73e8 !important;
    box-shadow: 0 1px 6px rgba(32,33,36,0.28);
}

div[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: #c2e7ff !important;
    color: #001d35 !important;
    border-radius: 16px !important;
    border: none !important;
    font-weight: 500 !important;
    padding: 12px 18px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
div[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: #a8dcff !important;
}

div[data-testid="stSidebar"] .stRadio > label { display: none; }
div[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
    padding: 8px 14px;
    border-radius: 0 20px 20px 0;
    margin-bottom: 2px;
    font-size: 14px;
    color: #202124;
}
div[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) {
    background-color: #d3e3fd;
    font-weight: 700;
    color: #001d35;
}

.st-key-inbox_rows button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 16px !important;
    padding: 2px 6px !important;
}
.st-key-inbox_rows button:hover {
    background: #f1f3f4 !important;
    border-radius: 50% !important;
}

.avatar {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 13px; flex-shrink: 0;
    margin-top: 4px;
}
.sender { font-weight: 400; color: #202124; font-size: 14px; width: 170px; flex-shrink: 0; }
.subject-snippet { font-size: 14px; color: #5f6368; flex-grow: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.subject-text { color: #202124; font-weight: 500; }
.timestamp { font-size: 12px; color: #5f6368; text-align: right; padding-top: 6px; }

.chip {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 700; margin-right: 6px; white-space: nowrap;
}
.chip-pricing { background: #e8f0fe; color: #1967d2; }
.chip-demo { background: #e6f4ea; color: #188038; }
.chip-support { background: #fef7e0; color: #f29900; }
.chip-partnership { background: #f3e8fd; color: #9334e6; }
.chip-spam { background: #fce8e6; color: #c5221f; }
.chip-other { background: #f1f3f4; color: #5f6368; }

.urgency-dot { height: 9px; width: 9px; border-radius: 50%; display: inline-block; margin-right: 4px; }
.urgency-High { background: #ea4335; }
.urgency-Medium { background: #fbbc04; }
.urgency-Low { background: #34a853; }

.no-results { text-align: center; padding: 60px 20px; color: #5f6368; }
hr.divider { border: none; border-top: 1px solid #e0e0e0; margin: 6px 0 14px 0; }
</style>
"""
st.markdown(GMAIL_CSS, unsafe_allow_html=True)

CATEGORY_CHIP = {
    "Pricing": "chip-pricing",
    "Demo Request": "chip-demo",
    "Support": "chip-support",
    "Partnership": "chip-partnership",
    "Spam": "chip-spam",
    "Other": "chip-other",
}
AVATAR_COLORS = ["#1a73e8", "#188038",
                 "#e37400", "#9334e6", "#d01884", "#12805c"]


def avatar_color(name: str) -> str:
    return AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]


def initials(name: str) -> str:
    clean = name.split("<")[0].strip().strip('"')
    parts = [p for p in clean.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[1][0]).upper()


if "starred" not in st.session_state:
    st.session_state.starred = set()
if "drafted" not in st.session_state:
    st.session_state.drafted = set()
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

if not st.session_state.sidebar_open:
    st.markdown(
        "<style>section[data-testid='stSidebar']{display:none;}</style>",
        unsafe_allow_html=True,
    )

with st.container(key="topbar"):
    c_burger, c_logo, c_search, c_help, c_settings, c_apps, c_avatar = st.columns(
        [0.5, 2.2, 4.0, 0.8, 0.5, 0.5, 0.6]
    )

    with c_burger:
        if st.button("☰", key="hamburger_btn", help="Toggle sidebar"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.rerun()

    with c_logo:
        st.markdown(
            '<div class="gmail-logo"><span class="mail-icon">📧</span> Chauhan Mail</div>',
            unsafe_allow_html=True,
        )

    with c_search:
        search_query = st.text_input(
            "search", placeholder="Search mail", label_visibility="collapsed", key="search_box"
        )

    with c_help:
        with st.popover("Help"):
            st.markdown("**Help**")
            st.write("This is an AI email automation dashboard. Click any email to view the "
                     "AI-suggested reply, edit it, and save it as a Gmail draft.")

    with c_settings:
        with st.popover("⚙️"):
            st.markdown("**Settings**")
            st.write(f"AI model: `{config.GEMINI_MODEL}`")
            st.write(f"Reply mode: `{config.REPLY_MODE}`")
            st.caption("Change these in your `.env` file.")

    with c_apps:
        with st.popover("▦"):
            st.markdown("**Quick links**")
            st.write("📥 Inbox")
            st.write("⭐ Starred")
            st.write("📊 Analytics")

    with c_avatar:
        st.markdown('<div class="gmail-avatar-round">C</div>',
                    unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

if os.path.isfile(config.CSV_LOG_PATH):
    df = pd.read_csv(config.CSV_LOG_PATH).fillna("")
    if "id" not in df.columns:
        df["id"] = df.index.astype(str)
else:
    df = pd.DataFrame(columns=["id", "timestamp", "from", "subject", "category",
                               "urgency", "summary", "body", "suggested_reply", "reply_mode"])

with st.sidebar:
    if st.button("✏️  Compose  ·  Run automation now", use_container_width=True):
        with st.spinner("Checking inbox and processing unread emails..."):
            try:
                run_automation()
                st.success("Done — new emails processed!")
                st.rerun()
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.write("")
    total = len(df)
    high = int((df["urgency"] == "High").sum()) if total else 0
    spam = int((df["category"] == "Spam").sum()) if total else 0
    starred_count = len(st.session_state.starred)

    nav = st.radio(
        "nav",
        [f"📥  Inbox ({total})",
         f"⭐  Starred ({starred_count})",
         f"🔴  High Priority ({high})",
         f"🚫  Spam ({spam})",
         "📊  Analytics"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(f"AI model: `{config.GEMINI_MODEL}`")
    st.caption(f"Reply mode: `{config.REPLY_MODE}`")

if df.empty:
    st.info(
        "📭 **Inbox empty.** Click **Compose · Run automation now** in the sidebar to fetch "
        "and classify unread emails, or run `python main.py` once to generate data."
    )
    st.stop()

if "Analytics" in nav:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Emails", total)
    c2.metric("High Urgency", high)
    c3.metric("Categories", df["category"].nunique())
    c4.metric("Spam Filtered", spam)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Emails by Category")
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        st.plotly_chart(px.pie(cat_counts, names="category", values="count", hole=0.45,
                               color_discrete_sequence=px.colors.qualitative.Set2),
                        use_container_width=True)
    with col2:
        st.subheader("Emails by Urgency")
        urg_counts = df["urgency"].value_counts().reset_index()
        urg_counts.columns = ["urgency", "count"]
        st.plotly_chart(px.bar(urg_counts, x="urgency", y="count", color="urgency",
                               color_discrete_map={"High": "#ea4335", "Medium": "#fbbc04", "Low": "#34a853"}),
                        use_container_width=True)
    st.stop()

view_df = df.copy()
if "Starred" in nav:
    view_df = view_df[view_df["id"].isin(st.session_state.starred)]
elif "High Priority" in nav:
    view_df = view_df[view_df["urgency"] == "High"]
elif "Spam" in nav:
    view_df = view_df[view_df["category"] == "Spam"]

if search_query.strip():
    q = search_query.strip().lower()
    mask = (
        view_df["from"].str.lower().str.contains(q, na=False)
        | view_df["subject"].str.lower().str.contains(q, na=False)
        | view_df["summary"].str.lower().str.contains(q, na=False)
        | view_df["body"].str.lower().str.contains(q, na=False)
        | view_df["category"].str.lower().str.contains(q, na=False)
    )
    view_df = view_df[mask]

view_df = view_df.sort_values("timestamp", ascending=False)

st.write("")

if search_query.strip():
    st.caption(
        f"Search results for \u201c{search_query}\u201d — {len(view_df)} email(s) found")

if view_df.empty:
    st.markdown(
        '<div class="no-results">🔍<br><b>No matching emails</b><br>Try a different search term.</div>',
        unsafe_allow_html=True,
    )
else:
    with st.container(key="inbox_rows"):
        for _, row in view_df.iterrows():
            row_id = row["id"]
            sender_name = row["from"].split(
                "<")[0].strip().strip('"') or row["from"]
            chip_class = CATEGORY_CHIP.get(row["category"], "chip-other")
            is_starred = row_id in st.session_state.starred
            star_icon = "★" if is_starred else "☆"

            cols = st.columns([0.4, 0.8, 0.6, 5.1, 1.0, 0.4])

            with cols[0]:
                if st.button(star_icon, key=f"star_{row_id}", help="Star"):
                    if is_starred:
                        st.session_state.starred.discard(row_id)
                    else:
                        st.session_state.starred.add(row_id)
                    st.rerun()

            with cols[1]:
                if st.button("Delete", key=f"del_{row_id}", help="Delete this email"):
                    delete_email(row_id)
                    st.session_state.starred.discard(row_id)
                    st.session_state.drafted.discard(row_id)
                    st.toast("Email deleted.")
                    st.rerun()

            with cols[2]:
                st.markdown(
                    f'<div class="avatar" style="background:{avatar_color(sender_name)}">{initials(sender_name)}</div>',
                    unsafe_allow_html=True,
                )

            with cols[3]:
                st.markdown(
                    f"""<div style="display:flex;align-items:center;gap:10px;padding-top:6px;">
                        <span class="sender">{sender_name}</span>
                        <span class="subject-snippet">
                            <span class="chip {chip_class}">{row['category']}</span>
                            <span class="urgency-dot urgency-{row['urgency']}"></span>
                            <span class="subject-text">{row['subject']}</span> — {row['summary']}
                        </span>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with cols[4]:
                st.markdown(
                    f'<div class="timestamp">{row["timestamp"]}</div>', unsafe_allow_html=True)

            with cols[5]:
                already_drafted = row_id in st.session_state.drafted
                st.markdown(
                    f'<div class="timestamp">{"✅ drafted" if already_drafted else ""}</div>',
                    unsafe_allow_html=True,
                )

            with st.expander("View email & AI reply"):
                left, right = st.columns(2)
                with left:
                    st.markdown("**Original message**")
                    st.text_area("body", value=row["body"], height=160,
                                 key=f"body_{row_id}", disabled=True, label_visibility="collapsed")
                with right:
                    st.markdown("**AI-suggested reply** ✨")
                    edited_reply = st.text_area("reply", value=row["suggested_reply"], height=160,
                                                key=f"reply_{row_id}", label_visibility="collapsed")

                b1, b2 = st.columns([1, 1])
                with b1:
                    already_drafted = row_id in st.session_state.drafted
                    btn_label = "✅ Draft Saved" if already_drafted else "💾 Save as Draft"
                    if st.button(btn_label, key=f"draft_{row_id}", use_container_width=True,
                                 disabled=already_drafted):
                        try:
                            to_addr = row["from"]
                            if "<" in to_addr:
                                to_addr = to_addr.split(
                                    "<")[1].replace(">", "").strip()
                            handle_reply(to_addr, row["subject"], edited_reply)
                            st.session_state.drafted.add(row_id)
                            st.success("Saved to Gmail Drafts.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not save draft: {e}")
                with b2:
                    st.caption(
                        f"Logged at {row['timestamp']} · reply mode: `{row['reply_mode']}`")

            st.markdown('<hr class="divider">', unsafe_allow_html=True)