"""
email_reader.py
Connects to the mailbox via IMAP and fetches unread emails.
"""

import imaplib
import email
import re
from email.header import decode_header
from html.parser import HTMLParser

import config


def _decode(value):
    """Decode email header safely (handles non-ASCII subjects/names)."""
    if value is None:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


_STYLE_SCRIPT_RE = re.compile(
    r"<(style|script)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_HIDDEN_STYLE_RE = re.compile(r"display\s*:\s*none", re.IGNORECASE)
_ZERO_WIDTH_RE = re.compile("[\u034f\u200b\u200c\u200d\ufeff\u00ad]")


class _HTMLToText(HTMLParser):
    """Minimal HTML -> readable plain text converter (stdlib only, no bs4 needed).

    Assumes <style>/<script>/comments have already been stripped by regex
    (see _html_to_text) so it doesn't rely on those tags being well-formed
    or properly closed -- real marketing emails frequently leave <head>
    unclosed, which would otherwise get this parser stuck skipping content.
    """
    _BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2",
                   "h3", "h4", "h5", "h6", "table", "hr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._chunks = []
        self._hidden_stack = []  # tag names currently hiding their content

    def handle_starttag(self, tag, attrs):
        style = dict(attrs).get("style", "") or ""
        if self._hidden_stack or _HIDDEN_STYLE_RE.search(style):
            self._hidden_stack.append(tag)
            return
        if tag in self._BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_startendtag(self, tag, attrs):
        # self-closing tags like <br/> never hide content themselves
        if not self._hidden_stack and tag in self._BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_endtag(self, tag):
        if self._hidden_stack and self._hidden_stack[-1] == tag:
            self._hidden_stack.pop()
            return
        if not self._hidden_stack and tag in self._BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data):
        if not self._hidden_stack and data.strip():
            self._chunks.append(data.strip())

    def get_text(self):
        text = " ".join(self._chunks)
        text = _ZERO_WIDTH_RE.sub("", text)
        text = re.sub(r"\s*\n\s*", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def _html_to_text(html):
    cleaned = _COMMENT_RE.sub("", html)
    cleaned = _STYLE_SCRIPT_RE.sub("", cleaned)
    parser = _HTMLToText()
    try:
        parser.feed(cleaned)
        parser.close()
        text = parser.get_text()
        if text:
            return text
    except Exception:
        pass
    # last-resort fallback: strip all remaining tags with a blunt regex
    return re.sub(r"<[^>]+>", " ", cleaned).strip()


def _unflow(text):
    """Rejoin 'format=flowed' style soft-wrapped lines.

    Many mail senders (Google included) wrap plain-text lines and leave a
    trailing space to signal "this continues on the next line" (RFC 3676).
    Without unwrapping, words get split across lines like:
        Get
        started<https://...>
    This joins such lines back into normal paragraphs, while still
    preserving real paragraph breaks (blank lines) and quoted (">") lines.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    result = []
    buffer = ""
    for line in lines:
        is_blank = line.strip() == ""
        is_quote = line.startswith(">")
        is_sig_delim = line.rstrip("\n") == "-- "
        if (not is_blank) and (not is_quote) and (not is_sig_delim) and line.endswith(" "):
            buffer += line.rstrip(" ") + " "
        else:
            buffer += line
            result.append(buffer)
            buffer = ""
    if buffer:
        result.append(buffer)
    return "\n".join(result)


def _get_body(msg):
    """Extract a readable plain-text body from an email.message.Message object.

    Prefers a real text/plain part. If the email is HTML-only (no plain-text
    alternative), the HTML is converted to readable text instead of being
    dumped as raw markup.
    """
    plain_text = None
    html_text = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            if "attachment" in disposition:
                continue
            if content_type == "text/plain" and plain_text is None:
                charset = part.get_content_charset() or "utf-8"
                plain_text = part.get_payload(
                    decode=True).decode(charset, errors="ignore")
            elif content_type == "text/html" and html_text is None:
                charset = part.get_content_charset() or "utf-8"
                html_text = part.get_payload(
                    decode=True).decode(charset, errors="ignore")
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True).decode(charset, errors="ignore")
        if msg.get_content_type() == "text/html":
            html_text = payload
        else:
            plain_text = payload

    if plain_text and plain_text.strip():
        return _unflow(plain_text)
    if html_text:
        return _html_to_text(html_text)
    return ""


def fetch_unread_emails(limit=None):
    """
    Connects to the inbox and returns a list of dicts:
    [{ "id": ..., "from": ..., "subject": ..., "body": ... }, ...]
    Only UNSEEN (unread) emails are fetched.
    """
    limit = limit or config.MAX_EMAILS_PER_RUN

    imap = imaplib.IMAP4_SSL(config.IMAP_SERVER)
    imap.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    imap.select("INBOX")

    status, message_numbers = imap.search(None, "UNSEEN")
    if status != "OK":
        imap.logout()
        return []

    ids = message_numbers[0].split()
    ids = ids[-limit:]  # most recent N unread emails

    emails = []
    for msg_id in ids:
        status, msg_data = imap.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        emails.append({
            "id": msg_id.decode(),
            "from": _decode(msg.get("From")),
            "subject": _decode(msg.get("Subject")),
            "body": _get_body(msg).strip(),
        })

    imap.logout()
    return emails


if __name__ == "__main__":
    # quick manual test: python email_reader.py
    for e in fetch_unread_emails():
        print("-" * 40)
        print("From:", e["from"])
        print("Subject:", e["subject"])
        print("Body:", e["body"][:200])