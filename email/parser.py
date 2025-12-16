# email_ingest/parser.py

import base64
from models import EmailEvent
from datetime import datetime

def _get_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return None

def _extract_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                return base64.urlsafe_b64decode(
                    part["body"]["data"]
                ).decode("utf-8", errors="ignore")
    elif payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(
            payload["body"]["data"]
        ).decode("utf-8", errors="ignore")

    return ""

def parse_message_to_event(msg):
    payload = msg["payload"]
    headers = payload["headers"]

    # ✅ Gmail provides internalDate in milliseconds
    internal_date_ms = int(msg.get("internalDate", 0))
    timestamp = datetime.fromtimestamp(internal_date_ms / 1000)

    return EmailEvent(
        id=msg["id"],
        from_address=_get_header(headers, "From"),
        to_address=_get_header(headers, "To"),
        subject=_get_header(headers, "Subject"),
        body_text=_extract_body(payload),
        timestamp=timestamp,
        raw=msg
    )
